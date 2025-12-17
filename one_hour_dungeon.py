import pygame
import sys
import random
import json
import os
from pygame.locals import *

# 定義顏色
WHITE = (255, 255, 255)
BLACK = (  0,   0,   0)
RED   = (255,   0,   0)
CYAN  = (  0, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BLINK = [(224,255,255), (192,240,255), (128,224,255), (64,192,255), (128,224,255), (192,240,255)]

# 載入圖片
imgTitle = pygame.image.load("image/title.png")
imgWall = pygame.image.load("image/wall.png")
imgWall2 = pygame.image.load("image/wall2.png")
imgDark = pygame.image.load("image/dark.png")
imgPara = pygame.image.load("image/parameter.png")
imgBtlBG = pygame.image.load("image/btlbg.png")
imgEnemy = pygame.image.load("image/enemy0.png")
imgItem = [
    pygame.image.load("image/potion.png"),
    pygame.image.load("image/blaze_gem.png"),
    pygame.image.load("image/spoiled.png"),
    pygame.image.load("image/apple.png"),
    pygame.image.load("image/meat.png")
]
imgFloor = [
    pygame.image.load("image/floor.png"),
    pygame.image.load("image/tbox.png"),
    pygame.image.load("image/cocoon.png"),
    pygame.image.load("image/stairs.png")
]
imgPlayer = [
    pygame.image.load("image/mychr0.png"),
    pygame.image.load("image/mychr1.png"),
    pygame.image.load("image/mychr2.png"),
    pygame.image.load("image/mychr3.png"),
    pygame.image.load("image/mychr4.png"),
    pygame.image.load("image/mychr5.png"),
    pygame.image.load("image/mychr6.png"),
    pygame.image.load("image/mychr7.png"),
    pygame.image.load("image/mychr8.png")
]
imgEffect = [
    pygame.image.load("image/effect_a.png"),
    pygame.image.load("image/effect_b.png")
]

# 宣告變數
speed = 1
idx = 0
tmr = 0
floor = 0
fl_max = 1
welcome = 0

pl_x = 0
pl_y = 0
pl_d = 0
pl_a = 0
pl_lifemax = 0
pl_life = 0
pl_str = 0
food = 0
potion = 0
blazegem = 0
treasure = 0

emy_name = ""
emy_lifemax = 0
emy_life = 0
emy_str = 0
emy_x = 0
emy_y = 0
emy_step = 0
emy_blink = 0

dmg_eff = 0
btl_cmd = 0

# 遊戲統計
kill_count = 0
game_start_time = 0
game_end_time = 0

# 難度設定 (1=簡單, 2=普通, 3=困難)
difficulty = 2
difficulty_names = ["簡單", "普通", "困難"]

# 連擊系統
combo_count = 0
last_kill_time = 0

# 成就系統
achievements = {
    "floor_5": False,
    "floor_10": False,
    "kill_10": False,
    "kill_50": False,
    "explore_80": False
}
achievement_popup = None
achievement_timer = 0

# 暫停狀態
pause_sel = 0
pause_return_idx = 0

# 標題選單
title_sel = 0  # 0=新遊戲, 1=選擇難度, 2=繼續遊戲
difficulty_sel = 1  # 0=簡單, 1=普通, 2=困難
show_difficulty_menu = False

# 設定
settings = {
    "bgm_volume": 0.5,
    "se_volume": 0.7,
    "fullscreen": True
}
settings_sel = 0  # 0=BGM, 1=SE, 2=全螢幕, 3=返回

# 存檔/讀檔
save_file = "save.json"

# 傷害浮字
damage_floaters = []  # [{x, y, text, color, timer, dy}]

COMMAND = ["[A] 攻擊", "[P] 藥水", "[B] 火焰寶石", "[R] 逃跑"]
TRE_NAME = ["藥水", "火焰寶石", "食物腐壞了", "食物 +20", "食物 +100", "治療泉水！HP全回復", "詛咒祭壇...攻擊-20%", "幸運寶箱！大豐收"]
# 隨機事件名稱
EVENT_NAME = ["治療泉水", "詛咒祭壇", "幸運寶箱"]
EMY_NAME = [
    "綠色史萊姆", "紅色史萊姆", "斧獸", "食人魔", "劍士",
    "死亡黃蜂", "信號史萊姆", "惡魔植物", "雙刀殺手", "地獄魔王"
]

MAZE_W = 11
MAZE_H = 9
maze = []
for y in range(MAZE_H):
    maze.append([0]*MAZE_W)

DUNGEON_W = MAZE_W*3
DUNGEON_H = MAZE_H*3
dungeon = []
for y in range(DUNGEON_H):
    dungeon.append([0]*DUNGEON_W)

# 迷你地圖：已探索標記
seen = []
for y in range(DUNGEON_H):
    seen.append([0]*DUNGEON_W)

def make_dungeon(): # 自動產生地下城
    global seen
    XP = [ 0, 1, 0,-1]
    YP = [-1, 0, 1, 0]
    #周圍的牆壁
    for x in range(MAZE_W):
        maze[0][x] = 1
        maze[MAZE_H-1][x] = 1
    for y in range(1, MAZE_H-1):
        maze[y][0] = 1
        maze[y][MAZE_W-1] = 1
    #地下城一片空白的狀態
    for y in range(1, MAZE_H-1):
        for x in range(1, MAZE_W-1):
            maze[y][x] = 0
    #柱子
    for y in range(2, MAZE_H-2, 2):
        for x in range(2, MAZE_W-2, 2):
            maze[y][x] = 1
    #從柱子的上下左右延伸出牆壁
    for y in range(2, MAZE_H-2, 2):
        for x in range(2, MAZE_W-2, 2):
         d = random.randint(0, 3)
         if x > 2: # 自第二欄的柱子之後，不在左側建立牆壁
             d = random.randint(0, 2)
         maze[y+YP[d]][x+XP[d]] = 1

    # 根據迷宮建立地下城
    #將地下城的所有空間設定為牆壁
    for y in range(DUNGEON_H):
        for x in range(DUNGEON_W):
            dungeon[y][x] = 9
            seen[y][x] = 0
    #配置房間與通道
    for y in range(1, MAZE_H-1):
        for x in range(1, MAZE_W-1):
            dx = x*3+1
            dy = y*3+1
            if maze[y][x] == 0:
                if random.randint(0, 99) < 20: # 建立房間
                    for ry in range(-1, 2):
                        for rx in range(-1, 2):
                            dungeon[dy+ry][dx+rx] = 0
                else: # 建立通道
                    dungeon[dy][dx] = 0
                    if maze[y-1][x] == 0: dungeon[dy-1][dx] = 0
                    if maze[y+1][x] == 0: dungeon[dy+1][dx] = 0
                    if maze[y][x-1] == 0: dungeon[dy][dx-1] = 0
                    if maze[y][x+1] == 0: dungeon[dy][dx+1] = 0

def draw_dungeon(bg, fnt): # 繪製地下城
    global seen
    bg.fill(BLACK)
    for y in range(-4, 6):
        for x in range(-5, 6):
            X = (x+5)*80
            Y = (y+4)*80
            dx = pl_x + x
            dy = pl_y + y
            if 0 <= dx and dx < DUNGEON_W and 0 <= dy and dy < DUNGEON_H:
                # 標記可見區域為已探索
                seen[dy][dx] = 1
                if dungeon[dy][dx] <= 3:
                    bg.blit(imgFloor[dungeon[dy][dx]], [X, Y])
                if dungeon[dy][dx] == 9:
                    bg.blit(imgWall, [X, Y-40])
                    if dy >= 1 and dungeon[dy-1][dx] == 9:
                        bg.blit(imgWall2, [X, Y-80])
            if x == 0 and y == 0: # 顯示主角
                bg.blit(imgPlayer[pl_a], [X, Y-40])
    bg.blit(imgDark, [0, 0]) # 在四個角落配置暗沉的圖片
    draw_para(bg, fnt) # 顯示主角的能力

def put_event(): # 於地板配置道具
    global pl_x, pl_y, pl_d, pl_a
    # 配置樓梯
    while True:
        x = random.randint(3, DUNGEON_W-4)
        y = random.randint(3, DUNGEON_H-4)
        if(dungeon[y][x] == 0):
            for ry in range(-1, 2): # 將樓梯周圍的空間設定為地板
                for rx in range(-1, 2):
                    dungeon[y+ry][x+rx] = 0
            dungeon[y][x] = 3
            break
    # 配置寶箱與繭
    for i in range(60):
        x = random.randint(3, DUNGEON_W-4)
        y = random.randint(3, DUNGEON_H-4)
        if(dungeon[y][x] == 0):
            dungeon[y][x] = random.choice([1,2,2,2,2])
    # 配置特殊事件房間 (4=治療泉, 5=詛咒祭壇, 6=幸運寶箱)
    for i in range(3):
        x = random.randint(3, DUNGEON_W-4)
        y = random.randint(3, DUNGEON_H-4)
        if(dungeon[y][x] == 0):
            dungeon[y][x] = 4 + i  # 4, 5, 6
    # 玩家的初始位置
    while True:
        pl_x = random.randint(3, DUNGEON_W-4)
        pl_y = random.randint(3, DUNGEON_H-4)
        if(dungeon[pl_y][pl_x] == 0):
            break
    pl_d = 1
    pl_a = 2
                
def move_player(key): # 主角的移動
    global idx, tmr, pl_x, pl_y, pl_d, pl_a, pl_life, food, potion, blazegem, treasure, pl_lifemax, pl_str

    if dungeon[pl_y][pl_x] == 1: # 走到寶箱的位置
        dungeon[pl_y][pl_x] = 0
        treasure = random.choice([0,0,0,1,1,1,1,1,1,2])
        if treasure == 0:
            potion = potion + 1
        if treasure == 1:
            blazegem = blazegem + 1
        if treasure == 2:
            food = int(food/2)
        idx = 3
        tmr = 0
        return
    if dungeon[pl_y][pl_x] == 2: # 走到繭的位置
        dungeon[pl_y][pl_x] = 0
        r = random.randint(0, 99)
        if r < 40: # 食物
            treasure = random.choice([3,3,3,4])
            if treasure == 3: food = food + 20
            if treasure == 4: food = food + 100
            idx = 3
            tmr = 0
        else: # 敵人出現
            idx = 10
            tmr = 0
        return
    if dungeon[pl_y][pl_x] == 3: # 走到樓梯的位置
        idx = 2
        tmr = 0
        return
    # 特殊事件房間
    if dungeon[pl_y][pl_x] == 4: # 治療泉水
        dungeon[pl_y][pl_x] = 0
        pl_life = pl_lifemax
        food = min(999, food + 50)
        treasure = 5  # 特殊顯示
        idx = 3
        tmr = 0
        return
    if dungeon[pl_y][pl_x] == 5: # 詛咒祭壇
        dungeon[pl_y][pl_x] = 0
        pl_str = int(pl_str * 0.8)  # 降低20%攻擊力
        potion += 2  # 但獲得2瓶藥水
        treasure = 6  # 特殊顯示
        idx = 3
        tmr = 0
        return
    if dungeon[pl_y][pl_x] == 6: # 幸運寶箱
        dungeon[pl_y][pl_x] = 0
        potion += 2
        blazegem += 1
        food += 50
        treasure = 7  # 特殊顯示
        idx = 3
        tmr = 0
        return

    # 以方向鍵上下左右移動
    x = pl_x
    y = pl_y
    if key[K_UP] == 1:
        pl_d = 0
        if dungeon[pl_y-1][pl_x] != 9:
            pl_y = pl_y - 1
    if key[K_DOWN] == 1:
        pl_d = 1
        if dungeon[pl_y+1][pl_x] != 9:
            pl_y = pl_y + 1
    if key[K_LEFT] == 1:
        pl_d = 2
        if dungeon[pl_y][pl_x-1] != 9:
            pl_x = pl_x - 1
    if key[K_RIGHT] == 1:
        pl_d = 3
        if dungeon[pl_y][pl_x+1] != 9:
            pl_x = pl_x + 1
    pl_a = pl_d*2
    if pl_x != x or pl_y != y: # 移動時，計算食物的存量與體力
        pl_a = pl_a + tmr%2 # 移動時的原地踏步動畫
        if food > 0:
            food = food - 1
            if pl_life < pl_lifemax:
                pl_life = pl_life + 1
        else:
            pl_life = pl_life - 5
            if pl_life <= 0:
                pl_life = 0
                pygame.mixer.music.stop()
                idx = 9
                tmr = 0

def draw_text(bg, txt, x, y, fnt, col): # 顯示套用陰影效果的文字
    sur = fnt.render(txt, True, BLACK)
    bg.blit(sur, [x+1, y+2])
    sur = fnt.render(txt, True, col)
    bg.blit(sur, [x, y])

def draw_para(bg, fnt): # 顯示主角的能力
    X = 30
    Y = 600
    bg.blit(imgPara, [X, Y])
    col = WHITE
    if pl_life < 10 and tmr%2 == 0: col = RED
    draw_text(bg, "{}/{}".format(pl_life, pl_lifemax), X+128, Y+6, fnt, col)
    draw_text(bg, str(pl_str), X+128, Y+33, fnt, WHITE)
    col = WHITE
    if food == 0 and tmr%2 == 0: col = RED
    draw_text(bg, str(food), X+128, Y+60, fnt, col)
    draw_text(bg, str(potion), X+266, Y+6, fnt, WHITE)
    draw_text(bg, str(blazegem), X+266, Y+33, fnt, WHITE)

def draw_stats(bg, fnt): # 顯示遊戲統計
    # 計算探索率
    explored = sum(row.count(1) for row in seen)
    total_tiles = DUNGEON_W * DUNGEON_H
    explore_rate = int(explored / total_tiles * 100)
    
    # 計算遊戲時間
    elapsed = (pygame.time.get_ticks() - game_start_time) // 1000
    minutes = elapsed // 60
    seconds = elapsed % 60
    
    # 顯示統計資訊（右上角，移到速度顯示下方）
    stats_x = 680
    stats_y = 80
    draw_text(bg, f"擊殺: {kill_count}", stats_x, stats_y, fnt, CYAN)
    draw_text(bg, f"探索: {explore_rate}%", stats_x, stats_y + 30, fnt, CYAN)
    draw_text(bg, f"時間: {minutes:02d}:{seconds:02d}", stats_x, stats_y + 60, fnt, CYAN)

def init_battle(): # 準備進入戰鬥
    global imgEnemy, emy_name, emy_lifemax, emy_life, emy_str, emy_x, emy_y, difficulty
    typ = random.randint(0, floor)
    if floor >= 10:
        typ = random.randint(0, 9)
    lev = random.randint(1, floor)
    imgEnemy = pygame.image.load("image/enemy"+str(typ)+".png")
    emy_name = EMY_NAME[typ] + " LV" + str(lev)
    # 根據難度調整敵人數值
    difficulty_multiplier = [0.7, 1.0, 1.4][difficulty]  # 簡單/普通/困難
    emy_lifemax = int((50*(typ+1) + (lev-1)*8) * difficulty_multiplier)
    emy_life = emy_lifemax
    emy_str = int(emy_lifemax/10)
    emy_x = 440-imgEnemy.get_width()/2
    emy_y = 560-imgEnemy.get_height()

def draw_bar(bg, x, y, w, h, val, max): # 敵人體力條
    pygame.draw.rect(bg, WHITE, [x-2, y-2, w+4, h+4])
    pygame.draw.rect(bg, BLACK, [x, y, w, h])
    if val > 0:
        pygame.draw.rect(bg, (0,128,255), [x, y, w*val/max, h])

def draw_battle(bg, fnt): # 繪製戰鬥畫面
    global emy_blink, dmg_eff
    bx = 0
    by = 0
    if dmg_eff > 0:
        dmg_eff = dmg_eff - 1
        bx = random.randint(-20, 20)
        by = random.randint(-10, 10)
    bg.blit(imgBtlBG, [bx, by])
    if emy_life > 0 and emy_blink%2 == 0:
        bg.blit(imgEnemy, [emy_x, emy_y+emy_step])
    draw_bar(bg, 340, 580, 200, 10, emy_life, emy_lifemax)
    # 顯示敵人生命值數字
    hp_text = f"{emy_life}/{emy_lifemax}"
    hp_surface = fnt.render(hp_text, True, WHITE)
    hp_x = 440 - hp_surface.get_width() // 2  # 置中顯示
    draw_text(bg, hp_text, hp_x, 595, fnt, WHITE)
    if emy_blink > 0:
        emy_blink = emy_blink - 1
    for i in range(10): # 顯示戰鬥訊息（移到左側）
        draw_text(bg, message[i], 40, 100+i*50, fnt, WHITE)
    # 更新並繪製傷害浮字
    update_damage_floaters()
    draw_damage_floaters(bg, fnt)
    draw_para(bg, fnt) # 顯示主角能力
    # 顯示連擊數
    if combo_count > 1:
        draw_text(bg, f"連擊 x{combo_count}", 700, 100, fnt, ORANGE)
    # 顯示成就通知
    draw_achievement_popup(bg, fnt)

def battle_command(bg, fnt, key): # 輸入與顯示指令
    global btl_cmd
    ent = False
    if key[K_a]: # A鍵
        btl_cmd = 0
        ent = True
    if key[K_p]: # P鍵
        btl_cmd = 1
        ent = True
    if key[K_b]: # B鍵
        btl_cmd = 2
        ent = True
    if key[K_r]: # R鍵
        btl_cmd = 3
        ent = True
    if key[K_UP] and btl_cmd > 0: #↑鍵
        btl_cmd -= 1
    if key[K_DOWN] and btl_cmd < 3: #↓鍵
        btl_cmd += 1
    if key[K_SPACE] or key[K_RETURN]:
        ent = True
    for i in range(4):
        c = WHITE
        if btl_cmd == i: c = BLINK[tmr%6]
        # 將指令列表移到右側，避免與左側訊息重疊
        draw_text(bg, COMMAND[i], 600, 360+i*60, fnt, c)
    return ent

# 設定管理
def load_settings():
    global settings
    if os.path.exists("settings.json"):
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                loaded = json.load(f)
                settings.update(loaded)
        except:
            pass

def save_settings():
    try:
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except:
        pass

def apply_settings():
    pygame.mixer.music.set_volume(settings["bgm_volume"])
    # SE音量會在播放時套用

# 存檔/讀檔
def save_game():
    global floor, fl_max, pl_x, pl_y, pl_d, pl_a, pl_lifemax, pl_life, pl_str, food, potion, blazegem, kill_count, game_start_time, game_end_time, difficulty, achievements
    data = {
        "floor": floor,
        "fl_max": fl_max,
        "pl_x": pl_x,
        "pl_y": pl_y,
        "pl_d": pl_d,
        "pl_a": pl_a,
        "pl_lifemax": pl_lifemax,
        "pl_life": pl_life,
        "pl_str": pl_str,
        "food": food,
        "potion": potion,
        "blazegem": blazegem,
        "dungeon": dungeon,
        "seen": seen,
        "kill_count": kill_count,
        "game_start_time": game_start_time,
        "game_end_time": game_end_time,
        "difficulty": difficulty,
        "achievements": achievements
    }
    try:
        with open(save_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

def load_game():
    global floor, fl_max, pl_x, pl_y, pl_d, pl_a, pl_lifemax, pl_life, pl_str, food, potion, blazegem, dungeon, seen, kill_count, game_start_time, game_end_time, difficulty, achievements
    if not os.path.exists(save_file):
        return False
    try:
        with open(save_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        floor = data["floor"]
        fl_max = data["fl_max"]
        pl_x = data["pl_x"]
        pl_y = data["pl_y"]
        pl_d = data["pl_d"]
        pl_a = data["pl_a"]
        pl_lifemax = data["pl_lifemax"]
        pl_life = data["pl_life"]
        pl_str = data["pl_str"]
        food = data["food"]
        potion = data["potion"]
        blazegem = data["blazegem"]
        dungeon = data["dungeon"]
        seen = data.get("seen", [[0]*DUNGEON_W for _ in range(DUNGEON_H)])
        kill_count = data.get("kill_count", 0)
        game_start_time = data.get("game_start_time", pygame.time.get_ticks())
        game_end_time = data.get("game_end_time", 0)
        difficulty = data.get("difficulty", 2)
        achievements = data.get("achievements", {
            "floor_5": False,
            "floor_10": False,
            "kill_10": False,
            "kill_50": False,
            "explore_80": False
        })
        return True
    except:
        return False

# 傷害浮字
def add_damage_floater(x, y, damage, is_critical=False):
    global damage_floaters
    color = ORANGE if is_critical else WHITE
    text = str(damage) + ("!" if is_critical else "")
    damage_floaters.append({
        "x": x,
        "y": y,
        "text": text,
        "color": color,
        "timer": 30,
        "dy": 0
    })

def update_damage_floaters():
    global damage_floaters
    for floater in damage_floaters[:]:
        floater["timer"] -= 1
        floater["dy"] -= 2
        if floater["timer"] <= 0:
            damage_floaters.remove(floater)

def draw_damage_floaters(bg, fnt):
    for floater in damage_floaters:
        alpha = int(255 * (floater["timer"] / 30))
        col = floater["color"]
        draw_text(bg, floater["text"], int(floater["x"]), int(floater["y"] + floater["dy"]), fnt, col)

# 成就系統
def check_achievement(achievement_id, title, description):
    global achievements, achievement_popup, achievement_timer
    if not achievements[achievement_id]:
        achievements[achievement_id] = True
        achievement_popup = {"title": title, "desc": description}
        achievement_timer = 180  # 顯示3秒

def draw_achievement_popup(bg, fnt):
    global achievement_timer
    if achievement_popup and achievement_timer > 0:
        achievement_timer -= 1
        alpha = min(255, achievement_timer * 3) if achievement_timer < 85 else 255
        
        # 成就通知框
        box_w, box_h = 400, 120
        box_x = (880 - box_w) // 2
        box_y = 50
        
        # 背景
        pygame.draw.rect(bg, (40, 40, 40), [box_x, box_y, box_w, box_h])
        pygame.draw.rect(bg, YELLOW, [box_x, box_y, box_w, box_h], 3)
        
        # 標題
        draw_text(bg, "成就解鎖！", box_x + 20, box_y + 15, fnt, YELLOW)
        draw_text(bg, achievement_popup["title"], box_x + 20, box_y + 50, fnt, WHITE)
        draw_text(bg, achievement_popup["desc"], box_x + 20, box_y + 85, fnt, CYAN)

# 顯示戰鬥訊息的處理
message = [""]*10
def init_message():
    for i in range(10):
        message[i] = ""
    
def set_message(msg):
    for i in range(10):
        if message[i] == "":
            message[i] = msg
            return
    for i in range(9):
        message[i] = message[i+1]
    message[9] = msg

def draw_minimap(bg, x0=None, y0=None): # 迷你地圖（可指定位置）
    # 設定每格像素大小
    cell = 4
    mm_w = DUNGEON_W * cell
    mm_h = DUNGEON_H * cell
    margin = 20
    # 預設畫在右上角；若指定則使用指定位置
    if x0 is None:
        x0 = 880 - mm_w - margin
    if y0 is None:
        y0 = margin
    # 背景與邊框
    pygame.draw.rect(bg, (20,20,20), [x0-4, y0-4, mm_w+8, mm_h+8])
    pygame.draw.rect(bg, WHITE, [x0-4, y0-4, mm_w+8, mm_h+8], 2)
    # 各種類型顏色
    for y in range(DUNGEON_H):
        for x in range(DUNGEON_W):
            if seen[y][x]:
                v = dungeon[y][x]
                col = (60,60,60) # 牆預設深灰
                if v == 9:
                    col = (60,60,60)
                elif v == 0:
                    col = (180,180,180)
                elif v == 1:
                    col = (255,215,0) # 寶箱 金色
                elif v == 2:
                    col = (0,200,100) # 繭 綠色
                elif v == 3:
                    col = (0,180,255) # 樓梯 青色
                px = x0 + x*cell
                py = y0 + y*cell
                pygame.draw.rect(bg, col, [px, py, cell, cell])
    # 玩家位置高亮
    px = x0 + pl_x*cell
    py = y0 + pl_y*cell
    pygame.draw.rect(bg, (255,80,80), [px, py, cell, cell])

def main(): # 主要處理
    global speed, idx, tmr, floor, fl_max, welcome
    global pl_a, pl_lifemax, pl_life, pl_str, food, potion, blazegem
    global emy_life, emy_step, emy_blink, dmg_eff
    global settings, settings_sel, pause_sel, pause_return_idx, title_sel
    global kill_count, game_start_time, game_end_time, difficulty, difficulty_sel, show_difficulty_menu
    global combo_count, last_kill_time, achievements, achievement_popup, achievement_timer
    dmg = 0
    lif_p = 0
    str_p = 0
    is_critical = False
    
    # 載入設定
    load_settings()

    pygame.init()
    pygame.display.set_caption("一小時地下城")
    # 建立遊戲畫面 880x720
    game_width, game_height = 880, 720
    # 獲取全螢幕解析度
    display_info = pygame.display.Info()
    window_width, window_height = display_info.current_w, display_info.current_h
    screen = pygame.display.set_mode((window_width, window_height), pygame.FULLSCREEN)
    # 建立虛擬表面用於遊戲渲染
    game_surface = pygame.Surface((game_width, game_height))
    # 計算置中位置
    offset_x = (window_width - game_width) // 2
    offset_y = (window_height - game_height) // 2
    clock = pygame.time.Clock()
    font = pygame.font.Font("font/guin.ttc", 40)
    fontS = pygame.font.Font("font/guin.ttc", 30)

    se = [ # 音效
        pygame.mixer.Sound("sound/ohd_se_attack.ogg"),
        pygame.mixer.Sound("sound/ohd_se_blaze.ogg"),
        pygame.mixer.Sound("sound/ohd_se_potion.ogg"),
        pygame.mixer.Sound("sound/ohd_jin_gameover.ogg"),
        pygame.mixer.Sound("sound/ohd_jin_levup.ogg"),
        pygame.mixer.Sound("sound/ohd_jin_win.ogg")
    ]
    
    # 套用音效音量
    def play_se(idx):
        se[idx].set_volume(settings["se_volume"])
        se[idx].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_s:
                    speed = speed + 1
                    if speed == 4:
                        speed = 1
                # ESC 鍵切換暫停
                if event.key == K_ESCAPE:
                    if idx != 90:
                        pause_return_idx = idx
                        idx = 90
                        pause_sel = 0
                        tmr = 0
                    else:
                        idx = pause_return_idx
                        tmr = 0
                # 暫停介面鍵盤操作（使用 KEYDOWN 避免重複連發）
                if idx == 90:
                    if event.key == K_UP and pause_sel > 0:
                        pause_sel -= 1
                    if event.key == K_DOWN and pause_sel < 3:
                        pause_sel += 1
                    if event.key in (K_RETURN, K_SPACE):
                        if pause_sel == 0: # 繼續
                            idx = pause_return_idx
                            tmr = 0
                        elif pause_sel == 1: # 存檔
                            if save_game():
                                set_message("已存檔")
                        elif pause_sel == 2: # 設定
                            idx = 91
                            settings_sel = 0
                            tmr = 0
                        else: # 退出
                            pygame.quit()
                            sys.exit()
                # 設定介面鍵盤操作
                if idx == 91:
                    if event.key == K_UP and settings_sel > 0:
                        settings_sel -= 1
                    if event.key == K_DOWN and settings_sel < 3:
                        settings_sel += 1
                    if event.key == K_LEFT:
                        if settings_sel == 0 and settings["bgm_volume"] > 0:
                            settings["bgm_volume"] = max(0, settings["bgm_volume"] - 0.1)
                            apply_settings()
                        elif settings_sel == 1 and settings["se_volume"] > 0:
                            settings["se_volume"] = max(0, settings["se_volume"] - 0.1)
                    if event.key == K_RIGHT:
                        if settings_sel == 0 and settings["bgm_volume"] < 1:
                            settings["bgm_volume"] = min(1, settings["bgm_volume"] + 0.1)
                            apply_settings()
                        elif settings_sel == 1 and settings["se_volume"] < 1:
                            settings["se_volume"] = min(1, settings["se_volume"] + 0.1)
                    if event.key in (K_RETURN, K_SPACE):
                        if settings_sel == 2: # 切換全螢幕
                            settings["fullscreen"] = not settings["fullscreen"]
                            # 重建視窗
                            if settings["fullscreen"]:
                                screen = pygame.display.set_mode((window_width, window_height), pygame.FULLSCREEN)
                                offset_x = (window_width - game_width) // 2
                                offset_y = (window_height - game_height) // 2
                            else:
                                screen = pygame.display.set_mode((game_width, game_height))
                                offset_x = 0
                                offset_y = 0
                        elif settings_sel == 3: # 返回
                            save_settings()
                            idx = 90
                            tmr = 0
                    if event.key == K_ESCAPE:
                        save_settings()
                        idx = 90
                        tmr = 0
                # 標題選單鍵盤操作
                if idx == 0:
                    if show_difficulty_menu:
                        # 難度選擇介面
                        if event.key == K_LEFT and difficulty_sel > 0:
                            difficulty_sel -= 1
                        if event.key == K_RIGHT and difficulty_sel < 2:
                            difficulty_sel += 1
                        if event.key in (K_RETURN, K_SPACE):
                            difficulty = difficulty_sel
                            show_difficulty_menu = False
                        if event.key == K_ESCAPE:
                            show_difficulty_menu = False
                    else:
                        # 主選單
                        if event.key == K_UP:
                            title_sel = (title_sel - 1) % 3
                        if event.key == K_DOWN:
                            title_sel = (title_sel + 1) % 3
                        if event.key in (K_RETURN, K_SPACE):
                            if title_sel == 0:  # 開始新遊戲
                                make_dungeon()
                                put_event()
                                floor = 1
                                welcome = 15
                                pl_lifemax = 300
                                pl_life = pl_lifemax
                                pl_str = 100
                                food = 300
                                potion = 0
                                blazegem = 0
                                kill_count = 0
                                combo_count = 0
                                game_start_time = pygame.time.get_ticks()
                                game_end_time = 0
                                achievements = {
                                    "floor_5": False,
                                    "floor_10": False,
                                    "kill_10": False,
                                    "kill_50": False,
                                    "explore_80": False
                                }
                                idx = 1
                                pygame.mixer.music.load("sound/ohd_bgm_field.ogg")
                                pygame.mixer.music.play(-1)
                            elif title_sel == 1:  # 選擇難度
                                show_difficulty_menu = True
                                difficulty_sel = difficulty
                            elif title_sel == 2 and os.path.exists(save_file):  # 讀取存檔
                                if load_game():
                                    idx = 1
                                    welcome = 15
                                    pygame.mixer.music.load("sound/ohd_bgm_field.ogg")
                                    pygame.mixer.music.play(-1)
            # 標題選單滑鼠移動（hover 選取）
            if event.type == MOUSEMOTION and idx == 0:
                if not show_difficulty_menu:
                    mx, my = event.pos
                    gx = mx - offset_x
                    gy = my - offset_y
                    btn_w, btn_h = 300, 60
                    btn_x = (game_width - btn_w) // 2
                    for i in range(3):
                        btn_y = 470 + i * 70
                        if btn_x <= gx < btn_x + btn_w and btn_y <= gy < btn_y + btn_h:
                            title_sel = i
                            break
                else:
                    # 難度選擇介面的滑鼠移動
                    mx, my = event.pos
                    gx = mx - offset_x
                    gy = my - offset_y
                    btn_w, btn_h = 180, 80
                    start_x = (game_width - (btn_w * 3 + 40 * 2)) // 2
                    btn_y = 450
                    for i in range(3):
                        btn_x = start_x + i * (btn_w + 40)
                        if btn_x <= gx < btn_x + btn_w and btn_y <= gy < btn_y + btn_h:
                            difficulty_sel = i
                            break
            # 標題選單滑鼠點擊
            if event.type == MOUSEBUTTONDOWN and idx == 0:
                if not show_difficulty_menu:
                    mx, my = event.pos
                    gx = mx - offset_x
                    gy = my - offset_y
                    btn_w, btn_h = 300, 60
                    btn_x = (game_width - btn_w) // 2
                    for i in range(3):
                        btn_y = 470 + i * 70
                        if btn_x <= gx < btn_x + btn_w and btn_y <= gy < btn_y + btn_h:
                            if i == 0:  # 開始新遊戲
                                make_dungeon()
                                put_event()
                                floor = 1
                                welcome = 15
                                pl_lifemax = 300
                                pl_life = pl_lifemax
                                pl_str = 100
                                food = 300
                                potion = 0
                                blazegem = 0
                                kill_count = 0
                                combo_count = 0
                                game_start_time = pygame.time.get_ticks()
                                game_end_time = 0
                                achievements = {
                                    "floor_5": False,
                                    "floor_10": False,
                                    "kill_10": False,
                                    "kill_50": False,
                                    "explore_80": False
                                }
                                idx = 1
                                pygame.mixer.music.load("sound/ohd_bgm_field.ogg")
                                pygame.mixer.music.play(-1)
                            elif i == 1:  # 選擇難度
                                show_difficulty_menu = True
                                difficulty_sel = difficulty
                            elif i == 2 and os.path.exists(save_file):  # 讀取存檔
                                if load_game():
                                    idx = 1
                                    welcome = 15
                                    pygame.mixer.music.load("sound/ohd_bgm_field.ogg")
                                    pygame.mixer.music.play(-1)
                            break
                else:
                    # 難度選擇介面的滑鼠點擊
                    mx, my = event.pos
                    gx = mx - offset_x
                    gy = my - offset_y
                    btn_w, btn_h = 180, 80
                    start_x = (game_width - (btn_w * 3 + 40 * 2)) // 2  # 三個按鈕，間距40
                    btn_y = 450
                    for i in range(3):
                        btn_x = start_x + i * (btn_w + 40)
                        if btn_x <= gx < btn_x + btn_w and btn_y <= gy < btn_y + btn_h:
                            difficulty = i
                            show_difficulty_menu = False
                            break
            # 暫停介面滑鼠移動（hover 選取）
            if event.type == MOUSEMOTION and idx == 90:
                mx, my = event.pos
                gx = mx - offset_x
                gy = my - offset_y
                btn_w, btn_h = 300, 60
                btn_x = (game_width - btn_w) // 2
                btn_y = [280, 350, 420, 490]
                hovered = -1
                if 0 <= gx <= game_width and 0 <= gy <= game_height:
                    for i in range(4):
                        if btn_x <= gx <= btn_x+btn_w and btn_y[i] <= gy <= btn_y[i]+btn_h:
                            hovered = i
                            break
                if hovered != -1:
                    pause_sel = hovered

            # 暫停介面滑鼠點擊
            if event.type == MOUSEBUTTONDOWN and idx == 90:
                mx, my = event.pos
                gx = mx - offset_x
                gy = my - offset_y
                btn_w, btn_h = 300, 60
                btn_x = (game_width - btn_w) // 2
                btn_y = [280, 350, 420, 490]
                if 0 <= gx <= game_width and 0 <= gy <= game_height:
                    for i in range(4):
                        if btn_x <= gx <= btn_x+btn_w and btn_y[i] <= gy <= btn_y[i]+btn_h:
                            if i == 0:  # 繼續
                                idx = pause_return_idx
                                tmr = 0
                            elif i == 1:  # 存檔
                                save_game()
                            elif i == 2:  # 設定
                                idx = 91
                                settings_sel = 0
                                tmr = 0
                            elif i == 3:  # 退出
                                pygame.quit()
                                sys.exit()
                            break
            
            # 設定介面滑鼠互動
            if event.type == MOUSEBUTTONDOWN and idx == 91:
                mx, my = event.pos
                gx = mx - offset_x
                gy = my - offset_y
                
                # BGM 音量滑桿
                bar_x, bar_w = 450, 200
                bgm_y = 250
                if bar_x <= gx <= bar_x + bar_w and bgm_y + 5 <= gy <= bgm_y + 25:
                    settings["bgm_volume"] = max(0, min(1, (gx - bar_x) / bar_w))
                    apply_settings()
                
                # SE 音量滑桿
                se_y = 320
                if bar_x <= gx <= bar_x + bar_w and se_y + 5 <= gy <= se_y + 25:
                    settings["se_volume"] = max(0, min(1, (gx - bar_x) / bar_w))
                
                # 全螢幕切換
                fullscreen_y = 390
                if 200 <= gx <= 600 and fullscreen_y <= gy <= fullscreen_y + 30:
                    settings["fullscreen"] = not settings["fullscreen"]
                    if settings["fullscreen"]:
                        screen = pygame.display.set_mode((window_width, window_height), pygame.FULLSCREEN)
                        offset_x = (window_width - game_width) // 2
                        offset_y = (window_height - game_height) // 2
                    else:
                        screen = pygame.display.set_mode((game_width, game_height))
                        offset_x = 0
                        offset_y = 0
                
                # 返回按鈕
                btn_w_back = 200
                btn_x_back = (game_width - btn_w_back) // 2
                btn_y_back = 480
                if btn_x_back <= gx <= btn_x_back + btn_w_back and btn_y_back <= gy <= btn_y_back + 50:
                    save_settings()
                    idx = 90
                    tmr = 0
            
            # 設定介面滑鼠拖曳（持續按住滑鼠時）
            if event.type == MOUSEMOTION and idx == 91:
                if pygame.mouse.get_pressed()[0]:  # 左鍵按住
                    mx, my = event.pos
                    gx = mx - offset_x
                    gy = my - offset_y
                    
                    bar_x, bar_w = 450, 200
                    bgm_y = 250
                    # BGM 滑桿拖曳
                    if bar_x <= gx <= bar_x + bar_w and bgm_y + 5 <= gy <= bgm_y + 25:
                        settings["bgm_volume"] = max(0, min(1, (gx - bar_x) / bar_w))
                        apply_settings()
                    
                    # SE 滑桿拖曳
                    se_y = 320
                    if bar_x <= gx <= bar_x + bar_w and se_y + 5 <= gy <= se_y + 25:
                        settings["se_volume"] = max(0, min(1, (gx - bar_x) / bar_w))

        tmr = tmr + 1
        key = pygame.key.get_pressed()

        if idx == 0: # 標題畫面
            if tmr == 1:
                pygame.mixer.music.load("sound/ohd_bgm_title.ogg")
                pygame.mixer.music.play(-1)
                apply_settings()
            game_surface.fill(BLACK)
            # 置中標題圖片（水平置中）
            _title_x = (game_width - imgTitle.get_width()) // 2
            game_surface.blit(imgTitle, [_title_x, 60])
            if fl_max >= 2:
                # 置中「你到達了第 N 樓」文字（水平置中）
                _reach_txt = "你到達了第 {} 樓。".format(fl_max)
                _reach_sur = font.render(_reach_txt, True, WHITE)
                _reach_x = (game_width - _reach_sur.get_width()) // 2
                draw_text(game_surface, _reach_txt, _reach_x, 460, font, CYAN)
            
            if show_difficulty_menu:
                # 難度選擇介面（並排按鈕）- 向下移動避免與標題重疊
                draw_text(game_surface, "選擇難度", 350, 350, font, CYAN)
                
                btn_w, btn_h = 180, 80
                start_x = (game_width - (btn_w * 3 + 40 * 2)) // 2  # 三個按鈕，間距40
                btn_y = 450
                
                for i in range(3):
                    btn_x = start_x + i * (btn_w + 40)
                    
                    # 按鈕顏色
                    if i == difficulty_sel:
                        btn_color = CYAN
                        txt_color = BLACK
                    elif i == difficulty:
                        btn_color = (100, 200, 100)  # 當前難度用綠色
                        txt_color = WHITE
                    else:
                        btn_color = (80, 80, 80)
                        txt_color = WHITE
                    
                    # 繪製按鈕
                    pygame.draw.rect(game_surface, btn_color, [btn_x, btn_y, btn_w, btn_h])
                    pygame.draw.rect(game_surface, WHITE, [btn_x, btn_y, btn_w, btn_h], 3)
                    
                    # 置中文字
                    txt_sur = font.render(difficulty_names[i], True, txt_color)
                    txt_x = btn_x + (btn_w - txt_sur.get_width()) // 2
                    txt_y = btn_y + (btn_h - txt_sur.get_height()) // 2
                    game_surface.blit(txt_sur, [txt_x, txt_y])
                
                # 顯示提示
                draw_text(game_surface, "點擊選擇難度", 320, 570, fontS, WHITE)
                draw_text(game_surface, f"當前難度: {difficulty_names[difficulty]}", 300, 610, fontS, YELLOW)
            else:
                # 選單按鈕
                btn_titles = ["開始新遊戲", "選擇難度", "讀取存檔"]
                btn_w, btn_h = 300, 60
                btn_x = (game_width - btn_w) // 2
                has_save = os.path.exists(save_file)
                
                for i in range(3):
                    btn_y = 470 + i * 70
                    # 按鈕顏色
                    if i == 2 and not has_save:
                        btn_color = (60, 60, 60)  # 灰色（無存檔時）
                        txt_color = (100, 100, 100)
                    elif i == title_sel:
                        btn_color = CYAN
                        txt_color = BLACK
                    else:
                        btn_color = (80, 80, 80)
                        txt_color = WHITE
                    
                    # 繪製按鈕
                    pygame.draw.rect(game_surface, btn_color, [btn_x, btn_y, btn_w, btn_h])
                    pygame.draw.rect(game_surface, WHITE, [btn_x, btn_y, btn_w, btn_h], 2)
                    
                    # 置中文字
                    txt_sur = font.render(btn_titles[i], True, txt_color)
                    txt_x = btn_x + (btn_w - txt_sur.get_width()) // 2
                    txt_y = btn_y + (btn_h - txt_sur.get_height()) // 2
                    game_surface.blit(txt_sur, [txt_x, txt_y])

        elif idx == 1: # 玩家的移動
            move_player(key)
            draw_dungeon(game_surface, fontS)
            draw_text(game_surface, "第 {} 樓 ({},{})".format(floor, pl_x, pl_y), 60, 40, fontS, WHITE)
            if welcome > 0:
                welcome = welcome - 1
                draw_text(game_surface, "歡迎來到第 {} 樓。".format(floor), 300, 180, font, CYAN)
            # 迷你地圖：顯示在樓層文字下方
            draw_minimap(game_surface, 60, 80)
            # 顯示遊戲統計
            draw_stats(game_surface, fontS)
            # 成就檢查
            if floor == 5 and not achievements["floor_5"]:
                check_achievement("floor_5", "初探深淵", "到達第5樓")
            if floor == 10 and not achievements["floor_10"]:
                check_achievement("floor_10", "深淵挑戰者", "到達第10樓")
            explored = sum(row.count(1) for row in seen)
            total_tiles = DUNGEON_W * DUNGEON_H
            explore_rate = int(explored / total_tiles * 100)
            if explore_rate >= 80 and not achievements["explore_80"]:
                check_achievement("explore_80", "探索者", "探索率達80%")
            # 顯示成就通知
            draw_achievement_popup(game_surface, font)

        elif idx == 2: # 切換畫面
            draw_dungeon(game_surface, fontS)
            if 1 <= tmr and tmr <= 5:
                h = 80*tmr
                pygame.draw.rect(game_surface, BLACK, [0, 0, 880, h])
                pygame.draw.rect(game_surface, BLACK, [0, 720-h, 880, h])
            draw_minimap(game_surface, 60, 80)
            if tmr == 5:
                floor = floor + 1
                if floor > fl_max:
                    fl_max = floor
                welcome = 15
                make_dungeon()
                put_event()
            if 6 <= tmr and tmr <= 9:
                h = 80*(10-tmr)
                pygame.draw.rect(game_surface, BLACK, [0, 0, 880, h])
                pygame.draw.rect(game_surface, BLACK, [0, 720-h, 880, h])
            if tmr == 10:
                idx = 1

        elif idx == 3: # 取得道具或踩到陷阱
            draw_dungeon(game_surface, fontS)
            # 只在有對應圖片時才顯示（treasure 0-4 有圖片）
            if treasure <= 4:
                game_surface.blit(imgItem[treasure], [320, 220])
            draw_text(game_surface, TRE_NAME[treasure], 380, 240, font, WHITE)
            draw_minimap(game_surface, 60, 80)
            draw_achievement_popup(game_surface, font)
            if tmr == 10:
                idx = 1

        elif idx == 9: # 遊戲結束 - 結算畫面
            if tmr <= 30:
                PL_TURN = [2, 4, 0, 6]
                pl_a = PL_TURN[tmr%4]
                if tmr == 30: pl_a = 8 # 主角倒地的畫面
                draw_dungeon(game_surface, fontS)
            elif tmr == 31:
                play_se(3)
                # 記錄遊戲結束時間
                if game_end_time == 0:
                    game_end_time = pygame.time.get_ticks()
                
                game_surface.fill(BLACK)
                draw_text(game_surface, "遊戲結束", 340, 100, font, RED)
                # 顯示統計
                y_start = 220
                draw_text(game_surface, f"到達樓層: {floor} 樓", 280, y_start, font, WHITE)
                draw_text(game_surface, f"最高紀錄: {fl_max} 樓", 280, y_start + 60, font, CYAN)
                draw_text(game_surface, f"擊殺數: {kill_count}", 280, y_start + 120, font, WHITE)
                
                # 計算統計（使用儲存的結束時間）
                explored = sum(row.count(1) for row in seen)
                total_tiles = DUNGEON_W * DUNGEON_H
                explore_rate = int(explored / total_tiles * 100)
                elapsed = (game_end_time - game_start_time) // 1000
                minutes = elapsed // 60
                seconds = elapsed % 60
                
                draw_text(game_surface, f"探索率: {explore_rate}%", 280, y_start + 180, font, WHITE)
                draw_text(game_surface, f"遊玩時間: {minutes:02d}:{seconds:02d}", 280, y_start + 240, font, WHITE)
                draw_text(game_surface, f"難度: {difficulty_names[difficulty]}", 280, y_start + 300, font, YELLOW)
                
                draw_text(game_surface, "按空格鍵返回標題", 260, 600, fontS, BLINK[tmr%6])
            elif tmr > 31:
                # 保持結算畫面顯示（使用儲存的結束時間）
                game_surface.fill(BLACK)
                draw_text(game_surface, "遊戲結束", 340, 100, font, RED)
                y_start = 220
                draw_text(game_surface, f"到達樓層: {floor} 樓", 280, y_start, font, WHITE)
                draw_text(game_surface, f"最高紀錄: {fl_max} 樓", 280, y_start + 60, font, CYAN)
                draw_text(game_surface, f"擊殺數: {kill_count}", 280, y_start + 120, font, WHITE)
                
                explored = sum(row.count(1) for row in seen)
                total_tiles = DUNGEON_W * DUNGEON_H
                explore_rate = int(explored / total_tiles * 100)
                elapsed = (game_end_time - game_start_time) // 1000
                minutes = elapsed // 60
                seconds = elapsed % 60
                
                draw_text(game_surface, f"探索率: {explore_rate}%", 280, y_start + 180, font, WHITE)
                draw_text(game_surface, f"遊玩時間: {minutes:02d}:{seconds:02d}", 280, y_start + 240, font, WHITE)
                draw_text(game_surface, f"難度: {difficulty_names[difficulty]}", 280, y_start + 300, font, YELLOW)
                
                draw_text(game_surface, "按空格鍵返回標題", 260, 600, fontS, BLINK[tmr%6])
                
                if key[K_SPACE]:
                    idx = 0
                    tmr = 0

        elif idx == 10: # 開始戰鬥
            if tmr == 1:
                pygame.mixer.music.load("sound/ohd_bgm_battle.ogg")
                pygame.mixer.music.play(-1)
                init_battle()
                init_message()
            elif tmr <= 4:
                bx = (4-tmr)*220
                by = 0
                game_surface.blit(imgBtlBG, [bx, by])
                draw_text(game_surface, "遭遇敵人！", 350, 200, font, WHITE)
            elif tmr <= 16:
                draw_battle(game_surface, fontS)
                draw_text(game_surface, emy_name+"出現！", 300, 200, font, WHITE)
            else:
                idx = 11
                tmr = 0

        elif idx == 11: # 輪到玩家攻擊（等待指令輸入）
            draw_battle(game_surface, fontS)
            if tmr == 1: set_message("你的回合。")
            if battle_command(game_surface, font, key) == True:
                if btl_cmd == 0:
                    idx = 12
                    tmr = 0
                if btl_cmd == 1 and potion > 0:
                    idx = 20
                    tmr = 0
                if btl_cmd == 2 and blazegem > 0:
                    idx = 21
                    tmr = 0
                if btl_cmd == 3:
                    idx = 14
                    tmr = 0

        elif idx == 12: # 玩家發動攻擊
            draw_battle(game_surface, fontS)
            if tmr == 1:
                set_message("你發動攻擊！")
                play_se(0)
                # 計算傷害與暴擊
                is_critical = random.randint(1, 100) <= 25  # 25% 暴擊率
                floor_bonus = floor * 3  # 每層+3攻擊力（降低成長速度）
                base_dmg = pl_str + floor_bonus + random.randint(-5, 15)  # 增加變化性
                dmg = int(base_dmg * 2.5) if is_critical else base_dmg
            if 2 <= tmr and tmr <= 4:
                game_surface.blit(imgEffect[0], [700-tmr*120, -100+tmr*120])
            if tmr == 5:
                emy_blink = 5
                crit_text = "暴擊！" if is_critical else ""
                set_message(f"{crit_text}{dmg}點傷害！")
                # 添加傷害浮字
                add_damage_floater(emy_x + 50, emy_y + 50, dmg, is_critical)
            if tmr == 11:
                emy_life = emy_life - dmg
                if emy_life <= 0:
                    emy_life = 0
                    idx = 16
                    tmr = 0
            if tmr == 16:
                idx = 13
                tmr = 0

        elif idx == 13: # 輪到敵人攻擊
            draw_battle(game_surface, fontS)
            if tmr == 1:
                set_message("敵人的回合。")
            if tmr == 5:
                set_message(emy_name + "發動攻擊！")
                play_se(0)
                emy_step = 30
            if tmr == 9:
                dmg = emy_str + random.randint(0, 15)
                set_message(str(dmg)+"點傷害！")
                dmg_eff = 5
                emy_step = 0
                # 添加玩家受傷浮字
                add_damage_floater(400, 500, dmg, False)
            if tmr == 15:
                pl_life = pl_life - dmg
                if pl_life < 0:
                    pl_life = 0
                    idx = 15
                    tmr = 0
            if tmr == 20:
                idx = 11
                tmr = 0

        elif idx == 14: # 逃得掉嗎？
            draw_battle(game_surface, fontS)
            if tmr == 1: set_message("...")
            if tmr == 2: set_message("......")
            if tmr == 3: set_message("...........")
            if tmr == 4: set_message("............")
            if tmr == 5:
                if random.randint(0, 99) < 60:
                    idx = 22
                else:
                    set_message("逃脫失敗了。")
            if tmr == 10:
                idx = 13
                tmr = 0
             
        elif idx == 15: # 失敗
            draw_battle(game_surface, fontS)
            if tmr == 1:
                pygame.mixer.music.stop()
                set_message("你失敗了。")
            if tmr == 11:
                idx = 9
                tmr = 29

        elif idx == 16: # 勝利
            draw_battle(game_surface, fontS)
            if tmr == 1:
                set_message("你贏了！")
                pygame.mixer.music.stop()
                play_se(5)
                kill_count += 1
                
                # 連擊系統
                current_time = pygame.time.get_ticks()
                if current_time - last_kill_time < 10000:  # 10秒內連擊
                    combo_count += 1
                    if combo_count >= 2:
                        combo_bonus = int(pl_str * 0.1 * combo_count)  # 每次連擊+10%攻擊
                        pl_str += combo_bonus
                        set_message(f"連擊 x{combo_count}！攻擊力+{combo_bonus}")
                else:
                    combo_count = 1
                last_kill_time = current_time
                
                # 成就檢查
                if kill_count == 10 and not achievements["kill_10"]:
                    check_achievement("kill_10", "初次獵殺", "擊殺10隻怪物")
                if kill_count == 50 and not achievements["kill_50"]:
                    check_achievement("kill_50", "怪物剋星", "擊殺50隻怪物")
                
                # 怪物掉落系統 (30% 藥水, 20% 食物)
                drop_rand = random.randint(1, 100)
                if drop_rand <= 30:
                    potion += 1
                    set_message("你贏了！\n獲得藥水！")
                elif drop_rand <= 50:
                    food += random.randint(10, 30)
                    set_message("你贏了！\n獲得食物！")
            if tmr == 28:
                idx = 22
                if random.randint(0, emy_lifemax) > random.randint(0, pl_lifemax):
                    idx = 17
                    tmr = 0

        elif idx == 17: # 升級
            draw_battle(game_surface, fontS)
            if tmr == 1:
                set_message("升級了！")
                play_se(4)
                lif_p = random.randint(10, 20)
                str_p = random.randint(5, 10)
            if tmr == 21:
                set_message("最大生命力 + "+str(lif_p))
                pl_lifemax = pl_lifemax + lif_p
            if tmr == 26:
                set_message("力量 + "+str(str_p))
                pl_str = pl_str + str_p
            if tmr == 50:
                idx = 22

        elif idx == 20: # 藥水
            draw_battle(game_surface, fontS)
            if tmr == 1:
                set_message("使用藥水！")
                play_se(2)
            if tmr == 6:
                pl_life = pl_lifemax
                potion = potion - 1
            if tmr == 11:
                idx = 13
                tmr = 0

        elif idx == 21: # 火焰寶石
            draw_battle(game_surface, fontS)
            img_rz = pygame.transform.rotozoom(imgEffect[1], 30*tmr, (12-tmr)/8)
            X = 440-img_rz.get_width()/2
            Y = 360-img_rz.get_height()/2
            game_surface.blit(img_rz, [X, Y])
            if tmr == 1:
                set_message("使用火焰寶石！")
                play_se(1)
            if tmr == 6:
                blazegem = blazegem - 1
            if tmr == 11:
                dmg = 1000
                idx = 12
                tmr = 4

        elif idx == 22: # 戰鬥結束
            pygame.mixer.music.load("sound/ohd_bgm_field.ogg")
            pygame.mixer.music.play(-1)
            idx = 1

        # 只在非標題畫面顯示速度
        if idx != 0:
            draw_text(game_surface, "[S]速度 "+str(speed), 740, 40, fontS, WHITE)

        # 暫停介面繪製（覆蓋在目前遊戲畫面上）
        if idx == 90:
            overlay = pygame.Surface((game_width, game_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            game_surface.blit(overlay, (0, 0))
            # 標題
            title_text = "已暫停"
            title_sur = font.render(title_text, True, WHITE)
            title_x = (game_width - title_sur.get_width()) // 2
            draw_text(game_surface, title_text, title_x, 180, font, CYAN)
            # 按鈕
            btn_w, btn_h = 300, 60
            btn_x = (game_width - btn_w) // 2
            btn_y = [280, 350, 420, 490]
            labels = ["繼續遊戲", "存檔", "設定", "退出遊戲"]
            
            mx, my = pygame.mouse.get_pos()
            gx = mx - offset_x
            gy = my - offset_y
            
            for i in range(4):
                hovered = (btn_x <= gx <= btn_x+btn_w and btn_y[i] <= gy <= btn_y[i]+btn_h)
                col_n = (50, 50, 50)
                col_h = (80, 80, 80)
                pygame.draw.rect(game_surface, col_h if (hovered or pause_sel==i) else col_n, [btn_x, btn_y[i], btn_w, btn_h])
                pygame.draw.rect(game_surface, WHITE, [btn_x, btn_y[i], btn_w, btn_h], 2)
                
                label_sur = font.render(labels[i], True, WHITE)
                label_x = btn_x + (btn_w - label_sur.get_width()) // 2
                label_y = btn_y[i] + (btn_h - label_sur.get_height()) // 2
                draw_text(game_surface, labels[i], label_x, label_y, font, BLINK[tmr%6] if (hovered or pause_sel==i) else WHITE)
        
        # 設定介面繪製
        elif idx == 91:
            overlay = pygame.Surface((game_width, game_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            game_surface.blit(overlay, (0, 0))
            # 標題
            title_text = "設定"
            title_sur = font.render(title_text, True, WHITE)
            title_x = (game_width - title_sur.get_width()) // 2
            draw_text(game_surface, title_text, title_x, 150, font, CYAN)
            
            # 獲取滑鼠位置
            mx, my = pygame.mouse.get_pos()
            gx = mx - offset_x
            gy = my - offset_y
            
            # BGM 音量滑桿
            y = 250
            draw_text(game_surface, "BGM 音量", 200, y, fontS, WHITE)
            bar_x, bar_w = 450, 200
            bar_h = 20
            # 背景
            pygame.draw.rect(game_surface, (60,60,60), [bar_x, y+5, bar_w, bar_h])
            # 填充
            pygame.draw.rect(game_surface, CYAN, [bar_x, y+5, int(bar_w * settings["bgm_volume"]), bar_h])
            # 滑塊
            slider_x = bar_x + int(bar_w * settings["bgm_volume"])
            pygame.draw.circle(game_surface, WHITE, [slider_x, y+15], 12)
            pygame.draw.circle(game_surface, CYAN, [slider_x, y+15], 8)
            draw_text(game_surface, f"{int(settings['bgm_volume']*100)}%", bar_x+bar_w+20, y, fontS, WHITE)
            
            # SE 音量滑桿
            y = 320
            draw_text(game_surface, "SE 音量", 200, y, fontS, WHITE)
            # 背景
            pygame.draw.rect(game_surface, (60,60,60), [bar_x, y+5, bar_w, bar_h])
            # 填充
            pygame.draw.rect(game_surface, CYAN, [bar_x, y+5, int(bar_w * settings["se_volume"]), bar_h])
            # 滑塊
            slider_x = bar_x + int(bar_w * settings["se_volume"])
            pygame.draw.circle(game_surface, WHITE, [slider_x, y+15], 12)
            pygame.draw.circle(game_surface, CYAN, [slider_x, y+15], 8)
            draw_text(game_surface, f"{int(settings['se_volume']*100)}%", bar_x+bar_w+20, y, fontS, WHITE)
            
            # 全螢幕切換
            y = 390
            mode_text = "全螢幕" if settings["fullscreen"] else "視窗"
            fs_hovered = (200 <= gx <= 600 and y <= gy <= y + 30)
            col = BLINK[tmr%6] if fs_hovered else WHITE
            draw_text(game_surface, f"顯示模式: {mode_text}", 200, y, fontS, col)
            
            # 返回按鈕
            y = 480
            btn_w = 200
            btn_x = (game_width - btn_w) // 2
            btn_hovered = (btn_x <= gx <= btn_x + btn_w and y <= gy <= y + 50)
            pygame.draw.rect(game_surface, (80,80,80) if btn_hovered else (50,50,50), [btn_x, y, btn_w, 50])
            pygame.draw.rect(game_surface, WHITE, [btn_x, y, btn_w, 50], 2)
            label_sur = fontS.render("返回", True, WHITE)
            label_x = btn_x + (btn_w - label_sur.get_width()) // 2
            col = BLINK[tmr%6] if btn_hovered else WHITE
            draw_text(game_surface, "返回", label_x, y+10, fontS, col)

        # 先清空全螢幕
        screen.fill(BLACK)
        # 將遊戲表面置中繪製到全螢幕上
        screen.blit(game_surface, [offset_x, offset_y])
        pygame.display.update()
        clock.tick(4+2*speed)

if __name__ == '__main__':
    main()
