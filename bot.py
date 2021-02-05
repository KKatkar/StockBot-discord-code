import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Library for google search
from googlesearch import search

#Stock market info libraries
import pandas as pd
import yfinance as yf
from datetime import date,timedelta
import numpy as np

#Plotting libraries
import plotly.express as px

#Debugginbg
import traceback 

# current_stock = ''
s = None

errorGeneral = "The requested company code does not exist. \n You can get the company listing (NASDAQ/NYSE/so on...) name using \'GG: google search\' command.\n Eg. GG NYSE listings"

errorInitialize = "Specify the company using \'STOCK <company_code>\' command"

errorDates = "START date should be smaller than END date. \n Both should be in the format YYYY-MM-DD"

docURL = "https://pypi.org/project/yahoo-finance/"

errorRules = "For some intervals (Eg. INTERVAL 1m) only data of the last 7 days can be obtained. \n Refer yfinance documentation for all details:" + docURL

demoURL = "https://youtu.be/0w5HRHv7uJg"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="$")

@bot.event
async def on_ready(): #when bot is online
    print("Bot is running")

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.create_dm.send(
        f'Hi {member.name}, welcome to the Command Center'
    )

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    # Make a google search functionality

    if msg.content.startswith('GG'):
        searchContent = ""
        text = str(msg.content).split(' ')
        for string in range(1, len(text)):
            searchContent = searchContent + text[string] + " "

        for result in search(searchContent, tld="com", num=1, stop=1, pause=2):
            await msg.channel.send(result)
    

    # Get a list of all acceptable commands
    elif msg.content.startswith('HELP'):
        command_list = {'GG: Google search', 
        'STOCK: make a stock market query and initialize STOCK object. Eg. STOCK TSLA', 
        'STOCK HELP: List of stock market query commands',
        'DEMO: Provides an Example of all functionalities'}

        output_cmds = "```fix\n" #Yellow colored text
        for cmd in command_list:
            output_cmds = output_cmds + "\n" +cmd
        await msg.channel.send(output_cmds + "```")

    elif msg.content.startswith('DEMO'):
        await msg.channel.send(demoURL)


    # Commands specific to STOCK market activity
    elif msg.content.startswith('STOCK HELP'):
        command_list = {'H TREND: hourly plot of stock prices. Eg. H TREND GOOG \n', 
        'COMPANY HISTORY: plot of performance of the stock throughout its history. Eg. COMPANY HISTORY TSLA\n',
        'PERIOD: Plots closing price for the specified period. Requires STOCK to be initialized. (Type HELP or DEMO to see how!) \n '+
        '---Eg. PERIOD 5d. (Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max )\n',
        'DATE COMMANDS: More control by defining Start and End dates \n'
        }


        output_cmds = "```arm\n" #Red colored text
        for cmd in command_list:
            output_cmds = output_cmds + "\n" +cmd
        await msg.channel.send(output_cmds + "```")

    # Commands with higher control on date adjustments
    elif msg.content.startswith('DATE COMMANDS'):

        command_list = {'START: define START date for date specific plot. Eg. START YYYY-MM-DD \n',
        'END: define END date for date specific plot. Eg. END YYYY-MM-DD \n',
        'PLOT: Shows closing prices with START and END dates defined. Eg. PLOT \n',
        'INTERVAL (optional): Specify the interval for data received to plot. Default value = 1m \n'+
        '---Eg. INTERVAL 1m. (Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo) \n',
        }
        

        output_cmds = "```yaml\n" # cyan colored text
        for cmd in command_list:
            output_cmds = output_cmds + "\n" +cmd
        
        output_cmds = output_cmds + "\n**Note: There are limitations on how much data can be fetched. This can be referred at: \n"
        
        # const link = {url: "https://pypi.org/project/yahoo-finance/"}

        await msg.channel.send(output_cmds + "```")
        await msg.channel.send(docURL)





    #if query requests STOCK info: 
    # Eg. STOCK TSLA or STOCK TSLA GOOG
    elif msg.content.startswith('STOCK'):
        query = ""
        stocks = "" #will be used to initiate object

        text = str(msg.content).split(' ')
        # for string in range(1,len(text)):
        #     query = query + text[string] + " "
        # query = strip(query)
        
        # To return the last few activity days of market
        b = timedelta(days = 5)
        try:
            for string in range(1,len(text)):
                query = text[string]
                company_df = yf.download(query,
                                    start = date.today()-b,
                                    end = date.today(),
                                    interval = "1d",
                                    progress=False)
                
                day_1_df = company_df.tail(1)

                d = str(day_1_df.index[0].date())
                result = "-----> Details for "+ query+ "\n"+ day_1_df.index.name + ": " + d + "\n\n"

                for i in range(0,len(day_1_df.columns)):
                    result = result + day_1_df.columns[i] + ": " + str(day_1_df.values[0][i]) + "\n"

                stocks = stocks + query + " "
                    
                await msg.channel.send("```tex\n" + result + "```") #white string over black background
            
            stocks = stocks.strip()
            global s

            s = Stock(stocks) #Initiating the object
            print(s.getStock())

        
        
        except Exception as e:
            await msg.channel.send(errorGeneral)
            print(str(e))



        # Plot hourly trend
    elif msg.content.startswith('H TREND'):
        query = ""
        text = str(msg.content).split(' ')
        if(len(text) > 2):
            for string in range(2,len(text)):
                try:
                    query = text[string]

                    hourlyPlot(query)

                    await msg.channel.send(file = discord.File('images/plot.png'))
                    await msg.channel.send(file = discord.File('images/plot1.png'))
                
                except:
                    await msg.channel.send(errorGeneral)
        
        else:
            try:
                text = s.getStock().split(' ')
                for string in range(0,len(text)):
                    query = text[string]

                    hourlyPlot(query)

                    await msg.channel.send(file = discord.File('images/plot.png'))
                    await msg.channel.send(file = discord.File('images/plot1.png'))

            except:
                # await msg.channel.send("The requested company code does not exist. \n"+
                # "You can get the company listing (NASDAQ/NYSE/so on...) using \'GG: google search\' command.\n"+
                # "Eg. GG NYSE listings")
                await msg.channel.send(errorInitialize)


    
    elif msg.content.startswith('COMPANY HISTORY'):
        query = ""
        text = str(msg.content).split(' ')
        if(len(text) > 2):
            for string in range(2,len(text)):
                query = text[string]
                try:
                    companyHistory(query)

                    await msg.channel.send(file = discord.File('images/history.png'))
                
                except:
                    await msg.channel.send(errorGeneral)
            
        else:

            try:
                text = s.getStock().split(' ')
                for string in range(0,len(text)):
                    query = text[string]
                
                    companyHistory(query)

                    await msg.channel.send(file = discord.File('images/history.png'))
                
            except Exception as e:
                # await msg.channel.send("The requested company code does not exist. \n"+
                # "You can get the company listing (NASDAQ/NYSE/so on...) using \'GG: google search\' command.\n"+
                # "Eg. GG NYSE listings")
                await msg.channel.send(errorInitialize)
                print(str(e))

        
    elif msg.content.startswith('PERIOD'):
        p = ''
        text = str(msg.content).split(' ')
        try:
            p = text[1]
            query = s.getStock()

            company_df = yf.download(query,
            period = p,
            interval = "1d",
            progress=False)

            df_info = pd.DataFrame(company_df['Close']).copy()
            df_info.loc[:,'Datetime'] = df_info.index

            fig = px.line(df_info, 
            x = 'Datetime',
            y = list(df_info.keys()),
            title = "Closing Share prices for period: " + p
            )
    
            if not os.path.exists("images"):
                os.mkdir("images")
            
            fig.write_image("images/periodicPlot.png")

            await msg.channel.send(file = discord.File('images/periodicPlot.png'))

        except Exception as e:
            await msg.channel.send(errorInitialize)
            print(e)

    elif msg.content.startswith('START'):
        try:
            query = s.getStock()
            text = str(msg.content).split(' ')
            s.setStart(text[1])
            await msg.channel.send("```tex\n" + "START date defined" + "```")
        
        except Exception as e:
            await msg.channel.send(errorInitialize)
            print(e)

    elif msg.content.startswith('END'):
        try:
            query = s.getStock()
            text = str(msg.content).split(' ')
            s.setEnd(text[1])
            await msg.channel.send("```tex\n" + "END date defined" + "```")
        
        except:
            await msg.channel.send(errorInitialize)

    elif msg.content.startswith('INTERVAL'): #default = 1m
        try:
            query = s.getStock()
            text = str(msg.content).split(' ')
            s.setInterval(text[1])
            await msg.channel.send("```tex\n" + "Interval defined" + "```")
        
        except:
            await msg.channel.send(errorInitialize)

    elif msg.content.startswith('PLOT'):
        
        if(s==None):
            await msg.channel.send(errorInitialize)
        
        else:
            query = ''
            query = s.getStock()
        
            
        
            try:
                s_date = s.getStart()
                e_date = s.getEnd()
                
                if(s_date == ''):
                    await msg.channel.send("```fix\n" + "START date not defined. Use START <YYYY-MM-DD> command to define it!" + "```")

                
                elif(e_date ==''):
                    await msg.channel.send("```fix\n" + "END date not defined. Use END <YYYY-MM-DD> command to define it!" + "```")

                else:
                    company_df = yf.download(query,
                    start = s_date,
                    end = e_date,
                    interval = s.getInterval(),
                    progress=False)

                    df_info = pd.DataFrame(company_df['Close']).copy()
                    df_info.loc[:,'Datetime'] = df_info.index # .loc() is much faster with predicatable behaviour unlike chaining indexes
                    # df_info.reset_index(drop=True, inplace = True)

                    fig = px.line(df_info, 
                    #Debug
                    x = 'Datetime',
                    y = list(df_info.keys()),
                    title = "Closing Share prices from " + s_date + " to " + e_date
                    )
            
                    if not os.path.exists("images"):
                        os.mkdir("images")
                    
                    fig.write_image("images/start_end_plot.png")

                    await msg.channel.send(file = discord.File('images/start_end_plot.png'))
            
            except Exception as e:
                
                await msg.channel.send(errorDates)
                await msg.channel.send(errorRules)

                #Debugging
                # traceback.print_exc()
                # print(e.__class__.__name__)
                # print(type(e.__class__.__name__))


    # Default prompt
    else:
        response =  'You can type HELP (case-sensitive) to get a list of all commands'
        await msg.channel.send(response)

    await bot.process_commands(msg)

