import pygame as pg
import numpy as np
import math
import ctypes

pg.init()

#Constantes
intro_text_size=50
font = pg.font.SysFont('Arial', 30)
intro_font = pg.font.SysFont('Arial', intro_text_size)
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
width = screensize[0]
height = screensize[1]
win_size = (width, height)

#Couleurs
FOND_COLOR= 25,25,25
YELLOW = 255,255,0

#Variables
max_mass=400
min_mass=10
min_radius=5
max_radius=50
min_speed=1
max_speed=5

class Ball:
    def __init__(self,radius,bouncefactor,color,mass,xpos,ypos,xspeed,yspeed,id):
        self.xspeed=xspeed
        self.yspeed=yspeed
        self.xpos=xpos
        self.ypos=ypos
        self.radius=radius
        self.bouncefactor=bouncefactor
        self.base_color=color
        self.color=color
        self.mass=mass
        self.sprite=pg.transform.scale(pg.image.load(f"visage{(mass//((max_mass)//4)+1)}.png").convert(),(radius,radius))
        self.interact_cooldown=0
        self.id=id
    
    def move(self,dt):
        new_xpos=self.xpos+self.xspeed
        new_ypos=self.ypos+self.yspeed
        if new_xpos-self.radius<=0 or new_xpos+self.radius>width:
            self.xspeed=-self.xspeed
        elif new_ypos-self.radius<=0 or new_ypos+self.radius>height:
            self.yspeed=-self.yspeed 
        self.xpos+=self.xspeed
        self.ypos+=self.yspeed

def newball(balls):
    radius=np.random.randint(min_radius,max_radius)
    bounce_factor=np.random.random()
    mass= np.random.randint(min_mass,max_mass)
    xpos=np.random.randint(radius,width-radius)
    ypos=np.random.randint(radius,height-radius)
    xspeed=np.random.randint(min_speed,max_speed)
    yspeed=np.random.randint(min_speed,max_speed)
    color = (255-(mass/max_mass)*255,150-(mass/max_mass)*150,100-(mass/max_mass)*100)
    new_ball = Ball(radius=radius,bouncefactor=bounce_factor,color=color,mass=mass,xpos=xpos,ypos=ypos,xspeed=xspeed,yspeed=yspeed,id=len(balls))
    return new_ball

def drawball(surface,balls):
    for b in balls:
        pg.draw.circle(surface=surface,color=b.color,center=(b.xpos,b.ypos),radius=b.radius)
        surface.blit(b.sprite,[b.xpos-b.radius/2,b.ypos-b.radius/2])

def check_collision(balls):
    if len(balls)>1:
        for b in balls:
            for b2 in balls:
                if np.sqrt((b.xpos-b2.xpos)**2+(b.ypos-b2.ypos)**2)<=b.radius+b2.radius and b.id!=b2.id:
                    resolve_collision(b,b2)

def resolve_collision(ball1, ball2):
    # Vecteur de séparation
    dx = ball2.xpos - ball1.xpos
    dy = ball2.ypos - ball1.ypos
    dist = np.hypot(dx, dy)

    # Normale de collision
    nx = dx / dist
    ny = dy / dist

    # Vitesse relative
    rvx = ball2.xspeed - ball1.xspeed
    rvy = ball2.yspeed - ball1.yspeed

    # Vitesse relative projetée sur la normale
    vel_along_normal = rvx * nx + rvy * ny

    # Les sphères s'éloignent déjà → pas de collision
    if vel_along_normal > 0:
        return

    m1, m2 = ball1.mass, ball2.mass

    # Collision parfaitement élastique
    restitution = 1.0

    # Impulsion scalaire
    j = -(1 + restitution) * vel_along_normal
    j /= (1 / m1 + 1 / m2)

    # Impulsion vectorielle
    impulse_x = j * nx
    impulse_y = j * ny

    # Application des vitesses
    ball1.xspeed -= impulse_x / m1
    ball1.yspeed -= impulse_y / m1
    ball2.xspeed += impulse_x / m2
    ball2.yspeed += impulse_y / m2

    # Correction d’overlap (position)
    penetration = ball1.radius + ball2.radius - dist
    if penetration > 0:
        percent = 1.0        # 100% de correction
        slop = 0.001         # tolérance anti-jitter

        correction = max(penetration - slop, 0) / (1 / m1 + 1 / m2)
        correction_x = correction * nx * percent
        correction_y = correction * ny * percent

        ball1.xpos -= correction_x / m1
        ball1.ypos -= correction_y / m1
        ball2.xpos += correction_x / m2
        ball2.ypos += correction_y / m2

