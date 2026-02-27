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

BULLET_SPEED = 10
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
        self.max_health = 10
        self.health = 10
        self.display_health = 10.0   

    def update(self,player_x,player_y):
        dx=player_x -self.x
        dy=player_y-self.y
        self.angle=math.degrees(math.atan2(dy,dx))

        self.x += math.cos((math.radians(self.angle)))*self.speed
        self.y += math.sin(math.radians(self.angle))*self.speed
        # Smooth health bar animation
        self.display_health += (self.health - self.display_health) * 0.15



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
     if self.health< self.max_health:
       bar_width = 50
       bar_height = 6

       health_ratio = max(0, self.display_health / self.max_health)
       health_width = bar_width * health_ratio

       bar_x = self.x - bar_width / 2
       bar_y = self.y + self.radius + 20

       # Red background
       arcade.draw_lbwh_rectangle_filled(
       bar_x, bar_y, bar_width, bar_height, arcade.color.RED
        )

       # Green foreground (smooth)
       arcade.draw_lbwh_rectangle_filled(
       bar_x, bar_y, health_width, bar_height, arcade.color.GREEN
        )

       arcade.draw_lbwh_rectangle_outline(
         bar_x, bar_y, bar_width, bar_height, arcade.color.WHITE, 1
       )

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
        self.can_shoot = True
        self.auto_fire = False
        self.shoot_timer = 0.0
        self.enemy_spawn_timer=0 
        self.health=100
        self.score=0   
        self.game_over=False
        # self.shoot_cooldown =0

        self.keys_pressed = set()
        self.score_text = arcade.Text(
              "Score: 0", 10, SCREEN_HEIGHT - 30,
               arcade.color.WHITE, 20
            )       

        self.health_text = arcade.Text(
            "Health: 100", 10, SCREEN_HEIGHT - 60,
            arcade.color.WHITE, 20
            )

        self.game_over_text = arcade.Text(
            "GAME OVER",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
            arcade.color.RED, 48,
         anchor_x="center"
            )

        self.final_score_text = arcade.Text(
            "", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
              arcade.color.WHITE, 36,
              anchor_x="center"
            )

    def restart_game(self):
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_angle = 0

        self.bullets.clear()
        self.enemies.clear()

        self.score = 0
        self.health = 100
        self.game_over = False

        self.can_shoot = True
        self.auto_fire = False
        self.shoot_timer = 0
        self.enemy_spawn_timer = 0

        self.score_text.text = "Score: 0"
        self.health_text.text = "Health: 100"

    def on_draw(self):
       self.clear()

       if not self.game_over:
        # -------- NORMAL GAME DRAW --------
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

          for enemy in self.enemies:
            enemy.draw()
            enemy.draw_health_bar()

          self.score_text.draw()
          self.health_text.draw()

       else:
        # -------- GAME OVER SCREEN ONLY --------
         self.game_over_text.draw()
         self.final_score_text.draw()
         self.restart_text.draw()
        
    def on_update(self, delta_time):
        
        # self.shoot_cooldown -=delta_time
        self.shoot_timer += delta_time

        self.enemy_spawn_timer -= delta_time

        
        if not self.game_over:
           self.score_text.text = f"Score: {self.score}"
           self.health_text.text = f"Health: {self.health}"
           self.final_score_text.text = f"FINAL SCORE {self.score}"

        
        if self.enemy_spawn_timer <=0:
            self.enemies.append(Enemy())
            self.enemy_spawn_timer=ENEMY_SPAWN_RATE

        if self.game_over:
           return

        if self.auto_fire and arcade.key.SPACE in self.keys_pressed:
           if self.shoot_timer >= PLAYER_SHOOT_COOLDOWN:
             self.shoot()
             self.shoot_timer = 0
        
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
                                  (enemy.y-self.player_y)**2)
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
                   enemy.health-=1
                   self.bullets.remove(bullet)
                   
                   if enemy.health<=0:
                      self.enemies.remove(enemy)
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
          
         if self.game_over and key == arcade.key.R:
          self.restart_game()
          return
         
         if key == arcade.key.SPACE and not self.game_over:
            if self.can_shoot:
               self.shoot()              # single shot
               self.can_shoot = False    # block repeat
               self.auto_fire = True     # allow hold fire

        # record key
         self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.SPACE:
          self.can_shoot = True
          self.auto_fire = False

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