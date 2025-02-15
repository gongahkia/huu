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

async def ensure_user_exists(user_id: str):
    result = supabase.table('users').select('*').eq('user_id', user_id).execute()
    if not result.data:
        supabase.table('users').insert({'user_id': user_id, 'price_updates': True}).execute()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await setup_price_updates(bot, supabase)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await ensure_user_exists(str(message.author.id))
    await bot.process_commands(message)

setup_stock_commands(bot, supabase)
setup_coin_commands(bot, supabase)

bot.run(os.getenv('DISCORD_TOKEN'))