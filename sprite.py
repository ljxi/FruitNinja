from tools import pw,ph,k_to_deg,get_hit_k,abs_path
import pygame
import random
import math
class Speed:
    def __init__(self,x=0,y=0):
        self.x=x
        self.y=y

# 重力物件类
class Gravity(pygame.sprite.Sprite):
    dt = 0.016
    g = 2*ph(1)

    # 根据重力更新位置
    def update_position(self,speed,rect) -> None:
        speed.y -= Gravity.g * Gravity.dt
        rect.top -= speed.y * Gravity.dt
        rect.centerx += speed.x * Gravity.dt
        if rect.top>ph(1):
            self.kill()

    # 随机生成物体初始数据
    def get_random_gravity_data(self):
        height = (0.375 * random.random() + 0.625) * ph(1)
        # height=ph(1)
        t = (8 * height / Fruit.g) ** 0.5
        x_in = pw(1) * random.random()
        x_out = pw(1) * random.random()
        speed_x = (x_out - x_in) / t
        speed_y = (2 * Fruit.g * height) ** 0.5
        return {
            'height': height,
            'time': t,
            'x_in': x_in,
            'x_out': x_out,
            'speed_x': speed_x,
            'speed_y': speed_y
        }

# 影子类
class Shadow(pygame.sprite.Sprite):
    def __init__(self,rect,imgs):
        super().__init__()
        self.target_rect=rect
        self.image = pygame.transform.scale(imgs['shadow'], (pw(0.1), ph(0.15)))
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.centery=self.target_rect.bottom+25
        self.rect.centerx=self.target_rect.centerx+50

# 水果类
class Fruit(Gravity):
    fruits = {'apple': [(pw(0.1), ph(0.15)), (189, 227, 37)],
                   'banana': [(pw(0.13), ph(0.08)), (255, 227, 55)],
                   'basaha': [(pw(0.1), ph(0.15)), (196, 13, 0)],
                   'peach': [(pw(0.1), ph(0.15)), (241, 93, 20)],
                   'sandia': [(pw(0.15), ph(0.225)), (88, 135, 15)]}
    fruit_types = list(fruits.keys())

    def __init__(self,func,imgs,music,sprite_grop,orbit,score):
        super().__init__()
        self.score=score
        self.music=music
        self.sprite_grop=sprite_grop
        self.orbit=orbit
        self.imgs=imgs
        self.dieFunc=func
        self.name=random.choice(self.fruit_types)
        self.data=self.fruits[self.name]
        self.image=pygame.transform.scale(imgs[self.name],self.data[0])
        self.rect = self.image.get_rect()
        self.shadow=Shadow(self.rect,imgs)
        sprite_grop.add(self.shadow)
        self.rect.top = ph(1)
        self.speed=Speed()
        height,time,\
            self.rect.centerx,x_out,\
            self.speed.x,self.speed.y = self.get_random_gravity_data().values()

    def update(self):
        self.update_position(self.speed,self.rect)
        k=get_hit_k(self.rect, self.orbit)
        if k:
            self.score()
            self.music.play('splatter')
            self.sprite_grop.add(FruitCut(self.name+"-1",self.rect.centerx,self.rect.top,-200,k,self.imgs))
            self.sprite_grop.add(FruitCut(self.name + "-2", self.rect.centerx, self.rect.top, 200,k,self.imgs))
            for i in range(20):
                self.sprite_grop.add(Circle(self.data[1], self.rect.centerx, self.rect.centery,2))
            self.kill()
        # rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
        # self.rect=self.image.get_rect(center = rotated_image_center)

    def kill(self) -> None:
        self.shadow.kill()
        if self.rect.top>ph(1):
            self.dieFunc()
        super().kill()

# 炸弹类
class Boom(Gravity):
    def __init__(self,imgs,music,sprite_grop,orbit,game_over):
        super().__init__()
        self.game_over=game_over
        self.music=music
        self.sprite_grop=sprite_grop
        self.orbit=orbit
        self.imgs=imgs
        self.sound=pygame.mixer.Sound(abs_path('./assets/sound/bomb-fuse.ogg'))
        self.sound.set_volume(0.5)
        self.sound.play(loops=10000)
        self.image=pygame.transform.scale(imgs['boom'],(pw(0.1), ph(0.15)))
        self.rect = self.image.get_rect()
        self.shadow=Shadow(self.rect,imgs)
        sprite_grop.add(self.shadow)
        self.rect.top = ph(1)
        self.speed = Speed()
        height, time, \
            self.rect.centerx, x_out, \
            self.speed.x, self.speed.y = self.get_random_gravity_data().values()

    def update(self):
        self.update_position(self.speed,self.rect)
        if random.random()>0.6:
            self.sprite_grop.add(Circle((242,191,98), self.rect.left, self.rect.top,0.5))
        k=get_hit_k(self.rect, self.orbit)
        if k:
            self.music.play('boom',1.0)
            self.game_over(self.rect)

    def kill(self) -> None:
        self.shadow.kill()
        self.sound.fadeout(500)
        super().kill()

# 半水果类
class FruitCut(Gravity):
    def __init__(self,name,centerx,top,speed_x,k,imgs):
        super().__init__()
        self.fruit = {'apple': [(pw(0.1), ph(0.15)),-135],
                   'banana': [(pw(0.13), ph(0.08)),-90],
                   'basaha':[(pw(0.1), ph(0.15)),-45],
                   'peach': [(pw(0.1), ph(0.15)),-135],
                   'sandia': [(pw(0.15), ph(0.225)),-90]}
        self.deg=k_to_deg(k)+self.fruit[name.split('-')[0]][1]
        self.ori_image=pygame.transform.scale(imgs[name],self.fruit[name.split('-')[0]][0])
        self.image = pygame.transform.rotate(self.ori_image,self.deg)
        self.rect = self.image.get_rect()
        self.rect.centerx=centerx
        self.rect.top = top
        self.speed=Speed(x=speed_x)

    def update(self):
        self.update_position(self.speed,self.rect)

# 粒子效果类
class Circle(Gravity):
    def __init__(self,color,center_x,center_y,energy=1.0):
        super().__init__()
        self.ori_image = pygame.Surface([pw(0.02), pw(0.02)]).convert_alpha()
        self.ori_image .fill((255, 255, 255, 0))
        self.image=self.ori_image.copy()
        self.color=color
        pygame.draw.circle(self.image, color, [pw(0.01), pw(0.01)], pw(0.01))
        self.rect = self.image.get_rect()
        self.rect.centerx = center_x
        self.rect.centery = center_y

        deg=random.random()*math.pi/2
        k=math.tan(deg)
        speed=ph(1)*pw(1)*random.random()*energy*0.5
        self.speed=Speed()
        self.speed.x = (speed/(1+k*k))**0.5*random.choice([1,-1])
        self.speed.y = self.speed.x*k*random.choice([1,-1])
        self.size=1

    def update(self):
        self.update_position(self.speed,self.rect)

        self.image = self.ori_image.copy()
        pygame.draw.circle(self.image, self.color, [pw(0.01), pw(0.01)], self.size*ph(0.01))

        self.size-=0.03
        if self.size<=0:
            self.kill()
            return
