import arcade
import math
import random
import os



# defining global variables
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Alien Invasion 2"

SPRITE_ANGLE_OFFSET = 90 
NORMAL_ENEMY_SPRITE_ANGLE =-90
FIRING_ENEMY_SPRITE_ANGLE =-90

PLAYER_SCALE = 0.14
PLAYER_SPEED = 6
PLAYER_ROTATION_SPEED = 6
PLAYER_SHOOT_COOLDOWN = 0.2

BULLET_SPEED = 10
BULLET_SCALE = 0.6
ENEMY_SPAWN_RATE=1
ENEMY_SPEED_MIN=0.5
ENEMY_SPEED_MAX=4
ENEMY_SCALE=0.14

ENEMY_TYPES=["normal","shooter"]
ENEMY_SHOOT_COOLDOWN = 2.0
ENEMY_BULLET_SPEED = 5
ENEMY_BULLET_COLOR= arcade.color.RED
PARTICLE_COUNT = 40
PARTICAL_FADE_RATE=8
CELL_SIZE = 120
MAX_ATTACKERS = 4
MAX_ENEMIES = 6
SEPARATION_FORCE = 0.05
PLAYER_FRICTION = 0.90
MAX_PLAYER_SPEED = 15

class PowerUp:
   def __init__(self,x,y,power_type):
        self.x=x
        self.y=y
        self.type=power_type
        self.radius =10
        self.speed_y =-1
        
        if power_type =="rapid_fire":
           self.color=arcade.color.BLUE
        elif power_type =="shield":
           self.color=arcade.color.CYAN
        else:
           self.color=arcade.color.GREEN

   def update(self):
      self.y +=self.speed_y

   def draw(self):
      arcade.draw_circle_filled(self.x,self.y,self.radius,self.color)
   
class Particle:

    def __init__(self,x,y):

        self.x=x
        self.y=y

        self.angle=random.uniform(0,360)
        self.speed=random.uniform(2,6)

        self.life=random.uniform(0.5,1.2)
        self.radius=random.uniform(1,3)

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
        
    def draw(self,game):
        if game.enemy_bullet_texture:
            arcade.draw_texture_rect(
            game.enemy_bullet_texture,
            arcade.rect.XYWH(
                self.x,
                self.y,
                10,
                20
            ),
            angle=-self.angle + 90
        )
        else:
         arcade.draw_circle_filled(self.x,self.y,self.radius,self.color)

    def is_off_screen(self):
        return (self.x <0 or self.x >SCREEN_WIDTH or
                self.y <0 or self.y >SCREEN_HEIGHT)  

