from enum import Enum
from datetime import datetime, timedelta

class CandleColumns(Enum):
    Datetime = 0,
    Open = 1
    Close = 2
    High = 3
    Low = 4
    LowUptoNow = 5
    HighUptoNow = 6
    LastCandleLow = 7
    LastCandleHigh = 8

class Helper:
    def get_dates_between(self, start_date, end_date):
            # Convert the input strings to datetime objects
            start = datetime.strptime(start_date, '%b %d %Y')
            end = datetime.strptime(end_date, '%b %d %Y')

            # Create an empty list to store the formatted dates
            dates = []

            # Iterate through the range of dates
            current = start
            while current <= end:
                # Format the current date as 'DDMMYYYY' and add it to the list
                date_str = current.strftime('%d%m%Y')
                dates.append(date_str)

                # Move to the next day
                current += timedelta(days=1)

            return dates