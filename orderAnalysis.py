import pandas as pd
import plotly.graph_objects as go
import json
import os

from utilities import Helper

class OrderAnalysis:
    def __init__(self) -> None:
        self.day_profit = 0
        self.no_of_transaction = 0
        pass

    def CalculateProfitAndLoss(self, data):       
        for index, row in data.iterrows():
            if(row['type'] == 'BUY'):
                buy_price = row['price']
            
            if(row['type'] == 'SELL'):
                self.day_profit = self.day_profit + float(row['price']) - float(buy_price)
                self.no_of_transaction += 1

    def Graph_Formation(self, tradedate):
        self.day_profit = 0
        self.no_of_transaction = 0
        candles = pd.read_csv(f'/Users/nagi/Projects/Trading/BackTesting/Data/index_data_1min_low_high/{tradedate}.csv')        
        candles['DateTime'] = pd.to_datetime(candles['Timestamp'],format='%Y-%m-%d %H:%M:%S', dayfirst=True)       
        candles = candles.set_index('DateTime')
       
        with open(f'/Users/nagi/Projects/Trading/BackTesting/src/backtesting_stgy/transactions/{tradedate}.json', 'r') as f:
            buysell_data = json.load(f)

        buysell_df = pd.DataFrame(buysell_data)
        buysell_df.set_index('datetime', inplace=True)

        self.CalculateProfitAndLoss(buysell_df)

        #buysell_df['datetime'] = pd.to_datetime(buysell_df['datetime'])
        # Get the index and price for buy and sell points
        buy_points = buysell_df[buysell_df['type'] == 'BUY']['price'].astype(float)
        sell_points = buysell_df[buysell_df['type'] == 'SELL']['price'].astype(float)


        # Create the candlestick chart
        fig = go.Figure(data=go.Candlestick(x=candles.index,
                                        open=candles['Open'],
                                        high=candles['High'],
                                        low=candles['Low'],
                                        close=candles['Close']))

        # Add scatter traces for buy and sell points
        fig.add_trace(go.Scatter(x=buy_points.index,
                                y=buy_points,
                                mode='markers',
                                name='Buy',
                                marker=dict(color='green', size=10)))

        fig.add_trace(go.Scatter(x=sell_points.index,
                                y=sell_points,
                                mode='markers',
                                name='Sell',
                                marker=dict(color='red', size=10)))

        # Set x-axis and y-axis labels
        fig.update_layout(xaxis_title='Datetime', yaxis_title='Price')

        # Set the chart title
        fig.update_layout(title_text='1-minute Candlestick Chart with Buy and Sell Points')

        # Add an annotation outside the chart
        fig.add_annotation(
            xref='paper',
            yref='paper',
            x=1.05,  # Adjust the x-coordinate to position the annotation
            y=0.5,  # Adjust the y-coordinate to position the annotation
            text=f'Number of transactions today: {str(self.no_of_transaction)}',
            showarrow=False
        )

        fig.add_annotation(
            xref='paper',
            yref='paper',
            x=1.05,  # Adjust the x-coordinate to position the annotation
            y=0.6,  # Adjust the y-coordinate to position the annotation
            text=f'Profit/Loss Today: {str(round(self.day_profit, 1))}',
            showarrow=False
        )

        # Update the layout to accommodate the annotation
        fig.update_layout(
            annotations=[
                dict(
                    text=f'Number of transactions today: {str(self.no_of_transaction)}',
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=1.05,  # Adjust the x-coordinate to position the annotation
                    y=0.5,  # Adjust the y-coordinate to position the annotation
                    align='left'
                ),
                dict(
                    text=f'Profit/Loss Today: {str(round(self.day_profit, 1))}',
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=1.05,  # Adjust the x-coordinate to position the annotation
                    y=0.6,  # Adjust the y-coordinate to position the annotation
                    align='left'
                )
            ]
        )

        chart_file = f'/Users/nagi/Projects/Trading/BackTesting/src/backtesting_stgy/charts/candlestick_chart_{tradedate}.html'
        fig.write_html(chart_file)

    def CalculateProfitForMonth(self, startdate, enddate):
        helperinstance = Helper()
        p_df = pd.DataFrame(columns=['Date', 'profit', 'no_of_transactions'])
        o_list = []

        trade_days = helperinstance.get_dates_between(startdate, enddate)       
        for tradingday in trade_days:
            self.day_profit = 0
            self.no_of_transaction = 0
            
            filepath = f'/Users/nagi/Projects/Trading/BackTesting/src/backtesting_stgy/transactions/{tradingday}.json'
            if(not os.path.exists(filepath)):
                continue

            with open(filepath, 'r') as f:
                buysell_data = json.load(f)

            buysell_df = pd.DataFrame(buysell_data)
            buysell_df.set_index('datetime', inplace=True)

            self.CalculateProfitAndLoss(buysell_df)
            

            o_list.append({'Date': tradingday, 'profit': self.day_profit, 'no_of_transactions': self.no_of_transaction})
            

            #p_df = pd.concat([pd.DataFrame({'Date': tradingday, 'profit': self.day_profit, 'no_of_transactions': self.no_of_transaction}), p_df])
        p_df = pd.DataFrame.from_records(o_list)
        p_df.to_html(f'/Users/nagi/Projects/Trading/BackTesting/src/backtesting_stgy/charts/{str(startdate)}--{str(enddate)}.html')
