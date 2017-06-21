import datetime
import pytz
from tws_async import *

# pick the desired timezone to use for intraday data in the CSV output
timezone = datetime.timezone.utc
# timezone = pytz.timezone('Europe/Amsterdam')
# timezone = pytz.timezone('US/Eastern')

stocks = [
    Stock('TSLA'),
    Stock('AAPL'),
    Stock('GOOG'),
    Stock('INTC', primaryExchange='NASDAQ')
]
forexs = [
    Forex('EURUSD'),
    Forex('GBPUSD'),
    Forex('USDJPY')
]

endDate = datetime.date.today()
startDate = endDate - datetime.timedelta(days=7)

histReqs = []
for date in dateRange(startDate, endDate):
    histReqs += [HistRequest(stock, endDateTime=date) for stock in stocks]
    histReqs += [HistRequest(forex, endDateTime=date, whatToShow='MIDPOINT')
            for forex in forexs]

tws = HistRequester()
tws.connect('127.0.0.1', 7497, clientId=1)
task = tws.download(histReqs, rootDir='data', timezone=timezone)
tws.run(task)
