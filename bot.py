import os
import discord
from discord.ext import commands
import aiohttp
import sqlite3
import random
from config import RE_TOKEN, DEV_ID, DEV_TOKEN, DEVMODE

if DEVMODE:
    token = DEV_TOKEN
else:
    token = RE_TOKEN

conn = sqlite3.connect("juste-prix.db")
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS servers (server_id INTEGER PRIMARY KEY, prefix TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, wins INTEGER)")

# Fonction qui verifie si une colonne existe dans une table
def column_exists(cursor, table_name, column_name):
    cursor.execute("PRAGMA table_info({})".format(table_name))
    columns = cursor.fetchall()
    for column in columns:
        if column[1] == column_name:
            return True
    return False

if not column_exists(c, "servers", "channel_id"):
    c.execute("ALTER TABLE servers ADD COLUMN channel_id INTEGER")

if not column_exists(c, "servers", "object"):
    c.execute("ALTER TABLE servers ADD COLUMN object TEXT")

if not column_exists(c, "servers", "price"):
    c.execute("ALTER TABLE servers ADD COLUMN price INTEGER")

if not column_exists(c, "users", "user_id"):
    c.execute("ALTER TABLE users ADD COLUMN user_id INTEGER")

# Initialisation du bot
class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

bot = Bot()

# Fonction pour acceder a la DB
async def add_object(guild_id, object):
    c.execute("UPDATE servers SET object = ? WHERE server_id = ?", (object, guild_id))
    conn.commit()

async def add_price(guild_id, price):
    c.execute("UPDATE servers SET price = ? WHERE server_id = ?", (price, guild_id))
    conn.commit()

async def fetch_object(guild_id):
    c.execute("SELECT object FROM servers WHERE server_id = ?", (guild_id,))
    return c.fetchone()

async def fetch_price(guild_id):
    c.execute("SELECT price FROM servers WHERE server_id = ?", (guild_id,))
    return c.fetchone()

# Fonctions pour jouer au juste prix
async def newitem():
    return random.randint(1, 1000000)

async def juste_prix():
    price = await fetch_price()
    return price

@bot.event
async def on_ready():
    print(f"{bot.user} est connecté avec succès !")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {synced} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    await bot.change_presence(activity=discord.Game(name='TU DUDU'))

@bot.tree.command(name="ping")
async def ping(ctx):
    await ctx.response.send_message("Pong ! " + str(round(bot.latency * 1000)) + "ms")

@bot.tree.command(name="start")


# Commandes admin
@bot.tree.command(name="stop")
@commands.is_owner()
async def stop(ctx):
    await ctx.response.send_message("🛑 Arrêt du bot...")
    await bot.close()

bot.run(token)