#clears messages. Can be set to 'None' to clear the entire chat
@bot.command()
async def clear(ctx, limit: int=None):
    async for text in ctx.message.channel.history(limit=limit):
        # if text.author.id == bot.user.id:
        try:
            await text.delete()
            # passed += 1
        except:
            # failed += 1
            pass



def hourlyPlot(query):
    #Ticker module provides more info about the company

    ticker = yf.Ticker(query)
    company_tick = ticker.history(period= '5d', interval = '1m')
    company_tick = company_tick.tail(60)  # last hour

    fig = px.line(company_tick['Close'], y = 'Close', title = ticker.info['shortName'] + " Share Prices "+
        str(company_tick.index[0].time())
        + " to " +str(company_tick.index[len(company_tick.index) - 1].time()))
    if not os.path.exists("images"):
        os.mkdir("images")
    
    fig.write_image("images/plot.png")

    #dataframe for 1 hour info of the stock
    
    # using timedelta library for practice
    b = timedelta(days = 5)

    # can use period = 5d instead of start/end.
    # Note period takes only the following values: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    company_df = yf.download(query,
            start = date.today()-b,
            end = date.today(),
            #period = '5d',
            interval = "1m",
            progress=False)

    company_df = company_df.tail(60) #last hour

    df_info = company_df[{'Open', 'High', 'Low', 'Close', 'Adj Close'}]
    df_info['Datetime'] = df_info.index

    fig = px.line(df_info, 
            x = 'Datetime',
            y = list(df_info.keys()),
            title = ticker.info['shortName'] + " Share Prices "+
            str(company_tick.index[0].time())
            + " to " +str(company_tick.index[len(company_tick.index) - 1].time())
            )
    
    fig.write_image("images/plot1.png")

    
def companyHistory(query, p = "max"):

    ticker = yf.Ticker(query)
    company_tick = ticker.history(period= p) #get company history

    fig = px.line(company_tick['Close'], y = 'Close', title = ticker.info['shortName'] + " Stock History")
    if not os.path.exists("images"):
        os.mkdir("images")
    
    fig.write_image("images/history.png")


#class Stock saves objects for quick command access
class Stock():
    stocks = ''
    start_date = ''
    end_date = ''
    interval = '1m'
    # period = ''

    def __init__(self,stocks):
        self.stocks = stocks
    
    def setStart(self, start_date):
        self.start_date = start_date
    
    def setEnd(self, end_date):
        self.end_date = end_date

    def setInterval(self, interval):
        self.interval = interval
    
    def getStock(self):
        try:
            return self.stocks
        except Exception as e:
            return "No company code included"
            print(e)
    
    def getStart(self):
        try:
            return self.start_date
        except Exception as e:
            return "Start date not defined."
            print(e)

    def getEnd(self):
        try:
            return self.end_date
        except Exception as e:
            return "End date not defined."
            print(e)

    def getInterval(self):
        try:
            return self.interval
        except Exception as e:
            return "interval not specified."
            print(e)
        


bot.run(TOKEN)