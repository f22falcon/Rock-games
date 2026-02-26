import arcade
import math

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
        self.shoot_cooldown =0

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


    def on_update(self, delta_time):
        
        self.shoot_cooldown -=delta_time

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
            

    def shoot(self):
        if self.shoot_cooldown<=0:
            bullet_x=self.player_x+\
                math.cos(math.radians(self.player_angle))*self.player_radius
            bullet_y=self.player_y+\
                math.sin(math.radians(self.player_angle))*self.player_radius
            self.bullets.append(Bullet(bullet_x,bullet_y,self.player_angle))
            self.shoot_cooldown=PLAYER_SHOOT_COOLDOWN

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
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