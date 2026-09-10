import os
import discord
from discord.ext import commands
import requests

TOKEN = os.environ["DISCORD_TOKEN"]

PLAYER_ID = 592450

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
        "season": "2026"
    }

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    stats = data["stats"][0]["splits"][0]["stat"]

    return stats


@bot.event
async def on_ready():

    print(f"登入成功：{bot.user}")


@bot.command()
async def judge(ctx):

    try:

        stats = get_judge_stats()

        avg = stats.get("avg", "N/A")
        obp = stats.get("obp", "N/A")
        slg = stats.get("slg", "N/A")
        ops = stats.get("ops", "N/A")

        hr = stats.get("homeRuns", 0)
        rbi = stats.get("rbi", 0)
        hits = stats.get("hits", 0)
        runs = stats.get("runs", 0)

        message = f"""
⚾ **Aaron Judge｜2026 球季**

📊 **打擊成績**

AVG：{avg}
OBP：{obp}
SLG：{slg}
OPS：{ops}

🔥 HR：{hr}
💥 RBI：{rbi}
🎯 H：{hits}
🏃 R：{runs}
"""

        await ctx.send(message)

    except Exception as e:

        await ctx.send(
            f"❌ 查詢失敗：{e}"
        )


@bot.command()
async def helpjudge(ctx):

    message = """
⚾ **Aaron Judge Bot**

指令：

`!judge`
→ 查看 Aaron Judge 2026 球季成績

`!helpjudge`
→ 顯示指令說明
"""

    await ctx.send(message)


bot.run(TOKEN)
