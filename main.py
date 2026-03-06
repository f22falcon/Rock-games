import arcade
import math
import random



# defining global variables
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Alien Invasion 2"

PLAYER_SCALE = 0.18
PLAYER_SPEED = 6
PLAYER_ROTATION_SPEED = 6
PLAYER_SHOOT_COOLDOWN = 0.2

BULLET_SPEED = 10
BULLET_SCALE = 0.6
ENEMY_SPAWN_RATE=1
ENEMY_SPEED_MIN=1
ENEMY_SPEED_MAX=3
ENEMY_SCALE=0.18

ENEMY_TYPES=["normal","shooter"]
ENEMY_SHOOT_COOLDOWN = 2.0
ENEMY_BULLET_SPEED = 5
ENEMY_BULLET_COLOR= arcade.color.RED
PARTICLE_COUNT = 40
PARTICAL_FADE_RATE=8
CELL_SIZE = 120
MAX_ATTACKERS = 4
SEPARATION_FORCE = 0.3
PLAYER_FRICTION = 0.90
MAX_PLAYER_SPEED = 15

class PowerUp:
   def __init__(self,x,y,power_type):
        self.x=x
        self.y=y
        self.type=power_type
        self.radius =20
        self.speed_y =-1
        
        if power_type =="rapid_fire":
           self.color=arcade.color.CYAN
        elif power_type =="shield":
           self.color=arcade.color.BLUE
        else:
           self.color=arcade.color.GREEN

   def update(self):
      self.y +=self.speed_y

   def draw(self):
      arcade.draw.draw_circle_filled(self.x,self.y,self.radius,self.color)
      if self.type == "rapaid_fire":
         arcade.draw_text("",self.x-6,self.y-
                          6,arcade.color.WHITE,12)
      elif self.type == "shield":
         arcade.draw_text("",self.x-6,self.y-
                          6,arcade.color.WHITE,12)
      else:
          arcade.draw_text("",self.x-6,self.y-
                          6,arcade.color.WHITE,12)
    
     
class Particle:

    def __init__(self,x,y):

        self.x=x
        self.y=y

        self.angle=random.uniform(0,360)
        self.speed=random.uniform(2,6)

        self.life=random.uniform(0.5,1.2)
        self.radius=random.uniform(2,4)

    def update(self,dt):

        self.x += math.cos(math.radians(self.angle))*self.speed
        self.y += math.sin(math.radians(self.angle))*self.speed

        self.life -= dt

    def draw(self):

        arcade.draw_circle_filled(
            self.x,
            self.y,
            self.radius,
            random.choice ([arcade.color.YELLOW,
                            arcade.color.ORANGE,
                            arcade.color.RED
            ])
        )


