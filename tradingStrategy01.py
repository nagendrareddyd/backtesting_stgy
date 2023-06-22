# Strategy01: 
# 1. Buy at 9:16 open
# 2. keep stop loss as 10 or any number
# 3. keep profitbooking as 50 or infinity
# 4. keep total day stop loss as 25 or infinity
# 5. profit sell : condition 1 : reach the high of the day upto now
#                  condition 2: next candle reach the lowest of the previous candle (high reached candle)
# 6. re-enter buy: when reaches the lowest low of the day upto now

import os
from sqlite3 import Row
import pandas as pd
import jsonpickle
from datetime import timedelta

from dataclasses import dataclass

@dataclass
class Order:
    type: str
    datetime: str
    price: str

class TradingStrategy01:
    def __init__(self) -> None:
        self.orders = []
        self.count = 0
        self.minute_High =0
        self.BuySide_Stop_Loss = 10
        self.Buy_position_price = 0
        self.LowSoFar = 100000
        self.HighSofar = 0
        self.condition1Hit = False
        self.profitCondition1Hit = False
        self.profitCondition1HitTime = None
        self.condition1HitTime = None
        pass

    def run():
        print('started')

    async def startTrading(self, tradeDate):
        print(f'trading started - {tradeDate}')
        filepath = f'/Users/nagi/Projects/Trading/BackTesting/Data/options/GFDLNFO_TICK_{tradeDate}/BANKNIFTY-I.NFO.csv'
        if(not os.path.exists(filepath)):
            return

        ticks_data_df = self.GetTicksData(filepath)

        await self.FirstTrade(ticks_data_df)
        print(self.orders)
        
        for index, row in ticks_data_df.iterrows():
            if(index.hour == 9 and index.minute <= 16):
                continue

            self.setHighAndLow(row['LTP'])
            
            if(self.Buy_position_price > 0 and (row['LTP'] <= self.Buy_position_price - self.BuySide_Stop_Loss or await self.IsProfitReached(row['LTP'], index))):                
                self.Buy_position_price = 0
                self.profitCondition1Hit = False
                self.profitCondition1HitTime = None
                order = Order('SELL', str(index) , str(row['LTP']))
                await self.ProcessOrder(order)
                continue
            
            if(self.Buy_position_price > 0 and row['LTP'] >= self.HighSofar):                
                self.profitCondition1Hit = True
                self.profitCondition1HitTime = index
                continue

            if(self.Buy_position_price == 0 and row['LTP'] <= self.LowSoFar):                
                self.condition1Hit = True
                self.condition1HitTime = index
                continue

            if(self.Buy_position_price == 0 and await self.ReBuyConditionReached(row['LTP'], index)):                
                self.Buy_position_price = row['LTP']
                self.condition1Hit = False
                self.condition1HitTime = None
                order = Order('BUY', str(index) , str(row['LTP']))
                await self.ProcessOrder(order)
                continue

            
            if(self.Buy_position_price > 0 and index.hour == 15 and index.minute >= 20):
                self.Buy_position_price = 0
                order = Order('SELL', str(index) , str(row['LTP']))
                await self.ProcessOrder(order)                
                break
            
    async def ReBuyConditionReached(self, price, time):
        if(self.condition1Hit == True):
            if(time.hour == self.condition1HitTime.hour and time.minute == self.condition1HitTime.minute):
                return False
            re_buy_signal_candle_high = await self.GetMinuteHigh(self.condition1HitTime)
            return (re_buy_signal_candle_high <= price)
        return False

    async def IsProfitReached(self, price, time):
        if(self.profitCondition1Hit):            
            if(time.hour == self.profitCondition1HitTime.hour and time.minute == self.profitCondition1HitTime.minute):
                return False
            signal_candle_low = await self.GetMinuteLow(self.profitCondition1HitTime)           
            return signal_candle_low >= price
        return False

    async def ProcessOrder(self, order):
        self.orders.append(order)
       
    def setHighAndLow(self, value):
        if(self.LowSoFar > value):
            self.LowSoFar = value

        if(self.HighSofar < value):
            self.HighSofar = value

    async def WriteOrdersToJson(self, orders, tradingday):
        # store in variable
        json_string = jsonpickle.encode(orders)
        # write the JSON string to a file
        with open(f'/Users/nagi/Projects/Trading/BackTesting/src/backtesting_stgy/transactions/{tradingday}.json', 'w') as f:
            f.write(json_string)

    def GetTicksData(self, filepath):               
        ticks_data_df = pd.read_csv(filepath)
        ticks_data_df['DateTime'] = pd.to_datetime(ticks_data_df['Date'] + ' ' + ticks_data_df['Time'], dayfirst=True)

        ticks_data_df.set_index('DateTime', inplace=True)
        return ticks_data_df

    async def FirstTrade(self, ticks_data_df):
        for index, row in ticks_data_df.iterrows():            

            self.setHighAndLow(row['LTP'])

            if(index.hour == 9 and index.minute >= 16):
                self.Buy_position_price = row['LTP']

                # place buy order
                order = Order('BUY', str(index) , str(row['LTP']))
                await self.ProcessOrder(order)
                break

    async def GetMinuteHigh(self, present_time):
        tradedate = present_time.strftime("%d%m%Y")        
        filepath = f'/Users/nagi/Projects/Trading/BackTesting/Data/index_data_1min_low_high/{tradedate}.csv'
        df = pd.read_csv(filepath)
        present_time = present_time.replace(second=0)
        search_timestamp = present_time.strftime("%Y-%m-%d %H:%M:%S")        
        result = df[df['Timestamp'] == search_timestamp]
        return result.iloc[0].High

    async def GetMinuteLow(self, present_time):
        tradedate = present_time.strftime("%d%m%Y")        
        filepath = f'/Users/nagi/Projects/Trading/BackTesting/Data/index_data_1min_low_high/{tradedate}.csv'
        df = pd.read_csv(filepath)
        present_time = present_time.replace(second=0)        
        search_timestamp = present_time.strftime("%Y-%m-%d %H:%M:%S")        
        result = df[df['Timestamp'] == search_timestamp]
        return result.iloc[0].Low

    async def ResetTrade(self):
        self.orders = []
        self.count = 0
        self.minute_High =0
        self.BuySide_Stop_Loss = 10
        self.Buy_position_price = 0
        self.LowSoFar = 100000
        self.HighSofar = 0
        self.condition1Hit = False
        self.profitCondition1Hit = False
        self.profitCondition1HitTime = None
        self.condition1HitTime = None