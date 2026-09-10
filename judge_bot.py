import requests
from datetime import datetime, timedelta, timezone

WEBHOOK_URL = https://discord.com/api/webhooks/1547457299872874567/-SDUm-P51mxiFGDawQvJBC8kcLKKlJ9bNgSIM-0HM7Qs2C6KnkUJxTgK4xZM2M9J6LSJ

PLAYER_ID = 592450

TW = timezone(timedelta(hours=8))


def get_schedule(date):
    url = "https://statsapi.mlb.com/api/v1/schedule"

    params = {
        "sportId": 1,
        "date": date
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()


def get_boxscore(game_pk):
    url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore"

    response = requests.get(url)
    response.raise_for_status()

    return response.json()


def send_discord(message):
    requests.post(
        WEBHOOK_URL,
        json={"content": message}
    )


today = datetime.now(TW)
date = (today - timedelta(days=1)).strftime("%Y-%m-%d")

schedule = get_schedule(date)

if not schedule.get("dates"):
    print("昨天沒有比賽")
    exit()

found = False

for date_data in schedule["dates"]:

    for game in date_data["games"]:

        game_pk = game["gamePk"]

        boxscore = get_boxscore(game_pk)

        players = {}

        players.update(boxscore["teams"]["away"]["players"])
        players.update(boxscore["teams"]["home"]["players"])

        player_key = f"ID{PLAYER_ID}"

        if player_key not in players:
            continue

        player = players[player_key]

        stats = player.get("stats", {}).get("batting", {})

        if not stats:
            continue

        ab = stats.get("atBats", 0)
        hits = stats.get("hits", 0)
        hr = stats.get("homeRuns", 0)
        rbi = stats.get("rbi", 0)
        runs = stats.get("runs", 0)
        bb = stats.get("baseOnBalls", 0)
        so = stats.get("strikeOuts", 0)

        message = f"""⚾ **Aaron Judge 今日成績**

📅 {date}

**{ab} AB｜{hits} H｜{hr} HR｜{rbi} RBI**

得分：{runs}
保送：{bb}
三振：{so}
"""

        send_discord(message)

        found = True

        print("Aaron Judge 成績已發送")

        break

    if found:
        break


if not found:
    print("Aaron Judge 昨天沒有出賽")
