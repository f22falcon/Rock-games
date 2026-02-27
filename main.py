import arcade
import math
import random



# defining global variables
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Alien Invasion 2"

PLAYER_SCALE = 0.3
PLAYER_SPEED = 5
PLAYER_ROTATION_SPEED = 3
PLAYER_SHOOT_COOLDOWN = 0.2

BULLET_SPEED = 12
BULLET_SCALE = 0.8
ENEMY_SPAWN_RATE=1
ENEMY_SPEED_MIN=1
ENEMY_SPEED_MAX=3
ENEMY_SCALE=0.3


class Enemy:
    def __init__(self):
        side=random.choice(["top","right","bottam","left"])
        if side == "top":
            self.x=random.uniform(0,SCREEN_WIDTH)
            self.y=SCREEN_HEIGHT+20

        elif side == "right":
            self.x=SCREEN_WIDTH+20
            self.y=random.uniform(0,SCREEN_HEIGHT)

        elif side == "bottam":
            self.x=random.uniform(0,SCREEN_WIDTH)
            self.y=-20

        else :
            self.x=-20
            self.y=random.uniform(0,SCREEN_HEIGHT)
        
        self.speed= random.uniform(ENEMY_SPEED_MIN,ENEMY_SPEED_MAX)
        self.angle=0
        self.radius=150* ENEMY_SCALE
        self.health=1

    def update(self,player_x,player_y):
        dx=player_x -self.x
        dy=player_y-self.y
        self.angle=math.degrees(math.atan2(dy,dx))

        self.x += math.cos((math.radians(self.angle)))*self.speed
        self.y += math.sin(math.radians(self.angle))*self.speed



    def draw(self):
        arcade.draw_triangle_filled(
            self.x +math.cos(math.radians(self.angle))*self.radius*2,
            self.y +math.sin(math.radians(self.angle))*self.radius*2,
            self.x +math.cos(math.radians(self.angle + 140))*self.radius,
            self.y +math.sin(math.radians(self.angle + 140))*self.radius,
            self.x +math.cos(math.radians(self.angle - 140))*self.radius,
            self.y +math.sin(math.radians(self.angle - 140))*self.radius,
            arcade.color.BLUE

        )

    def draw_health_bar(self):
        if self.health < self.max_health:
            bar_width=50
            bar_height=6
            helath_percentage=self.helath/self.max_health
            health_width=helath_percentage *bar_width

            bar_x=self.x
            bar_y=self.y +self.radius +20

            arcade.draw_rectangle_filled(
                 bar_x,bar_y,bar_width,bar_height,arcade.color.RED)
            arcade.draw_rectangle_filled(bar_x-(bar_width-health_width)/2,bar_y,
                                         health_width,bar_height,arcade.color.GREEN)
            arcade.draw_rectangle_outline(
                bar_x,bar_y,bar_width,bar_height,arcade.color.WHITE,1)
            

    def is_off_screen(self):
        return (self.x<-50 or self.x > SCREEN_WIDTH +50 or
                self.y <-50 or self.y >SCREEN_HEIGHT+50)


        