def calcul_total_cinetic(balls):
    total_cinetic = sum(0.5*b.mass*(b.xspeed**2+b.yspeed**2) for b in balls)
    return total_cinetic

def move_balls(balls,dt):
    for b in balls:
        b.move(dt)

def set_text_cinetic(surface,total_cinetic):
    text = font.render(f"Total cinetic energy: {total_cinetic:.2f}", True, (255, 255, 255))
    surface.blit(text, (10, 10))

def step_update(surface,balls,dt):
    check_collision(balls)
    move_balls(balls,dt)
    drawball(surface,balls)
    check_interact_color(balls)
    total_cinetic=calcul_total_cinetic(balls)
    set_text_cinetic(surface,total_cinetic)

def speedup_balls(balls):
    if len(balls)==0:
        return
    else:
        if len(balls)==1:
            random_ball=0
            b=balls[0]
        elif len(balls)>1:
            random_ball = np.random.randint(0,len(balls))
            b=balls[random_ball]
        new_xspeed = b.xspeed/(abs(b.xspeed)+abs(b.yspeed))
        new_yspeed = b.yspeed/(abs(b.xspeed)+abs(b.yspeed))
        new_xspeed = b.xspeed + abs(new_xspeed) if b.xspeed>0 else b.xspeed - abs(new_xspeed)
        new_yspeed = b.yspeed + abs(new_yspeed) if b.yspeed>0 else b.yspeed - abs(new_yspeed)
        balls[random_ball].xspeed=new_xspeed
        balls[random_ball].yspeed=new_yspeed
        balls[random_ball].color=YELLOW
        balls[random_ball].interact_cooldown=10

def check_interact_color(balls):
    for i,b in enumerate(balls):
        if b.color==YELLOW:
            if b.interact_cooldown<=0:
                balls[i].color=b.base_color
                balls[i].interact_cooldown=0
            else:
                balls[i].interact_cooldown-=1

def display_intro(surface):
    clock = pg.time.Clock()
    surface_text = pg.Surface(win_size, pg.SRCALPHA)

    # --- Préparation ---
    surface.fill(FOND_COLOR)
    surface_text.fill(FOND_COLOR)
    surface_text.set_alpha(255)

    intro_text = [
        intro_font.render("Control Key", True, (255, 255, 255)),
        intro_font.render("New Ball : Space", True, (255, 255, 255)),
        intro_font.render("Speed up random ball : S", True, (255, 255, 255)),
        intro_font.render("Erase last ball : K", True, (255, 255, 255)),
        intro_font.render("Pause : P", True, (255, 255, 255)),
        intro_font.render("Quit : Escape", True, (255, 255, 255))
    ]

    for i, t in enumerate(intro_text):
        surface_text.blit(t,(width // 2 - t.get_rect().centerx, height // 2 - intro_text_size * (len(intro_text) // 2)+ i * (intro_text_size + 5)))

    press_continue = intro_font.render("Press any key to continue", True, (255, 255, 255))

    # --- Affichage initial ---
    surface.blit(surface_text, (0, 0))
    pg.display.flip()
    pg.time.wait(1000)

    # --- Affiche "press any key" ---
    surface_text.blit(press_continue,(width // 2 - press_continue.get_rect().centerx, height - intro_text_size * 2))

    surface.fill(FOND_COLOR)
    surface.blit(surface_text, (0, 0))
    pg.display.flip()

    # --- Attente touche utilisateur ---
    waiting = True
    while waiting:
        clock.tick(60)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN:
                waiting = False

    # --- Fade-out ---
    alpha = 255
    while alpha > 0:
        clock.tick(60)
        alpha -= 4
        surface_text.set_alpha(alpha)

        surface.fill(FOND_COLOR)
        surface.blit(surface_text, (0, 0))
        pg.display.flip()

    return
        

def main():
    surface = pg.display.set_mode(win_size)
    balls=[]
    clock=pg.time.Clock()
    pause=False
    #Introduction
    display_intro(surface)
    while True:
        dt = clock.tick(60) / 1000.0 
        surface.fill(FOND_COLOR)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                loop = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_p:
                    pause=True if pause==False else False
                elif event.key == pg.K_ESCAPE:
                    pg.quit()
                    return
                if pause: 
                    continue   
                if event.key == pg.K_SPACE:
                    balls.append(newball(balls))
                elif event.key == pg.K_k:
                    if len(balls)>0:
                        balls.pop()
                elif event.key == pg.K_s:
                    speedup_balls(balls)
        if pause:
            continue
        step_update(surface,balls,dt)
        pg.display.flip()
        clock.tick(100)
    
if __name__ == '__main__':
    main()