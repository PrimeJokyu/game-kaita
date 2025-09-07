import pyxel

pyxel.init(160, 120, title="アニメーション")

# アニメーションフレームの作成
pyxel.image(0).load(0, 0, "assets/character_walk.png")

character_x = 80
character_y = 60
frame = 0

def update():
    global character_x, frame
    
    if pyxel.btn(pyxel.KEY_RIGHT):
        character_x = min(character_x + 2, 152)
        frame = (frame + 1) % 4
    elif pyxel.btn(pyxel.KEY_LEFT):
        character_x = max(character_x - 2, 0)
        frame = (frame + 1) % 4
    else:
        frame = 0
    
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

def draw():
    pyxel.cls(0)
    pyxel.blt(character_x, character_y, 0, frame * 8, 0, 30, 30, 0)

pyxel.run(update, draw)