class Bullet:
    def __init__(self,x,y,angle):
        self.x=x
        self.y=y
        self.angle=angle
        self.speed=BULLET_SPEED
        self.radius= 4*BULLET_SCALE

    def update(self ):
        #Move bullet  based on angle
        self.x += math.cos(math.radians(self.angle))*self.speed
        self.y += math.sin(math.radians(self.angle))*self.speed
    def draw(self):
        arcade.draw_circle_filled(self.x,self.y,self.radius,arcade.color.YELLOW)

    def is_off_screen(self):
        return (self.x<0 or self.x > SCREEN_WIDTH or
                self.y <0 or self.y >SCREEN_HEIGHT)

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_angle = 0
        self.player_radius = 150 * PLAYER_SCALE

        self.bullets =[]
        self.enemies =[]
        self.shoot_timer = 0.0
        self.enemy_spawn_timer=0 
        self.health=100
        self.score=0   
        self.game_over=False
        # self.shoot_cooldown =0

        self.keys_pressed = set()

    def on_draw(self):
        self.clear()

        arcade.draw_triangle_filled(
            self.player_x + math.cos(math.radians(self.player_angle)) * self.player_radius * 1.5,
            self.player_y + math.sin(math.radians(self.player_angle)) * self.player_radius * 1.5,
            self.player_x + math.cos(math.radians(self.player_angle + 150)) * self.player_radius,
            self.player_y + math.sin(math.radians(self.player_angle + 150)) * self.player_radius,
            self.player_x + math.cos(math.radians(self.player_angle - 150)) * self.player_radius,
            self.player_y + math.sin(math.radians(self.player_angle - 150)) * self.player_radius,
            arcade.color.WHITE
        )
        for bullet in self.bullets:
            bullet.draw()

        for enemy  in self.enemies:
            enemy.draw()

        arcade.draw_text(
        f"Score: {self.score}",
        10, SCREEN_HEIGHT - 30,
        arcade.color.WHITE, 20
    )

        arcade.draw_text(
        f"Health: {self.health}",
        10, SCREEN_HEIGHT - 60,
        arcade.color.WHITE, 20
    )
        
        if self.game_over:
            arcade.draw_rectangle_filled(SCREEN_WIDTH//2,SCREEN_HEIGHT//2,
                                         SCREEN_WIDTH,SCREEN_HEIGHT,(0,0,0,200))
            arcade.draw_text("GAME OVER",SCREEN_WIDTH//2,SCREEN_HEIGHT//2+50,
                             arcade.color.RED,48,ancore_x='center')
            arcade.draw_text(f"FINAL SCORE {self.score}",SCREEN_WIDTH//2,SCREEN_HEIGHT//2-50,
                             arcade.color.WHITE,36,ancore_x='center')
            arcade.draw_text("Press R to Restart",SCREEN_WIDTH//2,SCREEN_HEIGHT//2-120,
                             arcade.color.YELLOW,24,ancore_x='center')
            

    def on_update(self, delta_time):
        
        # self.shoot_cooldown -=delta_time
        self.shoot_timer += delta_time

        self.enemy_spawn_timer -= delta_time

        if arcade.key.SPACE in self.keys_pressed:
           while self.shoot_timer >= PLAYER_SHOOT_COOLDOWN:
            self.shoot()
            self.shoot_timer -= PLAYER_SHOOT_COOLDOWN

        if self.enemy_spawn_timer <=0:
            self.enemies.append(Enemy())
            self.enemy_spawn_timer=ENEMY_SPAWN_RATE


        if arcade.key.SPACE in self.keys_pressed:
            self.shoot()

        if arcade.key.W in self.keys_pressed:
            self.player_y += PLAYER_SPEED

        if arcade.key.S in self.keys_pressed:
            self.player_y -= PLAYER_SPEED

        if arcade.key.A in self.keys_pressed:
            self.player_x -= PLAYER_SPEED

        if arcade.key.D in self.keys_pressed:
            self.player_x += PLAYER_SPEED

       
        # Keep player inside screen
        self.player_x = max(self.player_radius, min(SCREEN_WIDTH - self.player_radius, self.player_x))
        self.player_y = max(self.player_radius, min(SCREEN_HEIGHT - self.player_radius, self.player_y))


        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
               self.bullets.remove(bullet)
        
        for enemy in self.enemies[:]:
            enemy.update(self.player_x,self.player_y)
            distance = math.sqrt((enemy.x-self.player_x)**2+
                                  (enemy.x-self.player_x)**2)
            if distance < enemy.radius +self.player_radius:
                self.health -=10
                self.enemies.remove(enemy)
                if self.health <=0:
                    self.game_over=True
                elif enemy.is_off_screen():
                  self.enemies.remove(enemy)
 

        for bullet in self.bullets[:]:
            
           for enemy in self.enemies[:]:
               distance =math.sqrt((bullet.x-enemy.x)**2
                                   +(bullet.y-enemy.y)**2)
               if distance < bullet.radius+enemy.radius:
                   self.enemies.remove(enemy)
                   if bullet in self.bullets:
                       self.bullets.remove(bullet)
                   self.score +=10
                   break
            
            

    def shoot(self):
        # if self.shoot_cooldown <=0:
            bullet_x=self.player_x+\
                math.cos(math.radians(self.player_angle))*self.player_radius
            bullet_y=self.player_y+\
                math.sin(math.radians(self.player_angle))*self.player_radius
            self.bullets.append(Bullet(bullet_x,bullet_y,self.player_angle))
            

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        self.keys_pressed.discard(key)

    def on_mouse_motion(self, x, y, dx, dy):
        dx = x - self.player_x
        dy = y - self.player_y
        self.player_angle = math.degrees(math.atan2(dy, dx))

    def restart_game(self):
        self.player_x=SCREEN_WIDTH //2
        self.player_y=SCREEN_HEIGHT //2
        self.player_angle=0
        self.bullets.clear()
        self.enemies.clear()
        self.score=0
        self.health=100
        self.game_over=False



def main():
    window = MyGame()
    arcade.run()

if __name__ == "__main__":
    main()