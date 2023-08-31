import pygame
import time
from tools import q_exit,ph

# 全局时间管理类
class EventHandler:
    def __init__(self):
        self.push_list=[]

    # 用于注册回调函数
    def register_callback(self, func, *args, **kwargs):
        self.push_list.append((func,args,kwargs))

    # 载入剩余事件
    def load_event(self):
        for a_event in pygame.event.get():
            if a_event.type == pygame.QUIT:
                q_exit()
            if a_event.type == pygame.KEYDOWN:
                if a_event.key == pygame.K_ESCAPE:
                    q_exit()
            for func,args,kwargs in self.push_list:
                func(a_event,*args,**kwargs)

# 用于跟踪窗口活跃状态
class ActiveManager:
    def __init__(self):
        self.active=True

    def push(self,event):
        if event.type == pygame.ACTIVEEVENT:
            if event.gain:
                self.active = True
            else:
                self.active = False

# 全局鼠标轨迹控制类
class Orbit:
    def __init__(self,screen):
        self.click=False
        self.orbit=[]
        self.screen=screen

    def push(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.click = True
            self.orbit = []
        elif event.type == pygame.MOUSEBUTTONUP:
            self.click = False
        elif event.type == pygame.MOUSEMOTION and self.click:
            self.orbit.append([time.time_ns()/1000000,event.pos])

    def draw(self):
        now=time.time_ns() / 1000000
        self.orbit=list(filter(lambda x:now-x[0]<=100,self.orbit))

        for i in range(1,len(self.orbit)):
            pygame.draw.line(self.screen, (255, 255, 255),
                             self.orbit[i-1][1], self.orbit[i][1],
                             int(ph(0.0003)*(self.orbit[i][0]+100-now)))