class EnemyBullet:
    def __init__ (self,x,y,angle):
        self.x=x
        self.y=y
        self.angle=angle
        self.speed = ENEMY_BULLET_SPEED
        self.radius = 6
        self.color = ENEMY_BULLET_COLOR

    def update(self):
        self.x += math.cos(math.radians(self.angle)) *self.speed
        self.y += math.sin(math.radians(self.angle)) *self.speed
        
    def draw(self):
        arcade.draw_circle_filled(self.x,self.y,self.radius,self.color)

    def is_off_screen(self):
        return (self.x <0 or self.x >SCREEN_WIDTH or
                self.y <0 or self.y >SCREEN_HEIGHT)  

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
        
        self.enemy_type = random.choice(ENEMY_TYPES)
        self.speed= random.uniform(ENEMY_SPEED_MIN,ENEMY_SPEED_MAX)
        self.angle=0
        self.radius=150* ENEMY_SCALE
        self.max_health = 5
        self.health = 5
        self.display_health = 5
        self.shoot_cooldown=0  
    
    def take_damage(self):
        self.health -=1
        return self.health <=0 

    def update(self,player_x,player_y,delta_time):
        dx=player_x -self.x
        dy=player_y-self.y
        self.angle=math.degrees(math.atan2(dy,dx))

        self.x += math.cos((math.radians(self.angle)))*self.speed
        self.y += math.sin(math.radians(self.angle))*self.speed
        # Smooth health bar animation
        self.display_health += (self.health - self.display_health) * 0.15

        if  self.enemy_type == "shooter":
            self.shoot_cooldown -= delta_time

    def shoot(self):
        if self.enemy_type == "shooter" and self.shoot_cooldown <=0:
            bullet_x=self.x+\
               math.cos(math.radians(self.angle))*self.radius
            bullet_y=self.y+\
               math.sin(math.radians(self.angle))*self.radius
            self.shoot_cooldown = ENEMY_SHOOT_COOLDOWN
            return EnemyBullet(bullet_x,bullet_y,self.angle)
        return None


    def draw(self):
        if self.enemy_type =="shooter":
            color =arcade.color.RED

        else:
            color =arcade.color.BLUE

        arcade.draw_triangle_filled(
            self.x +math.cos(math.radians(self.angle))*self.radius*2,
            self.y +math.sin(math.radians(self.angle))*self.radius*2,
            self.x +math.cos(math.radians(self.angle + 140))*self.radius,
            self.y +math.sin(math.radians(self.angle + 140))*self.radius,
            self.x +math.cos(math.radians(self.angle - 140))*self.radius,
            self.y +math.sin(math.radians(self.angle - 140))*self.radius,
            color

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
    

class BossBullet:
    def __init__(self,x,y,angle,is_big=False):
        self.x=x
        self.y=y
        self.angle= angle 
        self.is_big=is_big
        self.speed=7
        self.damage=999 if is_big else 30

        if is_big:
            self.radius=12
            self.color=arcade.color.YELLOW
        else:
            self.radius =6
            self.color = arcade.color.ORANGE_RED

    def update (self):
        self.x += math.cos(math.radians(self.angle)) *self.speed
        self.y += math.sin(math.radians(self.angle)) *self.speed

    def draw(self):
         arcade.draw_circle_filled(self.x,self.y,self.radius,self.color)
        
    def is_off_screen(self):
        return (self.x <0 or self.x >SCREEN_WIDTH or
                self.y <0 or self.y >SCREEN_HEIGHT)


class Boss:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 + random.uniform(-200,200)
        self.y = SCREEN_HEIGHT +100
        
        self.speed =2
        self.angle=0
        self.radius=150*ENEMY_SCALE*2
        self.health =100
        self.max_health=100
        self.mass = 40
        self.normal_shoot_cooldown=0
        self.big_shoot_cooldown =0
        self.damage_flash_timer=0
        self.flashing= False
        
        self.color=arcade.color.ORANGE

    def take_damage(self):
        self.health -=10
        self.damage_flash_timer=0.3
        self.flashing=True
        return self.health <= 0
    
    def update(self,player_x,player_y,delta_time):
        dx=player_x -self.x
        dy=player_y -self.y
        self.angle=math.degrees(math.atan2(dy,dx))

        self.x+=math.cos(math.radians(self.angle))*self.speed
        self.y+=math.sin(math.radians(self.angle))*self.speed
        
        self.normal_shoot_cooldown -=delta_time
        self.big_shoot_cooldown -=delta_time

        if self.flashing:
            self.damage_flash_timer -=delta_time
            if self.damage_flash_timer <=0:
                self.flashing =False

    def shoot_normal(self):
        if self.normal_shoot_cooldown <=0:
            bullet_x=self.x +\
               math.cos(math.radians(self.angle))*self.radius
            bullet_y=self.y +\
               math.sin(math.radians(self.angle))*self.radius
            self.normal_shoot_cooldown =1.5
            return BossBullet(bullet_x,bullet_y,self.angle,is_big=False)
        return None
    
    def shoot_big(self):
        if self.normal_shoot_cooldown <=0:
            bullet_x=self.x +\
               math.cos(math.radians(self.angle))*self.radius
            bullet_y=self.y +\
               math.sin(math.radians(self.angle))*self.radius
            self.normal_shoot_cooldown =8.0
            return BossBullet(bullet_x,bullet_y,self.angle,is_big=True)
        return None
    
    def draw(self):
        if self.flashing:
            draw_color=arcade.color.WHITE
        else:
            draw_color=self.color

        points =[
            (self.x + math.cos(math.radians(self.angle)) * self.radius * 1.5,
            self.y + math.sin(math.radians(self.angle)) * self.radius * 1.5),
            (self.x + math.cos(math.radians(self.angle + 90)) * self.radius,
            self.y + math.sin(math.radians(self.angle + 90)) * self.radius),
            (self.x + math.cos(math.radians(self.angle + 180)) * self.radius*1.5,
             self.y + math.sin(math.radians(self.angle + 180)) * self.radius*1.5),
            (self.x + math.cos(math.radians(self.angle + 270)) * self.radius,
            self.y + math.sin(math.radians(self.angle + 270)) * self.radius),
        ]
        arcade.draw_polygon_filled(points,draw_color)
        
    def draw_health_bar(self):

        bar_width = 100
        bar_height = 10

        health_ratio = self.health / self.max_health
        health_width = bar_width * health_ratio

        bar_x = SCREEN_WIDTH/2 - bar_width/2
        bar_y = SCREEN_HEIGHT - 40

        arcade.draw_lbwh_rectangle_filled(
        bar_x, bar_y, bar_width, bar_height, arcade.color.DARK_RED
        )

        arcade.draw_lbwh_rectangle_filled(
        bar_x, bar_y, health_width, bar_height, arcade.color.LIME_GREEN
        )

        arcade.draw_lbwh_rectangle_outline(
        bar_x, bar_y, bar_width, bar_height, arcade.color.WHITE, 2
       )



class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_angle = 0
        self.player_radius = 150 * PLAYER_SCALE

        self.player_vx = 0
        self.player_vy = 0
        self.player_mass = 10

        self.bullets =[]
        self.enemies =[]
        self.enemy_bullets = []
        self.boss_bullets =[]
        self.particals =[]
        self.boss =None
        self.can_shoot = True
        self.auto_fire = False
        self.shoot_timer = 0.0
        self.enemy_spawn_timer=0 
        self.boss_spawn_timer=5#random.uniform(20,60)
        self.health=100
        self.score=0   
        self.game_over=False
        self.collision_cooldown = 0
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
        self.restart_text = arcade.Text(
            "Press R to Restart",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 120,
            arcade.color.YELLOW,
            24,
            anchor_x="center"
            ) 
    
    def create_explosion(self,x,y,count=PARTICLE_COUNT):
       for _ in range(count):
        self.particals.append(Particle(x,y))


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
        
          for bullet in self.enemy_bullets:
             bullet.draw()

          for enemy in self.enemies:
            enemy.draw()
            enemy.draw_health_bar()

          self.score_text.draw()
          self.health_text.draw()

          if self.boss:
             self.boss.draw()
             self.boss.draw_health_bar()

          for bullet in self.boss_bullets:
            bullet.draw()

          for p in self.particals:
            p.draw()

       else:
        # -------- GAME OVER SCREEN ONLY --------
         self.game_over_text.draw()
         self.final_score_text.draw()
         self.restart_text.draw()
        
    def on_update(self, delta_time):
        
        # self.shoot_cooldown -=delta_time
        self.shoot_timer += delta_time
        self.collision_cooldown -= delta_time
        self.player_x += self.player_vx
        self.player_y += self.player_vy

        if self.game_over:
           return
        
        self.player_vx *= PLAYER_FRICTION
        self.player_vy *= PLAYER_FRICTION
        self.enemy_spawn_timer -= delta_time
        self.boss_spawn_timer -= delta_time

        speed = math.sqrt(self.player_vx**2 + self.player_vy**2)

        if speed > MAX_PLAYER_SPEED:
           self.player_vx = (self.player_vx / speed) * MAX_PLAYER_SPEED
           self.player_vy = (self.player_vy / speed) * MAX_PLAYER_SPEED

        
        if not self.game_over:
           self.score_text.text = f"Score: {self.score}"
           self.health_text.text = f"Health: {self.health}"
           self.final_score_text.text = f"FINAL SCORE {self.score}"

        
        if self.enemy_spawn_timer <=0:
            self.enemies.append(Enemy())
            self.enemy_spawn_timer=ENEMY_SPAWN_RATE


        # spawn boss timer
        

        if self.boss_spawn_timer <= 0 and self.boss is None:
           self.boss = Boss()

        if self.boss:

           # boss movement
           self.boss.update(self.player_x, self.player_y, delta_time)

           # -------- Boss collision with player --------
           dx = self.player_x - self.boss.x
           dy = self.player_y - self.boss.y

           distance = math.sqrt(dx*dx + dy*dy)

           nx = dx / distance
           ny = dy / distance

           rvx = self.player_vx
           rvy = self.player_vy

           vel_along_normal = rvx*nx + rvy*ny

           if vel_along_normal < 0:

            impulse = -(1.2) * vel_along_normal
            impulse /= (1/self.player_mass + 1/self.boss.mass)
            self.player_vx += impulse * nx / self.player_mass
            self.player_vy += impulse * ny / self.player_mass

           # damage player
            self.health -= 30

          # normalize direction
           if distance != 0:
              nx = dx / distance
              ny = dy / distance
           else:
              nx = 1
              ny = 0

           push_force = 40

           # push player away
           self.player_x += nx * push_force
           self.player_y += ny * push_force

           # push boss opposite direction
           self.boss.x -= nx * push_force
           self.boss.y -= ny * push_force

          # collision effect
           self.create_explosion(self.player_x, self.player_y, 20)
 
           if self.health <= 0:
             self.game_over = True

            # -------- Boss shooting --------
           bullet = self.boss.shoot_normal()
           if bullet:
             self.boss_bullets.append(bullet)

           bullet = self.boss.shoot_big()
           if bullet:
             self.boss_bullets.append(bullet)

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

        sorted_enemies = sorted(
        self.enemies,
        key=lambda e: (e.x - self.player_x)**2 + (e.y - self.player_y)**2
        )
        
        for i, enemy in enumerate(sorted_enemies):

          if i < MAX_ATTACKERS:
               enemy.update(self.player_x, self.player_y, delta_time)
          else:
            # orbit player
             dx = self.player_x - enemy.x
             dy = self.player_y - enemy.y

             dist = math.sqrt(dx*dx + dy*dy)

             if dist > 0:
               nx = dx / dist
               ny = dy / dist
               enemy.x += -ny * enemy.speed
               enemy.y += nx * enemy.speed

           # separation
          for other in self.enemies:

            if other is enemy:
              continue

            dx = enemy.x - other.x
            dy = enemy.y - other.y

            dist_sq = dx*dx + dy*dy

            if dist_sq < 2000:
             enemy.x += dx * SEPARATION_FORCE
             enemy.y += dy * SEPARATION_FORCE

          # shooting
          bullet = enemy.shoot()

          if bullet:
            self.enemy_bullets.append(bullet)

        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
               self.enemy_bullets.remove(bullet)

        for bullet in self.boss_bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.boss_bullets.remove(bullet)

        for bullet in self.boss_bullets[:]:

            distance = math.sqrt(
            (bullet.x - self.player_x)**2 +
            (bullet.y - self.player_y)**2
            )

            if distance < bullet.radius + self.player_radius:
              self.health -= bullet.damage
              self.boss_bullets.remove(bullet)

            if self.health <= 0:
               self.game_over = True

        for bullet in self.enemy_bullets[:]:
          distance = math.sqrt(
          (bullet.x - self.player_x)**2 +
          (bullet.y - self.player_y)**2
          )

          if distance < bullet.radius + self.player_radius:
             self.health -= 1
             self.enemy_bullets.remove(bullet)

          if self.health <= 0:
            self.game_over = True
        
        for p in self.particals[:]:
          p.update(delta_time)
          if p.life <= 0:
           self.particals.remove(p)

        for bullet in self.bullets[:]:
            
           for enemy in self.enemies[:]:
               distance =math.sqrt((bullet.x-enemy.x)**2
                                   +(bullet.y-enemy.y)**2)
               if distance < bullet.radius+enemy.radius:
                   self.create_explosion(bullet.x,bullet.y,4 )
                   enemy.health-=1
                   self.bullets.remove(bullet)
                   
                   if enemy.health<=0:
                      self.create_explosion(enemy.x,enemy.y,12)
                      self.enemies.remove(enemy)
                      self.score +=10
                   break
            
           if self.boss:    
              distance = math.sqrt(
              (bullet.x - self.boss.x)**2 +
              (bullet.y - self.boss.y)**2
                )

              if distance < bullet.radius + self.boss.radius:
                self.create_explosion(bullet.x,bullet.y,10)
                dead = self.boss.take_damage()
                self.bullets.remove(bullet)

                if dead:
                 self.create_explosion(self.boss.x, self.boss.y,120)
                 self.score += 500
                 self.boss = None

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


def main():
    window = MyGame()
    arcade.run()

if __name__ == "__main__":
    main()