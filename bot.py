import os
from dotenv import load_dotenv  # ← Ajoute cette ligne
import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup

# Charge les variables depuis le fichier .env
load_dotenv()  # ← Charge les variables d’environnement

# Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

users = {
    "bvstn": "Baston",
    "Catamaran23": "Bawel",
}

def get_thm_info(username):
    url = f"https://tryhackme.com/p/{username}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        rank_tag = soup.find("span", {"class": "rank"})
        rank = rank_tag.text.strip() if rank_tag else "No rank"

        badge_tag = soup.find("div", {"class": "badges-count"})
        badges = int(badge_tag.text.strip()) if badge_tag else 0

        streak_tag = soup.find("span", {"class": "streak"})
        streak = int(streak_tag.text.strip()) if streak_tag else 0

        rooms_tag = soup.find("span", {"class": "rooms-completed"})
        rooms_completed = int(rooms_tag.text.strip()) if rooms_tag else 0

        score_tag = soup.find("span", {"class": "points"})
        score = int(score_tag.text.replace(',', '')) if score_tag else 0

        return {
            'score': score,
            'badge': badges,
            'rooms_completed': rooms_completed,
            'rank': rank,
            'streak': streak
        }
    except requests.exceptions.RequestException as e:
        print(f"Request error for {username}: {e}")
        return None
    except Exception as e:
        print(f"Error for {username}: {e}")
        return None

@bot.command()
async def leaderboard(ctx):
    leaderboard = []
    for username, display_name in users.items():
        user_info = get_thm_info(username)
        leaderboard.append((display_name, user_info))

    leaderboard.sort(key=lambda x: x[1]['score'] if x[1] else 0, reverse=True)

    msg = "**🏆 TryHackMe Leaderboard 🏆**\n"
    for rank, (name, info) in enumerate(leaderboard, start=1):
        if info:
            msg += f"{rank}. **{name}** - {info['score']} points\n"
            msg += f"   Rank: {info['rank']}\n"
            msg += f"   Badge: {info['badge']} badges\n"
            msg += f"   Rooms completed: {info['rooms_completed']}\n"
            msg += f"   Streak: {info['streak']} day(s)\n"
        else:
            msg += f"{rank}. **{name}** - Error retrieving data\n"

    await ctx.send(msg)

# Démarrage sécurisé du bot
token = os.getenv("DISCORD_BOT_TOKEN")
if not token:
    raise ValueError("Token Discord introuvable. Assure-toi que le fichier .env contient DISCORD_BOT_TOKEN.")

bot.run(token)