class Bullet:
    def __init__(self):
       self.active=False

    def spawn(self,x,y,angle):
        self.x=x
        self.y=y
        self.angle=angle
        self.speed=BULLET_SPEED
        self.radius= 4*BULLET_SCALE
        self.active=True

    def update(self ):
        if  not self.active:
           return 
    
        self.x += math.cos(math.radians(self.angle))*self.speed
        self.y += math.sin(math.radians(self.angle))*self.speed

    def draw(self,game):
        if not self.active:
           return
        if game.player_bullet_texture:
          arcade.draw_texture_rect(
            game.player_bullet_texture,
            arcade.rect.XYWH(
                self.x,
                self.y,
                10,   # width
                20    # height
            ),
            angle=-self.angle + 90
        )
        else:
         arcade.draw_circle_filled(self.x,self.y,self.radius,arcade.color.YELLOW)
    
    def deactive(self):
       self.active=False

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
        self.turn_speed=2
    
    def take_damage(self):
        self.health -=1
        return self.health <=0 

    def update(self,player_x,player_y,delta_time):
       dx = player_x - self.x
       dy = player_y - self.y

       target_angle = math.degrees(math.atan2(dy, dx))

       # shortest angle difference
       diff = (target_angle - self.angle + 180) % 360 - 180

       # rotate gradually
       if diff > 0:
            self.angle += min(self.turn_speed, diff)
       else:
            self.angle += max(-self.turn_speed, diff)

       # move in current facing direction
       self.x += math.cos(math.radians(self.angle)) * self.speed
       self.y += math.sin(math.radians(self.angle)) * self.speed
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


    def draw(self,game):

        if self.enemy_type == "shooter":
          texture = game.Shooter_Enemy_texture
          final_angle = -self.angle+FIRING_ENEMY_SPRITE_ANGLE
          scale=1.4*ENEMY_SCALE  # for firing enemy
        else:
          texture = game.Normal_Enemy_texture
          final_angle = -self.angle+NORMAL_ENEMY_SPRITE_ANGLE  
          scale=ENEMY_SCALE # you can tweak later

    # ✅ Draw sprite if available
        if texture:
        #   final_angle = -self.angle + angle_offset
          game.draw_texture_safe(
            texture,
            self.x,
            self.y,
            scale,
            final_angle
          )

        

        else:
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
        
        self.speed =3
        self.angle=0
        self.radius=150*ENEMY_SCALE*2
        self.health =100
        self.max_health=100
        self.normal_shoot_cooldown=0
        self.big_shoot_cooldown =0
        self.damage_flash_timer=0
        self.flashing= False
        
        self.color=arcade.color.ORANGE

    def take_damage(self):
        self.health -=50
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
            self.normal_shoot_cooldown =1.5
            bullet_x=self.x +\
               math.cos(math.radians(self.angle))*self.radius
            bullet_y=self.y +\
               math.sin(math.radians(self.angle))*self.radius
           
            return BossBullet(bullet_x,bullet_y,self.angle,is_big=False)
        return None
    
    def shoot_big(self):
        if self.big_shoot_cooldown <=0:
            self.big_shoot_cooldown =8.0
            bullet_x=self.x +\
               math.cos(math.radians(self.angle))*self.radius
            bullet_y=self.y +\
               math.sin(math.radians(self.angle))*self.radius
           
            return BossBullet(bullet_x,bullet_y,self.angle,is_big=True)
        return None
    
    def draw(self,game):
        
        texture = game.Boss_texture
        final_angle = -self.angle+180

    # Draw sprite if available
        if texture:
        
          game.draw_texture_safe(
            texture,
            self.x,
            self.y,
            1.5*ENEMY_SCALE,
            final_angle
          )


        else:
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

        bar_x = self.x- bar_width/2
        bar_y = self.y +60

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
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE,resizable=False)
        arcade.set_background_color(arcade.color.BLACK)

        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_angle = 0
        self.player_radius = 150 * PLAYER_SCALE

        self.player_vx = 0
        self.player_vy = 0

        #import the sprits

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        def load_texture_safe(path):
          try:
            texture = arcade.load_texture(path)
            print(f"[OK] Loaded: {path}")
            return texture
          except Exception as e:
            print(f"[ERROR] Failed to load {path} → {e}")
            return None


        # Load  texture safely
        player_path = os.path.join(BASE_DIR, "assets", "images", "Player_ship.png")
        self.player_texture = load_texture_safe(player_path)
        
        Normal_Enemy_path = os.path.join(BASE_DIR, "assets", "images", "Normal_Enemy.png")
        self.Normal_Enemy_texture = load_texture_safe(Normal_Enemy_path)

        shooter_enemy_path = os.path.join(BASE_DIR, "assets", "images", "Firing_enemy2.png")
        self.Shooter_Enemy_texture = load_texture_safe(shooter_enemy_path)

        Boss_enemy_path = os.path.join(BASE_DIR, "assets", "images", "Boss.png")
        self.Boss_texture = load_texture_safe(Boss_enemy_path)

        player_bullet_path = os.path.join(BASE_DIR, "assets", "images", "Player_bullet.png")
        self.player_bullet_texture = load_texture_safe(player_bullet_path)

        enemy_bullet_path = os.path.join(BASE_DIR, "assets", "images", "Enemy_bullet.png")
        self.enemy_bullet_texture = load_texture_safe(enemy_bullet_path)
        
        
        self.bullet_pool=[Bullet() for _ in range (100)]
        self.bullet_index=0
        self.max_bullets=len(self.bullet_pool)
        self.enemies =[]
        self.enemy_bullets = []
        self.boss_bullets =[]
        self.particals =[]
        self.powerups = []
        self.rapid_fire_timer = 0
        self.shield_active = False
        self.shield_timer = 0
        self.boss =None
        self.can_shoot = True
        self.auto_fire = False
        self.shoot_timer = 0.0
        self.enemy_spawn_timer=0 
        self.boss_spawn_timer=1#random.uniform(20,60)
        self.health=100
        self.score=0   
        self.game_over=False
        self.collision_cooldown = 0
        self.boss_warning_timer = 0
        self.boss_hit_cooldown = 0
        self.boss_collision_cooldown = 0
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
        self.boss_warning_text = arcade.Text(
            "⚠ BOSS INCOMING ⚠",20,
            # SCREEN_WIDTH // 2,
            10,
            arcade.color.RED,
            15,
            
            )
    
    def create_explosion(self,x,y,count=PARTICLE_COUNT):
       for _ in range(count):
        self.particals.append(Particle(x,y))
    
    def build_spatial_grid(self):

        grid = {}

        for enemy in self.enemies:

           cell_x = int(enemy.x // CELL_SIZE)
           cell_y = int(enemy.y // CELL_SIZE)

           key = (cell_x, cell_y)

           if key not in grid:
             grid[key] = []

           grid[key].append(enemy)

        return grid

    def restart_game(self):
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_angle = 0

        for bullet in self.bullet_pool:
          bullet.deactive()
        self.enemies.clear()
        self.particals.clear()
        self.powerups.clear()

        self.boss = None
        self.boss_bullets.clear()
        self.boss_spawn_timer =random.uniform(20, 60)

        self.score = 0
        self.health = 100
        self.game_over = False

        self.can_shoot = True
        self.auto_fire = False
        self.shoot_timer = 0
        self.enemy_spawn_timer = 0

        self.score_text.text = "Score: 0"
        self.health_text.text = "Health: 100"

    def draw_texture_safe(self,texture, x, y, scale, angle=0):
        if texture:
            arcade.draw_texture_rect(
                    texture,
                    arcade.rect.XYWH(
                      x,
                      y,
                      texture.width * scale,
                      texture.height * scale
                    ),
                    angle=angle
                )
            
    def on_draw(self):
       self.clear()

       if not self.game_over:
          
          if self.player_texture:
            final_angle=-self.player_angle +SPRITE_ANGLE_OFFSET
            self.draw_texture_safe(
              self.player_texture,
              self.player_x,
              self.player_y,
              PLAYER_SCALE,
              final_angle
            )
          else:
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

          for bullet in self.bullet_pool:
            if bullet.active:
              bullet.draw(self)
        
          for bullet in self.enemy_bullets:
             bullet.draw(self)

          for enemy in self.enemies:
            enemy.draw(self)
            enemy.draw_health_bar()

          self.score_text.draw()
          self.health_text.draw()

          if self.boss:
             self.boss.draw(self)
             self.boss.draw_health_bar()

          if self.boss_warning_timer > 0:
             if self.boss_warning_timer > 0:
               if int(self.boss_warning_timer * 5) % 2 == 0:
                self.boss_warning_text.draw()

          
          if self.shield_active:
              arcade.draw_circle_outline(
              self.player_x,
              self.player_y,
              self.player_radius + 10,
              arcade.color.CYAN,
              1
              )
    

          for bullet in self.boss_bullets:
            bullet.draw()

          for p in self.particals:
            p.draw()

          for p in self.powerups:
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
        self.boss_warning_timer -= delta_time
        self.boss_hit_cooldown -= delta_time
        self.boss_collision_cooldown -= delta_time
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

        
        if self.enemy_spawn_timer <= 0 and len(self.enemies) < MAX_ENEMIES:
           self.enemies.append(Enemy())
           self.enemy_spawn_timer += ENEMY_SPAWN_RATE   

        # spawn boss timer
        

        if self.boss_spawn_timer <= 0 and self.boss is None:
           self.boss = Boss()
           self.boss_warning_timer = 1
        
        if self.boss:

          # boss movement
          self.boss.update(self.player_x, self.player_y, delta_time)

          dx = self.player_x - self.boss.x
          dy = self.player_y - self.boss.y
          distance = math.sqrt(dx*dx + dy*dy)

          if distance < (self.player_radius + self.boss.radius):

              if self.boss_collision_cooldown <= 0:

                  self.boss_collision_cooldown = 0.1

                  if distance == 0:
                    distance = 0.001

                  nx = dx / distance
                  ny = dy / distance

                  overlap = self.player_radius + self.boss.radius - distance

                 # strong separation (no sticking)
                  self.player_x += nx * overlap
                  self.player_y += ny * overlap

                  self.boss.x -= nx * overlap * 0.5
                  self.boss.y -= ny * overlap * 0.5

                # clean push (no physics mess)
                  push_force = 10
                  self.player_vx += nx * push_force
                  self.player_vy += ny * push_force

                # single explosion
                  self.create_explosion(self.player_x, self.player_y, 10)

                # single damage
                  if not self.shield_active:
                    self.health -= 2


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

             cooldown = PLAYER_SHOOT_COOLDOWN

            
             if self.rapid_fire_timer > 0:
                cooldown = 0.05  

             if self.shoot_timer >= cooldown:
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

        if self.rapid_fire_timer > 0:
          self.rapid_fire_timer -= delta_time   

        if self.shield_timer > 0:
           self.shield_timer -= delta_time
        else:
           self.shield_active = False

       
        # Keep player inside screen
        self.player_x = max(self.player_radius, min(SCREEN_WIDTH - self.player_radius, self.player_x))
        self.player_y = max(self.player_radius, min(SCREEN_HEIGHT - self.player_radius, self.player_y))


        for bullet in self.bullet_pool:
            if not bullet.active:
               continue
            bullet.update()
            if bullet.is_off_screen():
               bullet.deactive()

        sorted_enemies = sorted(
        self.enemies,
        key=lambda e: (e.x - self.player_x)**2 + (e.y - self.player_y)**2
        )
        
        for i, enemy in enumerate(sorted_enemies):

          if self.boss or  i < MAX_ATTACKERS:
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

          #shooting
          bullet=enemy.shoot()
          if bullet:
             self.enemy_bullets.append(bullet)

        grid = self.build_spatial_grid()
 
        # add boss into grid
        if self.boss:
            cell_x = int(self.boss.x // CELL_SIZE)
            cell_y = int(self.boss.y // CELL_SIZE)

            key = (cell_x, cell_y)

            if key not in grid:
               grid[key] = []

            grid[key].append(self.boss)
        
        # ____________________SEPARATION (ENEMY + BOSS)__________________________
    
        for enemy in self.enemies:

           cell_x = int(enemy.x // CELL_SIZE)
           cell_y = int(enemy.y // CELL_SIZE)

           for dx in [-1, 0, 1]:
             for dy in [-1, 0, 1]:

               neighbor_key = (cell_x + dx, cell_y + dy)

               if neighbor_key not in grid:
                   continue

               for other in grid[neighbor_key]:

                  if other is enemy:
                    continue

                  dx_ = enemy.x - other.x
                  dy_ = enemy.y - other.y

                  dist_sq = dx_*dx_ + dy_*dy_

                  # safe normalization (fix sticking)
                  if dist_sq < 0.01:
                     nx = random.uniform(-1, 1)
                     ny = random.uniform(-1, 1)
                     dist = 0.01
                  else:
                    dist = math.sqrt(dist_sq)
                    nx = dx_ / dist
                    ny = dy_ / dist

                  min_dist = enemy.radius + getattr(other, "radius", 30)

                  if dist < min_dist:

                    nx = dx_ / dist
                    ny = dy_ / dist

                    push = max((min_dist - dist) * 0.1,1.2)

                    enemy.x += nx * push
                    enemy.y += ny * push
                    # push boss slightly (prevents sticking)
                    if isinstance(other, Boss):
                       other.x -= nx * push * 0.3
                       other.y -= ny * push * 0.3


        if self.boss:
         for enemy in self.enemies:
           dx = enemy.x - self.boss.x
           dy = enemy.y - self.boss.y

           dist_sq = dx*dx + dy*dy
           safe_dist = (self.boss.radius * 1.5) ** 2

           if dist_sq < safe_dist:
              dist = math.sqrt(dist_sq) + 0.001
              nx = dx / dist
              ny = dy / dist

              enemy.x += nx * 2
              enemy.y += ny * 2
        

        for p in self.powerups[:]:
           p.update()

           if p.y < 0:
              self.powerups.remove(p)

        
        for p in self.powerups[:]:

           dx = p.x - self.player_x
           dy = p.y - self.player_y
           distance = math.sqrt(dx*dx + dy*dy)

           if distance < p.radius + self.player_radius:

            if p.type == "rapid_fire":
               self.rapid_fire_timer = 5.0   # 5 seconds

            elif p.type == "shield":
               self.shield_active = True
               self.shield_timer = 5.0

            elif p.type == "Health":
               if self.health <100:
                self.health+=(100-self.health)

            self.powerups.remove(p)


        #______________________________ENEMY-PLAYER COLLISION__________________________________
        for enemy in self.enemies[:]:
           dx = enemy.x - self.player_x
           dy = enemy.y - self.player_y
           distance = (dx*dx + dy*dy)

           if distance < (enemy.radius + self.player_radius)**2:
              if self.collision_cooldown <= 0:
               if not self.shield_active:
                   self.health -= 2
               self.collision_cooldown = 0.5

               self.create_explosion(enemy.x, enemy.y, 10)
               self.enemies.remove(enemy)

           if self.health <= 0:
                self.game_over = True

        
        for bullet in self.boss_bullets[:]:
          bullet.update()

          if bullet.is_off_screen():
            if bullet in self.boss_bullets:
              self.boss_bullets.remove(bullet)
            continue

          distance = math.sqrt(
          (bullet.x - self.player_x)**2 +
          (bullet.y - self.player_y)**2
          )

          if distance < bullet.radius + self.player_radius:

           if self.boss_hit_cooldown <= 0 :
            if not self.shield_active:
              self.health -= bullet.damage
            self.boss_hit_cooldown = 0.3

            self.create_explosion(self.player_x, self.player_y, 6)

           if bullet in self.boss_bullets:
            self.boss_bullets.remove(bullet)
           continue

        if self.health <= 0:
           self.game_over = True


        for bullet in self.enemy_bullets[:]:
          bullet.update()

          if bullet.is_off_screen():
               self.enemy_bullets.remove(bullet)
               continue
        
          distance = math.sqrt(
          (bullet.x - self.player_x)**2 +
          (bullet.y - self.player_y)**2
          )

          if distance < bullet.radius + self.player_radius:
             if not self.shield_active:
                self.health -= 1
             self.enemy_bullets.remove(bullet)
             self.create_explosion(self.player_x, self.player_y, 4)

          if self.health <= 0:
            self.game_over = True

        
        # Limit particles FIRST (outside loop)
        if len(self.particals) > 200:
           self.particals = self.particals[-200:]

        for p in self.particals:
           p.update(delta_time)
           if p.life <= 0:
             if p in self.particals:
               self.particals.remove(p)

        for bullet in self.bullet_pool:
          if not bullet.active:
             continue
          hit=False

          cell_x = int(bullet.x // CELL_SIZE)
          cell_y = int(bullet.y // CELL_SIZE)

          for dx in [-1, 0, 1]:
              
              for dy in [-1, 0, 1]:

                key = (cell_x + dx, cell_y + dy)
                if key not in grid:
                   continue

                for enemy in grid[key]:
                   
                   if enemy is self.boss:
                       continue

                   dx_ = bullet.x - enemy.x
                   dy_ = bullet.y - enemy.y

                   if dx_*dx_ + dy_*dy_ < (bullet.radius + enemy.radius) ** 2:

                       self.create_explosion(bullet.x, bullet.y, 4)
                       enemy.health -= 1
                       bullet.deactive()
                       hit=True

                       if enemy.health <= 0:
                          self.create_explosion(enemy.x, enemy.y, 8)
                          if enemy in self.enemies:
                            self.enemies.remove(enemy)

                          self.score += 10

                          if random.random()<0.8:
                             p_type = random.choice(["rapid_fire", "shield","Health"])
                             self.powerups.append(PowerUp(enemy.x, enemy.y, p_type))
                       break
            
                if hit:
                   break
 
              if hit:
                break
          if hit:
             continue
            
          if  bullet.active and self.boss:   
               dx=(bullet.x - self.boss.x)
               dy=(bullet.y - self.boss.y)
                

               if dx*dx+dy*dy< (bullet.radius + self.boss.radius)**2:
                dead = self.boss.take_damage()
                bullet.deactive()
                hit=True


                if dead:
                 self.create_explosion(self.boss.x, self.boss.y,50)
                 self.score += 500
                 if random.random() < 0.8:
                        offset_x = random.uniform(-30, 30)
                        offset_y = random.uniform(-30, 30)

                        p_type = random.choice(["rapid_fire", "shield","Health"])
                        self.powerups.append(PowerUp(self.boss.x+offset_x, self.boss.y+offset_y, p_type))
                 self.boss = None
                 self.boss_spawn_timer=random.uniform(30,80)
                continue

      
    def shoot(self):
        while self.bullet_pool[self.bullet_index].active:
            self.bullet_index = (self.bullet_index + 1) % self.max_bullets
        bullet = self.bullet_pool[self.bullet_index]

        if bullet.active:
           bullet.deactive()

        bullet.spawn(
        self.player_x + math.cos(math.radians(self.player_angle)) * self.player_radius,
        self.player_y + math.sin(math.radians(self.player_angle)) * self.player_radius,
        self.player_angle
        )

        # move pointer forward (circular)
        self.bullet_index = (self.bullet_index + 1) % self.max_bullets

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