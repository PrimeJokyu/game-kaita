# ring_game.py
import math
import pyxel
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class GameParams:
    # 画面
    W: int = 400
    H: int = 400

    # 玉ねぎ円のパラメータ（デフォルトはあなたの最新指定）
    NUM_LAYERS: int = 12
    BASE_RADIUS: int = 30
    RADIUS_STEP: int = 8
    ANGLE_GAP: float = math.pi / 4
    BASE_SPEED: float = 0.01

    # 物理・コリジョン
    GRAVITY: float = 0.1
    RESTITUTION: float = 1.0
    BALL_RADIUS: int = 3
    RING_THICKNESS: int = 1
    SUBSTEPS: int = 12

    # 初期位置（中心から開始）
    START_X: Optional[int] = None
    START_Y: Optional[int] = None

    # タイトル
    TITLE: str = "Bouncing Ball (Param Game)"

class RingGame:
    def __init__(self, p: GameParams):
        self.p = p
        self.cx = p.W // 2
        self.cy = p.H // 2

        # 角速度：外側ほど僅かに遅い
        self.rot_speeds: List[float] = [p.BASE_SPEED / (1 + i * 0.2) for i in range(p.NUM_LAYERS)]
        self.angles: List[float] = [0.0 for _ in range(p.NUM_LAYERS)]
        self.rings_alive: List[bool] = [True] * p.NUM_LAYERS

        # ボール初期位置
        self.ball_x = float(p.START_X if p.START_X is not None else self.cx)
        self.ball_y = float(p.START_Y if p.START_Y is not None else self.cy)
        self.ball_vx = 0.0
        self.ball_vy = 0.0

        # クリア状態
        self.game_clear = False
        self.clear_time = None

    # ---- 衝突（欠けを通過したら崩壊） ----
    def reflect_on_ring(self, ring_radius: float, gap_start: float, ring_index: int):
        if not self.rings_alive[ring_index]:
            return

        dx = self.ball_x - self.cx
        dy = self.ball_y - self.cy
        r  = math.hypot(dx, dy)
        if r < 1e-6:
            return

        theta = math.atan2(dy, dx) % (2 * math.pi)
        rin  = ring_radius - self.p.RING_THICKNESS / 2.0
        rout = ring_radius + self.p.RING_THICKNESS / 2.0

        # 欠け部分：衝突無効。外へ抜けたら崩壊
        if gap_start <= theta <= gap_start + self.p.ANGLE_GAP:
            if r > rout + self.p.BALL_RADIUS:
                self.rings_alive[ring_index] = False
            return

        # 幅のあるリングとの交差（ボール半径考慮）
        if (r > rin - self.p.BALL_RADIUS) and (r < rout + self.p.BALL_RADIUS):
            nx = dx / r
            ny = dy / r

            # 内外どちらに近いか
            dist_to_inner = abs(r - (rin - self.p.BALL_RADIUS))
            dist_to_outer = abs(r - (rout + self.p.BALL_RADIUS))
            if dist_to_inner < dist_to_outer:
                target_r = rin - self.p.BALL_RADIUS
                nfx, nfy = -nx, -ny  # 内面法線
            else:
                target_r = rout + self.p.BALL_RADIUS
                nfx, nfy = nx, ny    # 外面法線

            # 速度の法線反射
            dot = self.ball_vx * nfx + self.ball_vy * nfy
            self.ball_vx = self.ball_vx - 2.0 * dot * nfx
            self.ball_vy = self.ball_vy - 2.0 * dot * nfy

            # 反発係数（=1.0で永続バウンド）
            self.ball_vx *= self.p.RESTITUTION
            self.ball_vy *= self.p.RESTITUTION

            # めり込み完全解消（すり抜け防止）
            self.ball_x = self.cx + target_r * nx
            self.ball_y = self.cy + target_r * ny

    # ---- 更新 ----
    def update(self):
        if self.game_clear:
            return

        # 回転更新（生存しているリングのみ）
        for i in range(self.p.NUM_LAYERS):
            if self.rings_alive[i]:
                self.angles[i] = (self.angles[i] + self.rot_speeds[i]) % (2 * math.pi)

        # サブステップで物理更新（トンネリング対策）
        for _ in range(self.p.SUBSTEPS):
            self.ball_vy += self.p.GRAVITY / self.p.SUBSTEPS
            self.ball_x  += self.ball_vx / self.p.SUBSTEPS
            self.ball_y  += self.ball_vy / self.p.SUBSTEPS

            for i in range(self.p.NUM_LAYERS):
                radius = self.p.BASE_RADIUS + i * self.p.RADIUS_STEP
                gap_start = self.angles[i]
                self.reflect_on_ring(radius, gap_start, i)

        # クリア判定
        if all(not alive for alive in self.rings_alive):
            self.game_clear = True
            self.clear_time = pyxel.frame_count / 60.0  # 秒

    # ---- 描画 ----
    def draw_ring(self, radius: float, gap_start: float, color: int):
        step_angle = math.pi / 180
        theta = 0.0
        while theta < 2 * math.pi:
            if not (gap_start <= theta <= gap_start + self.p.ANGLE_GAP):
                x = int(self.cx + radius * math.cos(theta))
                y = int(self.cy + radius * math.sin(theta))
                pyxel.pset(x, y, color)
            theta += step_angle

    def draw(self):
        pyxel.cls(0)

        # リング
        for i in range(self.p.NUM_LAYERS):
            if self.rings_alive[i]:
                radius = self.p.BASE_RADIUS + i * self.p.RADIUS_STEP
                self.draw_ring(radius, self.angles[i], 7)

        # ボール
        pyxel.circ(int(self.ball_x), int(self.ball_y), self.p.BALL_RADIUS, 10)

        # クリア表示
        if self.game_clear:
            cx, cy = self.cx, self.cy
            pyxel.text(cx - 20, cy - 10, "CLEAR!", 11)
            pyxel.text(cx - 44, cy + 10, f"Time: {self.clear_time:.2f} sec", 10)

def run_game(**kwargs):
    """
    例:
        run_game(
            NUM_LAYERS=12, BASE_RADIUS=30, RADIUS_STEP=8,
            ANGLE_GAP=math.pi/4, BASE_SPEED=0.01,
            GRAVITY=0.1, RESTITUTION=1.0, BALL_RADIUS=3,
            RING_THICKNESS=1, SUBSTEPS=12, W=400, H=400,
            START_X=None, START_Y=None, TITLE="Param Race!"
        )
    """
    p = GameParams(**kwargs)
    pyxel.init(p.W, p.H, title=p.TITLE)
    game = RingGame(p)
    pyxel.run(game.update, game.draw)