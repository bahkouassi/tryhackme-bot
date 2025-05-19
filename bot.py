import asyncio
import discord
from discord.ext import commands
from playwright.async_api import async_playwright
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Classement (ordre = classement)
USERS = [
    ("2470546", "Bawel"),
    ("2787126", "Double Eyes"),
    ("2162464", "H@rpoCr@ker89"),
    ("1471764", "Varo"),
    ("2757814", "Christoff11"),
    ("3844342", "Baston"),
    ("3333798", "Frank"),
    ("4732031", "Yasmine"),
]

# Emojis personnalisés pour les 3 premiers
TOP_EMOJIS = [
    "🥇🔥",  # 1er : or + flamme
    "🥈✨",  # 2ème : argent + étoile brillante
    "🥉🌟"   # 3ème : bronze + étoile brillante
]
DEFAULT_EMOJI = "⭐"

async def screenshot_badge(user_id: str, output_file="badge.png"):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        iframe_url = f"https://tryhackme.com/api/v2/badges/public-profile?userPublicId={user_id}"
        html = f"""
        <html style="margin:0;padding:0;overflow:hidden;background:transparent;">
        <body style="margin:0;padding:0;overflow:hidden;background:transparent;">
        <iframe id="badge" src="{iframe_url}" width="327" height="84" style="border:none;"></iframe>
        </body>
        </html>
        """
        await page.set_content(html)
        await page.wait_for_timeout(3000)

        frame_element = await page.query_selector("iframe#badge")
        if frame_element:
            await frame_element.screenshot(path=output_file)
        else:
            print(f"❌ Could not find iframe for user {user_id}")

        await browser.close()

@bot.command(name="livebadge")
async def live_badge(ctx):
    await ctx.send("⏳ Récupération des badges pour le classement...")

    try:
        await ctx.send("\n🏆 **LEADERBOARD** 🏆\n")

        for index, (user_id, username) in enumerate(USERS):
            emoji = TOP_EMOJIS[index] if index < len(TOP_EMOJIS) else DEFAULT_EMOJI
            file_path = f"badge_{user_id}.png"

            await screenshot_badge(user_id=user_id, output_file=file_path)

            await ctx.send(f"{emoji} **{username}**", file=discord.File(file_path))
            await ctx.send("➖" * 6)

            os.remove(file_path)

    except Exception as e:
        print(f"❌ Erreur : {e}")
        await ctx.send("⚠️ Une erreur est survenue lors de la récupération des badges.")

bot.run(TOKEN)