from utilities import CandleColumns
import pandas as pd

class CandleFormation:
    def __init__(self) -> None:        
        self.ColumnsRequired = [] # add only CandleColumns Enum
        self.OneMinCandlesData = None
        self.StoreinFilepath = None
        self.StoreinDataFrame = False
        self.candle_time = None
        self.prev_candle_time = None
        self.completed_candles = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Timestamp', 'LowUptoNow','HighUptoNow'])
        self.LowestLow=1000000
        self.HighestHigh=0
        self.prev_candle = {}
        self.open=self.high=self.low=self.close=None
        pass

    def Form1MinCandle(self, filepath):
        
        ticks_data_df = pd.read_csv(filepath)
        ticks_data_df['DateTime'] = pd.to_datetime(ticks_data_df['Date'] + ' ' + ticks_data_df['Time'], dayfirst=True)

        ticks_data_df.set_index('DateTime', inplace=True)

        for index, row in ticks_data_df.iterrows():
            self.build_candle(index, row['LTP'], 'T')

    
    # Build dataframe with candle of specified timeframe
    def build_candle(self, timestamp, LTP, timeframe):
        # Get the current candle open timestamp
        self.candle_time = pd.Timestamp(timestamp).floor(timeframe)
        # print(self.candle_time)
       
        # Check if the candle open has changed
        if self.candle_time != self.prev_candle_time:
            
            if self.prev_candle_time is not None:
               
                if self.LowestLow>self.low and self.HighestHigh < self.high:
                    self.LowestLow = self.low
                    self.HighestHigh = self.high
                else:
                    if self.LowestLow>self.low:
                        self.LowestLow = self.low
                    if self.HighestHigh < self.high:
                        self.HighestHigh = self.high

            candle = pd.Series([self.open, self.high, self.low, self.close, self.prev_candle_time, self.LowestLow, self.HighestHigh],
                                index=['Open', 'High', 'Low', 'Close', 'Timestamp', 'LowUptoNow','HighUptoNow'])
            self.completed_candles=pd.concat([self.completed_candles, candle.to_frame().T], ignore_index=True)

            self.prev_candle = {'Open': self.open, 'High': self.high, 'Low': self.low, 'Close': self.close,
                                'Timestamp': self.prev_candle_time, 'LowUptoNow': self.LowestLow, 'HighUptoNow': self.HighestHigh}

            # Initialize the new candle
            self.open=self.high=self.low=self.close=LTP          
        else:
            # Update the minute candle values
            if self.open is None:
                self.open = LTP
            self.close = LTP
            self.high = max(LTP, self.high) if self.high is not None else LTP
            self.low = min(LTP, self.low) if self.low is not None else LTP

        
        # Update the previous candle
        self.prev_candle_time = self.candle_time        
