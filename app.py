import discord
import requests
import json
import fastapi
import uvicorn
import os
import multiprocessing
import random
import time
import asyncio
import urllib.parse
import datetime

from discord.ext import commands
from multiprocessing import Process
from fastapi import Query
from fastapi.responses import HTMLResponse

# ===============================
# Railway ENV Variables
# ===============================
token = os.getenv("TOKEN")
secret = os.getenv("SECRET")
client_id = os.getenv("ID")
redirect = os.getenv("REDIRECT")
api = os.getenv("API_ENDPOINT", "https://discord.com/api/v10")

logs_env = os.getenv("LOGS", "")
logs = [x.strip() for x in logs_env.split(",") if x.strip()]

# ===============================
# FastAPI + Discord Bot
# ===============================
app = fastapi.FastAPI()

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)
client.remove_command("help")


# ===============================
# Bot Ready
# ===============================
@client.event
async def on_ready():
    os.system("cls || clear")
    print(f"✅ Logged in as {client.user}")


# ===============================
# Railway Web Server
# ===============================
def run_fastapi():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080))
    )


def keep_alive():
    Process(target=run_fastapi).start()


# ===============================
# Home Route
# ===============================
@app.get("/")
async def home():
    return {"status": "Authix Running Fine"}


# ===============================
# OAuth Callback
# ===============================
@app.get("/callback")
def authenticate(code=Query(...)):
    try:
        data = {
            "client_id": client_id,
            "client_secret": secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect,
            "scope": "identify guilds.join"
        }

        response = requests.post(f"{api}/oauth2/token", data=data)
        details = response.json()

        access_token = details["access_token"]
        refresh_token = details["refresh_token"]

        headers = {"Authorization": f"Bearer {access_token}"}
        user_info = requests.get(f"{api}/users/@me", headers=headers).json()

        username = user_info["username"]

        return HTMLResponse(f"""
        <html>
        <body style="background:#111;color:white;text-align:center;padding:60px;font-family:Arial;">
        <h1>✅ Auth Success</h1>
        <p>Welcome {username}</p>
        </body>
        </html>
        """)

    except Exception as e:
        return HTMLResponse(f"""
        <html>
        <body style="background:#111;color:red;text-align:center;padding:60px;font-family:Arial;">
        <h1>❌ Auth Failed</h1>
        <p>{str(e)}</p>
        </body>
        </html>
        """)


# ===============================
# Commands
# ===============================
@client.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")


@client.command()
async def help(ctx):
    embed = discord.Embed(
        title="📚 Commands",
        color=discord.Color.blue()
    )
    embed.add_field(name="!ping", value="Bot Ping", inline=False)
    embed.add_field(name="!auth_link", value="Get OAuth Link", inline=False)

    await ctx.send(embed=embed)


@client.command(name="auth_link")
async def auth_link(ctx):
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect,
        "scope": "identify guilds.join"
    }

    url = "https://discord.com/oauth2/authorize?" + urllib.parse.urlencode(params)

    await ctx.send(f"🔗 {url}")


# ===============================
# Start
# ===============================
if __name__ == "__main__":
    keep_alive()
    client.run(token)
