import os
import discord
from discord.ext import commands
import requests
from datetime import datetime, timezone

# =========================
# 基本設定
# =========================

TOKEN = os.environ["DISCORD_TOKEN"]

PLAYER_ID = 592450
SEASON = 2026

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================
# MLB API
# =========================

def get_mlb_data(url, params=None):

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# =========================
# 取得 Aaron Judge 球季成績
# =========================

def get_judge_season_stats():

    url = f"https://statsapi.mlb.com/api/v1/people/{PLAYER_ID}/stats"

    params = {
        "stats": "season",
        "group": "hitting",
        "season": SEASON
    }

    data = get_mlb_data(url, params)

    splits = data["stats"][0]["splits"]

    if not splits:
        return None

    return splits[0]["stat"]


# =========================
# 取得 Aaron Judge 今天的比賽
# =========================

def get_today_game():

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    url = "https://statsapi.mlb.com/api/v1/schedule"

    params = {
        "sportId": 1,
        "date": today,
        "hydrate": "linescore"
    }

    data = get_mlb_data(url, params)

    dates = data.get("dates", [])

    if not dates:
        return None

    games = dates[0].get("games", [])

    for game in games:

        home_team = game["teams"]["home"]["team"]["id"]
        away_team = game["teams"]["away"]["team"]["id"]

        # New York Yankees = 147
        if home_team == 147 or away_team == 147:
            return game

    return None


# =========================
# Bot 上線
# =========================

@bot.event
async def on_ready():

    print(f"登入成功：{bot.user}")

    print("Aaron Judge Bot 已啟動")


# =========================
# !judge
# =========================

@bot.command()
async def judge(ctx):

    try:

        stats = get_judge_season_stats()

        if stats is None:

            await ctx.send(
                "⚾ 目前找不到 Aaron Judge 的 2026 球季資料。"
            )

            return

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
⚾ **Aaron Judge｜{SEASON} 球季**

📊 **打擊成績**

出賽：{games}
打擊率 AVG：{avg}
上壘率 OBP：{obp}
長打率 SLG：{slg}
OPS：{ops}

🔥 全壘打 HR：{home_runs}
💥 打點 RBI：{rbi}
🎯 安打 H：{hits}
🏃 得分 R：{runs}
🚶 保送 BB：{walks}
❌ 三振 SO：{strikeouts}
"""

        await ctx.send(message)

    except Exception as e:

        print(f"!judge 錯誤：{e}")

        await ctx.send(
            f"❌ 查詢失敗：{e}"
        )


# =========================
# !today
# =========================

@bot.command()
async def today(ctx):

    try:

        game = get_today_game()

        if game is None:

            await ctx.send(
                "⚾ 今天沒有找到 Yankees 的比賽。"
            )

            return

        game_status = game["status"]["detailedState"]

        home = game["teams"]["home"]["team"]["name"]
        away = game["teams"]["away"]["team"]["name"]

        home_score = game["teams"]["home"].get("score", 0)
        away_score = game["teams"]["away"].get("score", 0)

        message = f"""
⚾ **Aaron Judge｜今日比賽**

🏟️ {away} @ {home}

比分：
{away} **{away_score}**
{home} **{home_score}**

📌 比賽狀態：{game_status}

目前這個版本會先確認 Yankees 今天是否有比賽。

下一版可以再加入：
🔥 Judge 今日打數
🎯 安打
💣 全壘打
💥 打點
🏃 得分
"""

        await ctx.send(message)

    except Exception as e:

        print(f"!today 錯誤：{e}")

        await ctx.send(
            f"❌ 查詢失敗：{e}"
        )


# =========================
# !helpjudge
# =========================

@bot.command()
async def helpjudge(ctx):

    message = """
⚾ **Aaron Judge Bot**

📌 指令：

`!judge`
→ 查看 Aaron Judge 2026 球季成績

`!today`
→ 查看今天 Yankees 比賽狀態

`!helpjudge`
→ 顯示這份指令說明

🔥 之後可以加入每日自動推播！
"""

    await ctx.send(message)


# =========================
# 啟動 Bot
# =========================

bot.run(TOKEN)
