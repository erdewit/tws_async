import datetime
import pytz
from tws_async import *


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
for date in util.dateRange(startDate, endDate):
    histReqs += [HistRequest(stock, date) for stock in stocks]
    histReqs += [HistRequest(forex, date, whatToShow='MIDPOINT',
            durationStr='30 D', barSizeSetting='1 day') for forex in forexs]

timezone = datetime.timezone.utc
# timezone = pytz.timezone('Europe/Amsterdam')
# timezone = pytz.timezone('US/Eastern')

util.logToConsole()
tws = HistRequester()
tws.connect('127.0.0.1', 7497, clientId=1)
task = tws.download(histReqs, rootDir='data', timezone=timezone)
tws.run(task)
