import os
import discord
from discord.ext import commands
import requests
TOKEN = os.environ["DISCORD_TOKEN"]
PLAYER_ID = 592450
SEASON = 2026
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix="!",
    intents=intents
)
def get_judge_stats():
    url = f"https://statsapi.mlb.com/api/v1/people/{PLAYER_ID}/stats"
    params = {
        "stats": "season",
        "group": "hitting",
        "season": str(SEASON),
        "sportIds": "1"
    }
    response = requests.get(
        url,
        params=params,
        timeout=30
    )
    print("MLB API:", response.url)
    print("Status:", response.status_code)
    response.raise_for_status()
    data = response.json()
    if not data.get("stats"):
        return None
    if not data["stats"][0].get("splits"):
        return None
    return data["stats"][0]["splits"][0]["stat"]
@bot.event
async def on_ready():
    print(f"登入成功：{bot.user}")
@bot.command()
async def judge(ctx):
    try:
        stats = get_judge_stats()
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
⚾ **Aaron Judge｜2026 球季**
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
    except requests.exceptions.HTTPError as e:
        await ctx.send(
            f"❌ MLB API 發生錯誤：{e}"
        )
    except Exception as e:
        await ctx.send(
            f"❌ 查詢失敗：{e}"
        )
@bot.command()
async def helpjudge(ctx):
    message = """
⚾ **Aaron Judge Bot**
`!judge`
→ 查看 Aaron Judge 2026 球季成績
`!helpjudge`
→ 顯示指令說明
"""
    await ctx.send(message)
bot.run(TOKEN)
