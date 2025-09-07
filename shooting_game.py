import pyxel
import random

# Screen dimensions
SCREEN_WIDTH = 256
SCREEN_HEIGHT = 224

# Game constants
BULLET_MAX_COUNT = 10
ENEMY_MAX_COUNT = 15
ENEMY_BULLET_MAX_COUNT = 50
ENEMY_TYPE_A = 0 # 直進
ENEMY_TYPE_B = 1 # 上下動
ENEMY_TYPE_C = 2 # 高速直進 & 十字弾
STATE_TITLE = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2

class Player:
    """Manages the player ship"""
    def __init__(self):
        self.x = 30
        self.y = SCREEN_HEIGHT // 2
        self.w = 16
        self.h = 8
        self.speed = 2
        self.is_alive = True

    def update(self):
        if not self.is_alive:
            return

        if pyxel.btn(pyxel.KEY_A) and self.x > 0:
            self.x -= self.speed
        if pyxel.btn(pyxel.KEY_D) and self.x < SCREEN_WIDTH - self.w:
            self.x += self.speed
        if pyxel.btn(pyxel.KEY_W) and self.y > 0:
            self.y -= self.speed
        if pyxel.btn(pyxel.KEY_S) and self.y < SCREEN_HEIGHT - self.h:
            self.y += self.speed

        if pyxel.btnp(pyxel.KEY_SPACE):
            Bullet(self.x + self.w, self.y + self.h // 2 - 1)
            pyxel.play(3, 9)

    def draw(self):
        if self.is_alive:
            pyxel.blt(self.x, self.y, 0, 0, 0, self.w, self.h, 0)

class Bullet:
    """Manages player's bullets"""
    list = []

    def __init__(self, x, y):
        if len(Bullet.list) < BULLET_MAX_COUNT:
            self.x = x
            self.y = y
            self.w = 4
            self.h = 2
            self.speed = 4
            self.is_alive = True
            Bullet.list.append(self)

    @staticmethod
    def update_all():
        for b in Bullet.list:
            b.x += b.speed
            if b.x > SCREEN_WIDTH:
                b.is_alive = False
        Bullet.list[:] = [b for b in Bullet.list if b.is_alive]

    @staticmethod
    def draw_all():
        for b in Bullet.list:
            pyxel.rect(b.x, b.y, b.w, b.h, 10)

class EnemyBullet:
    """Manages enemy's bullets"""
    list = []
    
    def __init__(self, x, y, angle, speed):
        if len(EnemyBullet.list) < ENEMY_BULLET_MAX_COUNT:
            self.x = x
            self.y = y
            self.w = 4
            self.h = 4
            self.is_alive = True
            
            self.vx = pyxel.cos(angle) * speed
            self.vy = pyxel.sin(angle) * speed
            
            EnemyBullet.list.append(self)

    @staticmethod
    def update_all():
        for b in EnemyBullet.list:
            b.x += b.vx
            b.y += b.vy
            
            if (b.x + b.w < 0 or b.x > SCREEN_WIDTH or
                b.y + b.h < 0 or b.y > SCREEN_HEIGHT):
                b.is_alive = False
        
        EnemyBullet.list[:] = [b for b in EnemyBullet.list if b.is_alive]

    @staticmethod
    def draw_all():
        for b in EnemyBullet.list:
            pyxel.circ(b.x + b.w / 2, b.y + b.h / 2, 2, 8)

class Enemy:
    """Manages enemies"""
    list = []

    def __init__(self, type):
        self.x = SCREEN_WIDTH
        self.y = random.randint(0, SCREEN_HEIGHT - 16)
        self.w = 16
        self.h = 16
        self.type = type
        self.is_alive = True
        
        if self.type == ENEMY_TYPE_A:
            self.speed_x = -1.5
            self.color = 11
        elif self.type == ENEMY_TYPE_B:
            self.speed_x = -1.5
            self.angle = random.randint(0, 360)
            self.speed_y = 2 # ★★ 上下動の幅を大きくする (1 -> 2)
            self.color = 10
        elif self.type == ENEMY_TYPE_C:
            self.speed_x = -2.5
            self.color = 9
            self.has_shot = False
            self.shoot_frame = pyxel.frame_count + random.randint(30, 120)
            
        Enemy.list.append(self)

    def update(self):
        self.x += self.speed_x
        if self.type == ENEMY_TYPE_B:
            self.y += pyxel.sin(self.angle) * self.speed_y
            self.angle = (self.angle + 5) % 360
        
        if self.type == ENEMY_TYPE_A or self.type == ENEMY_TYPE_B:
            if random.randint(0, 100) == 0:
                self.shoot()
        elif self.type == ENEMY_TYPE_C:
            if not self.has_shot and pyxel.frame_count >= self.shoot_frame:
                self.shoot()
                self.has_shot = True
            
        if self.x < -self.w:
            self.is_alive = False
            
    def shoot(self):
        bullet_x = self.x + self.w / 2
        bullet_y = self.y + self.h / 2
        
        if self.type == ENEMY_TYPE_A:
            angle = random.uniform(150, 210)
            speed = 2
            EnemyBullet(bullet_x, bullet_y, angle, speed)
        elif self.type == ENEMY_TYPE_B:
            angle = 180
            speed = 1
            EnemyBullet(bullet_x, bullet_y, angle, speed)
        elif self.type == ENEMY_TYPE_C:
            speed = 2
            EnemyBullet(bullet_x, bullet_y, 0, speed)
            EnemyBullet(bullet_x, bullet_y, 90, speed)
            EnemyBullet(bullet_x, bullet_y, 180, speed)
            EnemyBullet(bullet_x, bullet_y, 270, speed)

    def draw(self):
        if self.is_alive:
            center_x = self.x + self.w / 2
            center_y = self.y + self.h / 2
            pyxel.circ(center_x, center_y, self.w / 2, self.color)

    @staticmethod
    def update_all():
        for e in Enemy.list:
            e.update()
        Enemy.list[:] = [e for e in Enemy.list if e.is_alive]

    @staticmethod
    def draw_all():
        for e in Enemy.list:
            e.draw()

class Explosion:
    """Manages explosion effects"""
    list = []

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 1
        self.is_alive = True
        Explosion.list.append(self)
    
    def update(self):
        self.radius += 1
        if self.radius > 8:
            self.is_alive = False

    def draw(self):
        pyxel.circ(self.x, self.y, self.radius, 8)
        pyxel.circb(self.x, self.y, self.radius, 7)

    @staticmethod
    def update_all():
        for exp in Explosion.list:
            exp.update()
        Explosion.list[:] = [exp for exp in Explosion.list if exp.is_alive]

    @staticmethod
    def draw_all():
        for exp in Explosion.list:
            exp.draw()

class App:
    """Main game application"""
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Gradius Clone", fps=60)
        self.hiscore = 0
        self.setup()
        pyxel.run(self.update, self.draw)

    def setup(self):
        self.game_state = STATE_TITLE
        self.score = 0
        self.player = Player()
        Bullet.list.clear()
        Enemy.list.clear()
        Explosion.list.clear()
        EnemyBullet.list.clear()
        self.create_assets()
        self.create_sounds()
        
        self.start_time = 0
        self.survival_time = 0

    def create_assets(self):
        pyxel.images[0].set(0, 0, ["00c0", "0cc0", "cffc", "ffff", "cffc", "0cc0", "00c0", "0000"])
        # Background creation removed
        
    def create_sounds(self):
        pyxel.sounds[8].set("r a-2 a-2 a-2 a-2", "p", "7", "f", 10)
        pyxel.sounds[9].set("c3e3", "t", "7", "n", 6)

    def update(self):
        if self.game_state == STATE_TITLE:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.game_state = STATE_PLAYING
                self.start_time = pyxel.frame_count
                
        elif self.game_state == STATE_PLAYING:
            self.update_playing()
        elif self.game_state == STATE_GAMEOVER:
            Explosion.update_all()
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.setup()

    def update_playing(self):
        self.survival_time = (pyxel.frame_count - self.start_time) // 60
        
        self.player.update()
        Bullet.update_all()
        Enemy.update_all()
        Explosion.update_all()
        EnemyBullet.update_all()

        if pyxel.frame_count % 30 == 0 and len(Enemy.list) < ENEMY_MAX_COUNT:
            enemy_type = random.choice([ENEMY_TYPE_A, ENEMY_TYPE_B, ENEMY_TYPE_C])
            Enemy(enemy_type)
        
        self.check_collisions()

    def check_collisions(self):
        for e in Enemy.list[:]:
            for b in Bullet.list[:]:
                if (b.x < e.x + e.w and b.x + b.w > e.x and
                    b.y < e.y + e.h and b.y + b.h > e.y):
                    e.is_alive = False
                    b.is_alive = False
                    Explosion(e.x + e.w / 2, e.y + e.h / 2)
                    self.score += 100
                    pyxel.play(3, 8)
                    break

        if self.player.is_alive:
            for b in EnemyBullet.list[:]:
                if (self.player.x < b.x + b.w and self.player.x + self.player.w > b.x and
                    self.player.y < b.y + b.h and self.player.y + self.player.h > b.y):
                    
                    b.is_alive = False
                    self.player.is_alive = False
                    Explosion(self.player.x + self.player.w / 2, self.player.y + self.player.h / 2)
                    self.game_state = STATE_GAMEOVER
                    if self.score > self.hiscore:
                        self.hiscore = self.score
                    pyxel.play(3, 8)
                    break

        if self.player.is_alive:
            for e in Enemy.list:
                if (self.player.x < e.x + e.w and self.player.x + self.player.w > e.x and
                    self.player.y < e.y + e.h and self.player.y + self.player.h > e.y):
                    self.player.is_alive = False
                    Explosion(self.player.x + self.player.w / 2, self.player.y + self.player.h / 2)
                    self.game_state = STATE_GAMEOVER
                    if self.score > self.hiscore:
                        self.hiscore = self.score
                    pyxel.play(3, 8)
                    break

    def draw(self):
        pyxel.cls(0)
        # Background drawing removed
        
        if self.game_state == STATE_TITLE:
            pyxel.text(SCREEN_WIDTH//2 - 30, SCREEN_HEIGHT//2 - 20, "GRADIUS CLONE", 7)
            pyxel.text(SCREEN_WIDTH//2 - 40, SCREEN_HEIGHT//2, "PRESS ENTER", pyxel.frame_count % 16)
        
        elif self.game_state in (STATE_PLAYING, STATE_GAMEOVER):
            self.player.draw()
            Bullet.draw_all()
            Enemy.draw_all()
            Explosion.draw_all()
            EnemyBullet.draw_all()
            
            score_text = f"SCORE {self.score:05}"
            hiscore_text = f"HI-SCORE {self.hiscore:05}"
            pyxel.text(5, 4, score_text, 7)
            pyxel.text(SCREEN_WIDTH - len(hiscore_text) * 4 - 5, 4, hiscore_text, 7)
            
            time_text = f"TIME {self.survival_time:03}"
            pyxel.text(5, 12, time_text, 7)
            
            if self.game_state == STATE_GAMEOVER:
                pyxel.text(SCREEN_WIDTH//2 - 24, SCREEN_HEIGHT//2, "GAME OVER", 8)

if __name__ == "__main__":
    App()