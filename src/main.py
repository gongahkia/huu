import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from stock_commands import setup_stock_commands
from coin_commands import setup_coin_commands
from price_updates import setup_price_updates

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

supabase: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await setup_price_updates(bot, supabase)

setup_stock_commands(bot, supabase)
setup_coin_commands(bot, supabase)

bot.run(os.getenv('DISCORD_TOKEN'))