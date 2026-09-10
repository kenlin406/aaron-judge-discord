import os
import json
import discord
from discord.ext import commands
import requests
from datetime import datetime
# ==========================================
# 基本設定
# ==========================================
TOKEN = os.environ["DISCORD_TOKEN"]
PLAYER_ID = 592450
YANKEES_ID = 147
SEASON = 2026
# 如果之後要自動推播，把你的 Discord 頻道 ID 放這裡
# 例如：CHANNEL_ID = 123456789012345678
CHANNEL_ID = None
# 用來記錄已經推播過的比賽
LAST_GAME_FILE = "last_game.txt"
# ==========================================
# Discord Bot 設定
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix="!",
    intents=intents
)
# ==========================================
# MLB API
# ==========================================
def mlb_get(url, params=None):
    response = requests.get(
        url,
        params=params,
        timeout=30
    )
    print("MLB API:", response.url)
    print("Status:", response.status_code)
    response.raise_for_status()
    return response.json()
# ==========================================
# 找今天 Yankees 的比賽
# ==========================================
def get_today_game():
    today = datetime.now().strftime("%Y-%m-%d")
    url = "https://statsapi.mlb.com/api/v1/schedule"
    params = {
        "sportId": 1,
        "date": today,
        "teamId": YANKEES_ID,
        "hydrate": "linescore"
    }
    data = mlb_get(url, params)
    dates = data.get("dates", [])
    if not dates:
        return None
    games = dates[0].get("games", [])
    if not games:
        return None
    return games[0]
# ==========================================
# 取得 Box Score
# ==========================================
def get_boxscore(game_pk):
    url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore"
    return mlb_get(url)
# ==========================================
# 從 Box Score 找 Aaron Judge
# ==========================================
def get_judge_game_stats(game):
    game_pk = game["gamePk"]
    data = get_boxscore(game_pk)
    teams = data["teams"]
    judge_stats = None
    # 檢查主隊與客隊
    for side in ["home", "away"]:
        team = teams[side]
        players = team.get("players", {})
        player_key = f"ID{PLAYER_ID}"
        if player_key in players:
            player = players[player_key]
            stats = player.get("stats", {})
            batting = stats.get("batting")
            if batting:
                judge_stats = batting
                break
    return judge_stats
# ==========================================
# 格式化單場成績
# ==========================================
def format_today_message(game, stats):
    home = game["teams"]["home"]["team"]["name"]
    away = game["teams"]["away"]["team"]["name"]
    home_score = game["teams"]["home"].get("score", 0)
    away_score = game["teams"]["away"].get("score", 0)
    status = game["status"]["detailedState"]
    game_date = game["officialDate"]
    at_bats = stats.get("atBats", 0)
    hits = stats.get("hits", 0)
    home_runs = stats.get("homeRuns", 0)
    rbi = stats.get("rbi", 0)
    runs = stats.get("runs", 0)
    walks = stats.get("baseOnBalls", 0)
    strikeouts = stats.get("strikeOuts", 0)
    doubles = stats.get("doubles", 0)
    triples = stats.get("triples", 0)
    return f"""
⚾ **Aaron Judge｜{game_date}**
🏟️ **{away} {away_score} - {home_score} {home}**
📌 比賽狀態：{status}
### 🔥 今日打擊
AB：**{at_bats}**
H：**{hits}**
2B：**{doubles}**
3B：**{triples}**
HR：**{home_runs}**
RBI：**{rbi}**
R：**{runs}**
BB：**{walks}**
SO：**{strikeouts}**
🎯 今日表現：
**{hits}-{at_bats}**
Game PK：`{game["gamePk"]}`
"""
# ==========================================
# !today
# ==========================================
@bot.command()
async def today(ctx):
    try:
        game = get_today_game()
        if game is None:
            await ctx.send(
                "⚾ 今天沒有找到 Yankees 的比賽。"
            )
            return
        stats = get_judge_game_stats(game)
        if stats is None:
            status = game["status"]["detailedState"]
            await ctx.send(
                f"⚾ 找到 Yankees 比賽！\n"
                f"目前狀態：{status}\n\n"
                f"但目前還沒有取得 Aaron Judge 的單場打擊資料。\n"
                f"如果比賽還沒開始或正在進行，請稍後再輸入 `!today`。"
            )
            return
        message = format_today_message(
            game,
            stats
        )
        await ctx.send(message)
    except Exception as e:
        print(f"!today ERROR: {e}")
        await ctx.send(
            f"❌ 查詢失敗：{e}"
        )
# ==========================================
# !judge
# ==========================================
@bot.command()
async def judge(ctx):
    try:
        url = f"https://statsapi.mlb.com/api/v1/people/{PLAYER_ID}/stats"
        params = {
            "stats": "season",
            "group": "hitting",
            "season": str(SEASON),
            "sportIds": "1"
        }
        data = mlb_get(url, params)
        if not data.get("stats"):
            await ctx.send(
                "⚾ 找不到 Aaron Judge 的球季資料。"
            )
            return
        splits = data["stats"][0].get("splits", [])
        if not splits:
            await ctx.send(
                "⚾ 目前沒有 Aaron Judge 的 2026 球季資料。"
            )
            return
        stats = splits[0]["stat"]
        avg = stats.get("avg", "N/A")
        obp = stats.get("obp", "N/A")
        slg = stats.get("slg", "N/A")
        ops = stats.get("ops", "N/A")
        games = stats.get("gamesPlayed", 0)
        hits = stats.get("hits", 0)
        home_runs = stats.get("homeRuns", 0)
        rbi = stats.get("rbi", 0)
        runs = stats.get("runs", 0)
        walks = stats.get("baseOnBalls", 0)
        strikeouts = stats.get("strikeOuts", 0)
        message = f"""
⚾ **Aaron Judge｜2026 球季**
📊 **累積成績**
出賽：**{games}**
AVG：**{avg}**
OBP：**{obp}**
SLG：**{slg}**
OPS：**{ops}**
🔥 HR：**{home_runs}**
💥 RBI：**{rbi}**
🎯 H：**{hits}**
🏃 R：**{runs}**
🚶 BB：**{walks}**
❌ SO：**{strikeouts}**
"""
        await ctx.send(message)
    except Exception as e:
        print(f"!judge ERROR: {e}")
        await ctx.send(
            f"❌ 查詢失敗：{e}"
        )
# ==========================================
# !helpjudge
# ==========================================
@bot.command()
async def helpjudge(ctx):
    message = """
⚾ **Aaron Judge Bot**
📌 指令：
`!judge`
→ 查看 Aaron Judge 2026 球季累積成績
`!today`
→ 查看 Aaron Judge 今天的單場成績
`!helpjudge`
→ 查看指令說明
🔥 Bot 可以再加入每日自動推播功能。
"""
    await ctx.send(message)
# ==========================================
# Bot 啟動
# ==========================================
@bot.event
async def on_ready():
    print("=" * 40)
    print(f"登入成功：{bot.user}")
    print("Aaron Judge Bot 已啟動")
    print("=" * 40)
# ==========================================
# 啟動
# ==========================================
bot.run(TOKEN)
