from candleFormation import CandleFormation
from utilities import CandleColumns, Helper
import os
from tradingStrategy01 import TradingStrategy01
import asyncio
from orderAnalysis import OrderAnalysis

class Main:
    def __init__(self) -> None:
        pass

    async def start(self):
        print('start')
        # totalOrders = []
        # helperinstance = Helper()
        orderInstance = OrderAnalysis()
        # trade_days = helperinstance.get_dates_between('Feb 01 2022', 'Feb 28 2022')
        # tradingInstance = TradingStrategy01()
        # for tradingday in trade_days:
        #     await tradingInstance.startTrading(tradingday)
        #     if(len(tradingInstance.orders) > 0):
        #         await tradingInstance.WriteOrdersToJson(tradingInstance.orders, tradingday)
        #         totalOrders.append(tradingInstance.orders) 
        #         await tradingInstance.ResetTrade()            
        #         orderInstance.Graph_Formation(tradingday)
        orderInstance.CalculateProfitForMonth('Feb 01 2022', 'Feb 28 2022')
        print('completed')
        
    def FormCandle(self, tradeDate):
        filepath = f'/Users/nagi/Projects/Trading/BackTesting/Data/options/GFDLNFO_TICK_{tradeDate}/BANKNIFTY-I.NFO.csv'
        if(not os.path.exists(filepath)):
            return
        candleInstance = CandleFormation()
        candleInstance.Form1MinCandle(filepath)
        out_file_path = f'/Users/nagi/Projects/Trading/BackTesting/Data/index_data_1min_low_high/{tradeDate}.csv'
        candleInstance.completed_candles.to_csv(out_file_path, index=False)

    def SetupInitialData(self):
        helperinstance = Helper()
        trade_days = helperinstance.get_dates_between('Feb 01 2022', 'Feb 28 2022')

        for tradingday in trade_days:
            self.FormCandle(tradingday)
        print('completed')

instance = Main()
#instance.SetupInitialData()

asyncio.run(instance.start())

