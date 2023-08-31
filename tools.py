import pygame
import sys
import math
import os
import ctypes
# pygame.init()
# display_info = pygame.display.Info()
# pw=lambda x:display_info.current_w*x
# ph=lambda x:display_info.current_h*x

# 按屏幕分辨率百分比获取像素值
user32 = ctypes.windll.user32
screen_x,screen_y = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
pw=lambda x:screen_x*x
ph=lambda y:screen_y*y

# 获取绝对路径，防止pyinstaller打包后找不到文件
def abs_path(file_path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), file_path))

# 重写了退出函数
def q_exit():
    pygame.quit()
    sys.exit()

# 斜率转角度
def k_to_deg(k):
    ret = math.atan(k)*180/math.pi
    if ret<0:
        ret+=180
    return ret

# 按比例缩放
def scale(s,p,i):
    x,y=p
    w,h=s
    center_x = x + w / 2
    center_y = y + h / 2
    return (w*i,h*i),(center_x-w*i/2,center_y-h*i/2)

# 获取点与直线之间的距离
def get_distance(p_a,p_b,p_c):
    d2_ab=(p_a[0]-p_b[0])**2+(p_a[1]-p_b[1])**2
    d2_ac = (p_a[0] - p_c[0]) ** 2 + (p_a[1] - p_c[1]) ** 2
    d2_bc = (p_b[0] - p_c[0]) ** 2 + (p_b[1] - p_c[1]) ** 2
    if d2_ac>d2_ab+d2_bc:
        return d2_bc**0.5
    if d2_bc>d2_ab+d2_ac:
        return d2_ac**0.5
    try:
        m = (p_b[1] - p_a[1]) / (p_b[0] - p_a[0])
        c = p_a[1] - m * p_a[0]
        return abs((-m) * p_c[0] + p_c[1] + (-c)) / math.sqrt((-m) ** 2 + 1)
    except ZeroDivisionError:
        return 100000000

# 碰撞判定
def get_hit_k(rect, orbit):
    if len(orbit.orbit)<2:
        return None
    x0, y0 = orbit.orbit[-2][1]
    x1, y1 = orbit.orbit[-1][1]
    distance=get_distance([x0, y0],[x1, y1],[rect[0]+rect[2]*0.5,rect[1]+rect[3]*0.5])
    if distance> 0.45*max([rect[2],rect[3]]):
        return None
    if x1==x0:
        return 100000
    k = 0-(y1 - y0) / (x1 - x0)
    return k

def load_image():
    ret={}
    for path,_dir,files in os.walk(abs_path('./assets/images')):
        for file in files:
            ret[file.split('.')[0]]=pygame.image.load(path+'/'+file)
    return ret

# 分数控制类
class Score:
    def __init__(self):
        self.score=0
        self.text_surface=None
        self.refresh_text_surface()

    def add(self):
        self.score+=1
        self.refresh_text_surface()

    def refresh_text_surface(self):
        fonts = pygame.font.get_fonts()[5]
        font = pygame.font.SysFont(fonts, int(ph(0.0625)))
        text = f'{self.score}'
        font.bold = False
        self.text_surface=font.render(text, False, (210, 113, 20))

# 音乐控制类
class Music:
    def __init__(self):
        self.sounds = {}
        for path, _dir, files in os.walk(abs_path('./assets/sound')):
            for file in files:
                self.sounds[file.split('.')[0]] = pygame.mixer.Sound(path + '/' + file)

    def __getitem__(self, item):
        return self.sounds.get(item)

    def play(self,name,volume=0.3):
        music=self.sounds[name]
        music.set_volume(volume)
        music.play()

    def menu(self):
        pygame.mixer.music.load(abs_path("./assets/sound/menu.mp3"))
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(loops=1000000)

    def game(self):
        pygame.mixer.music.load(abs_path("./assets/sound/background.ogg"))
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(loops=1000000)

# 剩余可漏水果控制
class Mark:
    def __init__(self,frame,screen,imgs,game_over):
        self.mark=3
        self.frame=frame
        self.screen=screen
        self.imgs=imgs
        self.game_over=game_over

    def post(self):
        self.mark-=1
        if self.mark==2:
            self.frame.blit(pygame.transform.scale(self.imgs['xf'], (pw(0.035), ph(0.05))), (pw(0.865), ph(0.01)))
        elif self.mark==1:
            self.frame.blit(pygame.transform.scale(self.imgs['xxf'], (pw(0.04), ph(0.065))), (pw(0.9), ph(0.01)))
        elif self.mark==0:
            self.frame.blit(pygame.transform.scale(self.imgs['xxxf'], (pw(0.06), ph(0.08))), (pw(0.94), ph(0.01)))
            self.game_over()
