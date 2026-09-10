import os
import discord
from discord.ext import commands
import requests
from datetime import datetime, timedelta
# ==========================================
# 基本設定
# ==========================================
TOKEN = os.environ["DISCORD_TOKEN"]
PLAYER_ID = 592450
YANKEES_ID = 147
SEASON = 2026
# ==========================================
# Discord Bot
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
# 找「昨天」Yankees 的比賽
# ==========================================
def get_yesterday_game():
    yesterday = (
        datetime.now() - timedelta(days=1)
    ).strftime("%Y-%m-%d")
    url = "https://statsapi.mlb.com/api/v1/schedule"
    params = {
        "sportId": 1,
        "date": yesterday,
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
    url = (
        f"https://statsapi.mlb.com/api/v1/game/"
        f"{game_pk}/boxscore"
    )
    return mlb_get(url)
# ==========================================
# 找 Aaron Judge 的單場成績
# ==========================================
def get_judge_game_stats(game):
    game_pk = game["gamePk"]
    data = get_boxscore(game_pk)
    teams = data["teams"]
    player_key = f"ID{PLAYER_ID}"
    for side in ["home", "away"]:
        team = teams[side]
        players = team.get("players", {})
        if player_key in players:
            player = players[player_key]
            stats = player.get("stats", {})
            batting = stats.get("batting")
            if batting:
                return batting
    return None
# ==========================================
# 格式化昨日成績
# ==========================================
def format_game_message(game, stats):
    home = game["teams"]["home"]["team"]["name"]
    away = game["teams"]["away"]["team"]["name"]
    home_score = game["teams"]["home"].get("score", 0)
    away_score = game["teams"]["away"].get("score", 0)
    status = game["status"]["detailedState"]
    game_date = game["officialDate"]
    at_bats = stats.get("atBats", 0)
    hits = stats.get("hits", 0)
    doubles = stats.get("doubles", 0)
    triples = stats.get("triples", 0)
    home_runs = stats.get("homeRuns", 0)
    rbi = stats.get("rbi", 0)
    runs = stats.get("runs", 0)
    walks = stats.get("baseOnBalls", 0)
    strikeouts = stats.get("strikeOuts", 0)
    return f"""
⚾ **Aaron Judge｜{game_date}**
🏟️ **{away} {away_score} - {home_score} {home}**
📌 比賽狀態：{status}
### 🔥 昨日打擊成績
AB：**{at_bats}**
H：**{hits}**
2B：**{doubles}**
3B：**{triples}**
HR：**{home_runs}**
RBI：**{rbi}**
R：**{runs}**
BB：**{walks}**
SO：**{strikeouts}**
🎯 **今日表現：{hits}-{at_bats}**
"""
# ==========================================
# !today
# 現在改成查「昨天」
# ==========================================
@bot.command()
async def today(ctx):
    try:
        game = get_yesterday_game()
        if game is None:
            await ctx.send(
                "⚾ 昨天沒有找到 Yankees 的比賽。"
            )
            return
        stats = get_judge_game_stats(game)
        if stats is None:
            await ctx.send(
                "⚾ 找到昨天 Yankees 的比賽，"
                "但沒有找到 Aaron Judge 的打擊資料。"
            )
            return
        message = format_game_message(
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
# 球季累積成績
# ==========================================
@bot.command()
async def judge(ctx):
    try:
        url = (
            f"https://statsapi.mlb.com/api/v1/"
            f"people/{PLAYER_ID}/stats"
        )
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
`!judge`
→ 查看 Aaron Judge 2026 球季累積成績
`!today`
→ 查看 Aaron Judge 昨天的單場成績
`!helpjudge`
→ 查看指令說明
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
# 啟動 Bot
# ==========================================
bot.run(TOKEN)
