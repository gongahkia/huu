import discord
from discord.ext import commands
from pycoingecko import CoinGeckoAPI
from tabulate import tabulate

cg = CoinGeckoAPI()

def setup_coin_commands(bot, supabase):
    async def ensure_user_exists(user_id: str):
        result = supabase.table('users').select('*').eq('user_id', user_id).execute()
        if not result.data:
            supabase.table('users').insert({'user_id': user_id, 'price_updates': True}).execute()

    @bot.command(name='find_coin')
    async def find_coin(ctx, coin_id: str):
        await ensure_user_exists(str(ctx.author.id))
        try:
            coin = cg.get_coin_by_id(coin_id)
            embed = discord.Embed(title=f"{coin['name']} ({coin['symbol'].upper()})")
            embed.add_field(name="Price", value=f"${coin['market_data']['current_price']['usd']:.2f}")
            embed.add_field(name="Market Cap", value=f"${coin['market_data']['market_cap']['usd']:,}")
            embed.set_thumbnail(url=coin['image']['small'])
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"An error occurred while fetching information for {coin_id}: {str(e)}")

    @bot.command(name='add_coin')
    async def add_coin(ctx, coin_id: str):
        await ensure_user_exists(str(ctx.author.id))
        try:
            coin = cg.get_coin_by_id(coin_id)
            supabase.table('coins').insert({
                'user_id': str(ctx.author.id),
                'coin_id': coin_id,
                'name': coin['name']
            }).execute()
            await ctx.send(f"Added {coin['name']} ({coin['symbol'].upper()}) to your watchlist.")
        except Exception as e:
            await ctx.send(f"An error occurred while adding {coin_id}: {str(e)}")

    @bot.command(name='remove_coin')
    async def remove_coin(ctx, coin_id: str):
        await ensure_user_exists(str(ctx.author.id))
        try:
            result = supabase.table('coins').delete().eq('user_id', str(ctx.author.id)).eq('coin_id', coin_id).execute()
            if result.data:
                await ctx.send(f"Removed {coin_id} from your watchlist.")
            else:
                await ctx.send(f"{coin_id} was not found in your watchlist.")
        except Exception as e:
            await ctx.send(f"An error occurred while removing {coin_id}: {str(e)}")

    @bot.command(name='list_coins')
    async def list_coins(ctx):
        await ensure_user_exists(str(ctx.author.id))
        try:
            coins = supabase.table('coins').select('*').eq('user_id', str(ctx.author.id)).execute()
            if not coins.data:
                await ctx.send("You don't have any coins in your watchlist.")
                return
            
            data = []
            for coin in coins.data:
                try:
                    info = cg.get_price(ids=coin['coin_id'], vs_currencies='usd')[coin['coin_id']]
                    data.append([coin['coin_id'], f"${info['usd']:.2f}"])
                except Exception:
                    data.append([coin['coin_id'], 'N/A'])
            
            table = tabulate(data, headers=['Coin', 'Price (USD)'], tablefmt='pretty')
            await ctx.send(f"``````")
        except Exception as e:
            await ctx.send(f"An error occurred while listing coins: {str(e)}")