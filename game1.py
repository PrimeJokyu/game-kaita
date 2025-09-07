# main.py
import math
from ring_game import run_game

# ▼ここを小学生が手で変える！
PARAMS = dict(
    # 画面
    W=400, H=400, TITLE="Param Race!",

    # 玉ねぎ円
    NUM_LAYERS=12,      # 推奨: 6〜16
    BASE_RADIUS=30,     # 推奨: 20〜40
    RADIUS_STEP=8,      # 推奨: 4〜12（間隔が広いほど易しい）
    ANGLE_GAP=math.pi/4,# 推奨: pi/12〜pi/2（大きいほど易しい）
    BASE_SPEED=0.01,    # 推奨: 0.005〜0.03（大きいほど難しい：回転が速い）

    # 物理
    GRAVITY=0.1,        # 推奨: 0.05〜0.2（重力が強いと時間短縮しやすいが難しくもなる）
    RESTITUTION=1.0,    # 1.0 固定（永遠バウンド）
    BALL_RADIUS=3,      # 推奨: 2〜5（小さいほど通れそうな隙間が増え難しい）
    RING_THICKNESS=1,   # 推奨: 1〜3（厚いほど当たりやすく難しい）
    SUBSTEPS=12,        # 推奨: 10〜20（大きいほどすり抜けにくい）

    # 初期位置（None で画面中心）
    START_X=None,
    START_Y=None,
)

if __name__ == "__main__":
    run_game(**PARAMS)