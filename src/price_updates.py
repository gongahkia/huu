from discord.ext import tasks
import yfinance as yf
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

async def setup_price_updates(bot, supabase):
    @tasks.loop(hours=1)
    async def price_update():
        users = supabase.table('users').select('*').execute()
        for user in users.data:
            if user['price_updates']:
                discord_user = await bot.fetch_user(int(user['user_id']))
                stocks = supabase.table('stocks').select('*').eq('user_id', user['user_id']).execute()
                coins = supabase.table('coins').select('*').eq('user_id', user['user_id']).execute()
                
                message = "Hourly Price Update:\n\n"
                
                if stocks.data:
                    message += "Stocks:\n"
                    for stock in stocks.data:
                        info = yf.Ticker(stock['ticker']).info
                        message += f"{stock['name']} ({stock['ticker']}): ${info['currentPrice']:.2f}\n"
                
                if coins.data:
                    message += "\nCryptocurrencies:\n"
                    coin_ids = [coin['coin_id'] for coin in coins.data]
                    prices = cg.get_price(ids=coin_ids, vs_currencies='usd')
                    for coin in coins.data:
                        message += f"{coin['name']} ({coin['coin_id']}): ${prices[coin['coin_id']]['usd']:.2f}\n"
                
                await discord_user.send(message)

    price_update.start()

    @bot.command(name='toggle_updates')
    async def toggle_updates(ctx):
        user = supabase.table('users').select('*').eq('user_id', str(ctx.author.id)).execute()
        if not user.data:
            supabase.table('users').insert({
                'user_id': str(ctx.author.id),
                'price_updates': True
            }).execute()
            await ctx.send("Price updates enabled.")
        else:
            current_status = user.data[0]['price_updates']
            supabase.table('users').update({'price_updates': not current_status}).eq('user_id', str(ctx.author.id)).execute()
            await ctx.send(f"Price updates {'disabled' if current_status else 'enabled'}.")