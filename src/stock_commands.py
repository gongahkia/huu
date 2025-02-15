import discord
from discord.ext import commands
import yfinance as yf
from tabulate import tabulate

def setup_stock_commands(bot, supabase):
    @bot.command(name='find_stock')
    async def find_stock(ctx, ticker: str):
        stock = yf.Ticker(ticker)
        info = stock.info
        embed = discord.Embed(title=f"{info['longName']} ({ticker})")
        embed.add_field(name="Price", value=f"${info['currentPrice']:.2f}")
        embed.add_field(name="Market Cap", value=f"${info['marketCap']:,}")
        embed.set_thumbnail(url=info['logo_url'])
        await ctx.send(embed=embed)

    @bot.command(name='add_stock')
    async def add_stock(ctx, ticker: str):
        stock = yf.Ticker(ticker)
        info = stock.info
        supabase.table('stocks').insert({
            'user_id': str(ctx.author.id),
            'ticker': ticker,
            'name': info['longName']
        }).execute()
        await ctx.send(f"Added {info['longName']} ({ticker}) to your watchlist.")

    @bot.command(name='remove_stock')
    async def remove_stock(ctx, ticker: str):
        supabase.table('stocks').delete().eq('user_id', str(ctx.author.id)).eq('ticker', ticker).execute()
        await ctx.send(f"Removed {ticker} from your watchlist.")

    @bot.command(name='list_stocks')
    async def list_stocks(ctx):
        stocks = supabase.table('stocks').select('*').eq('user_id', str(ctx.author.id)).execute()
        if not stocks.data:
            await ctx.send("You don't have any stocks in your watchlist.")
            return
        
        data = []
        for stock in stocks.data:
            info = yf.Ticker(stock['ticker']).info
            data.append([stock['ticker'], info['currentPrice'], info['dayHigh'], info['dayLow']])
        
        table = tabulate(data, headers=['Ticker', 'Price', 'Day High', 'Day Low'], tablefmt='pretty')
        await ctx.send(f"``````")