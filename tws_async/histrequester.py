import os
import datetime
import asyncio
import logging
import csv

import ibapi
from .twsclient import TWSClient, iswrapper, TWSException
from ibapi.wrapper import BarData

UTC = datetime.timezone.utc

__all__ = ['HistRequester', 'HistRequest']


class HistRequest:
    """
    Historical request.
    """
    def __init__(self, contract, endDateTime=None, durationStr='1 D',
            barSizeSetting='1 min', keepUpToDate = False, whatToShow='TRADES', useRTH=False):
        self.contract = contract
        self.endDateTime = endDateTime
        self.durationStr = durationStr
        self.barSizeSetting = barSizeSetting
        self.keepUptoDate = keepUpToDate
        self.whatToShow = whatToShow
        self.useRTH = useRTH
        self.formatDate = 1 if barSizeSetting \
                in ('1 day', '1 week', '1 month') else 2
        self.chartOptions = None
        self.data = []


class HistRequester(TWSClient):
    """
    Download historical data and save to CSV files.
    """
    def __init__(self):
        TWSClient.__init__(self)
        self._reqIdSeq = 0
        self._histReqs = {}
        self._futs = {}
        self._logger = logging.getLogger(__class__.__name__)

    async def histReqAsync(self, req: HistRequest) -> list:
        """
        Download historical data for the given request and return
        the data as a list of [datetime, open, high, low, close, volume] lists.
        """
        await self.readyEvent.wait()
        reqId = self.getReqId()
        if not req.endDateTime:
            end = ''
        elif isinstance(req.endDateTime, datetime.datetime):
            end = req.endDateTime.strftime('%Y%m%d %H:%M:%S'),
        else:
            end = req.endDateTime.strftime('%Y%m%d 23:59:59')
        self.reqHistoricalData(reqId, req.contract, end,
                req.durationStr, req.barSizeSetting, req.whatToShow,
                req.useRTH, formatDate=req.formatDate, keepUpToDate = req.keepUptoDate,
                chartOptions=req.chartOptions)
        self._histReqs[reqId] = req
        fut = asyncio.Future()
        self._futs[reqId] = fut
        await fut
        return fut.result().data

    async def download(self, histReqs: [HistRequest],
            rootDir: str='data', timezone=UTC):
        """
        Download historical data for the list of historical requests and
        write each result to its own CSV file below the given
        rootDir directory (default 'data' in the current directory).

        The timezone parameter (default UTC) specifies what timezone to use
        for the timestamps of the bars in the CSV output.
        When the timezone is UTC no additional timezone information is written
        in the output.
        
        To avoid pacing violations, one request at a time is submitted
        to the server.
        """
        for histReq in histReqs:
            filename = self.getCsvFilename(histReq)
            path = os.path.join(rootDir, filename)
            if os.path.exists(path):
                continue
            try:
                data = await self.histReqAsync(histReq)
                dir = os.path.dirname(path)
                if not os.path.isdir(dir):
                    os.makedirs(dir)
                with open(path, 'w', newline='') as f:
                    csvfile = csv.writer(f)
                    csvfile.writerow([
                            'Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
                    for row in data:
                        if timezone is not UTC and histReq.formatDate == 2:
                            # write timezone info when timzone is not UTC
                            dt = row[0]
                            row[0] = dt.replace(tzinfo=UTC).astimezone(timezone)
                        csvfile.writerow(row)
                self._logger.info('Downloaded {}, {} bars'.
                        format(filename, len(data)))
            except TWSException as e:
                self._logger.info('Error downloading {}: {}'.
                        format(filename, e))

    def getCsvFilename(self, histReq):
        """
        Get relative filename of where the historical data should be saved.
        The name may contain sub directories.
        """
        c = histReq.contract
        if c.secType == 'CASH':
            name = c.symbol + c.currency
        elif c.secType == 'FUT':
            name = c.localSymbol or '{}-{}'.format(
                    c.symbol, c.lastTradeDateOrContractMonth)
        elif c.secType == 'OPT':
            name = c.localSymbol or '{}-{}{}-{}'.format(
                    c.symbol, c.right, c.strike,
                    c.lastTradeDateOrContractMonth)
        else:
            name = c.localSymbol or c.symbol

        filename = '{}_{}_{}.csv'.format(name,
                histReq.barSizeSetting.replace(' ', ''),
                histReq.endDateTime.strftime('%Y%m%d'))
        return filename

    @iswrapper
    def historicalData(self, reqId: int, bar: BarData):
    # def historicalData(self, reqId: int, date: str, open: float, high: float,
    #         low: float, close: float, volume: int, barCount: int,
    #         WAP: float, hasGaps: int):
        histReq = self._histReqs[reqId]
        if histReq.formatDate == 1:
            # YYYYmmdd
            y = int(bar.date[0:4])
            m = int(bar.date[4:6])
            d = int(bar.date[6:8])
            dt = datetime.date(y, m, d)
        else:
            dt = datetime.datetime.utcfromtimestamp(int(bar.date))
        histReq.data.append([dt, bar.open, bar.high, bar.low, bar.close,
                             bar.volume if bar.volume > 0 else 0])

    @iswrapper
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        histReq = self._histReqs.pop(reqId)
        fut = self._futs.pop(reqId)
        fut.set_result(histReq)

    @iswrapper
    def error(self, reqId: int, errorCode: int, errorString: str):
        if reqId in self._histReqs:
            fut = self._futs.pop(reqId)
            fut.set_exception(TWSException(errorString))
