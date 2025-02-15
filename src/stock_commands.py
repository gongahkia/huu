import discord
from discord.ext import commands
import yfinance as yf
from tabulate import tabulate

def setup_stock_commands(bot, supabase):
    async def ensure_user_exists(user_id: str):
        result = supabase.table('users').select('*').eq('user_id', user_id).execute()
        if not result.data:
            supabase.table('users').insert({'user_id': user_id, 'price_updates': True}).execute()

    @bot.command(name='find_stock')
    async def find_stock(ctx, ticker: str):
        await ensure_user_exists(str(ctx.author.id))
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info:
                await ctx.send(f"No information available for ticker {ticker}")
                return
            
            embed = discord.Embed(title=f"{info.get('longName', 'Unknown')} ({ticker})")
            embed.add_field(name="Price", value=f"${info.get('currentPrice', 'N/A'):.2f}")
            embed.add_field(name="Market Cap", value=f"${info.get('marketCap', 'N/A'):,}")
            
            if 'logo_url' in info:
                embed.set_thumbnail(url=info['logo_url'])
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"An error occurred while fetching information for {ticker}: {str(e)}")

    @bot.command(name='add_stock')
    async def add_stock(ctx, ticker: str):
        await ensure_user_exists(str(ctx.author.id))
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info:
                await ctx.send(f"No information available for ticker {ticker}")
                return
            
            supabase.table('stocks').insert({
                'user_id': str(ctx.author.id),
                'ticker': ticker,
                'name': info.get('longName', 'Unknown')
            }).execute()
            await ctx.send(f"Added {info.get('longName', 'Unknown')} ({ticker}) to your watchlist.")
        except Exception as e:
            await ctx.send(f"An error occurred while adding {ticker}: {str(e)}")

    @bot.command(name='remove_stock')
    async def remove_stock(ctx, ticker: str):
        await ensure_user_exists(str(ctx.author.id))
        try:
            result = supabase.table('stocks').delete().eq('user_id', str(ctx.author.id)).eq('ticker', ticker).execute()
            if result.data:
                await ctx.send(f"Removed {ticker} from your watchlist.")
            else:
                await ctx.send(f"{ticker} was not found in your watchlist.")
        except Exception as e:
            await ctx.send(f"An error occurred while removing {ticker}: {str(e)}")

    @bot.command(name='list_stocks')
    async def list_stocks(ctx):
        try:
            stocks = supabase.table('stocks').select('*').eq('user_id', str(ctx.author.id)).execute()
            if not stocks.data:
                await ctx.send("You don't have any stocks in your watchlist.")
                return
            
            stock_list = []
            for stock in stocks.data:
                info = yf.Ticker(stock['ticker']).info
                current_price = info.get('currentPrice', 'N/A')
                if current_price != 'N/A':
                    current_price = f"${current_price:.2f}"
                stock_list.append(f"{stock['name']} ({stock['ticker']}): {current_price}")
            
            stock_message = "Your stocks:\n" + "\n".join(stock_list)
            await ctx.send(stock_message)
        except Exception as e:
            await ctx.send(f"An error occurred while listing stocks: {str(e)}")