import ibapi
from tws_async import TWSClient, iswrapper, Stock, Forex, CFD


class TickStreamer(TWSClient):
    """
    Get live streaming tick data from TWS or gateway server.
    """
    def __init__(self):
        TWSClient.__init__(self)
        self.accountName = ''
        self._reqIdSeq = 0
        self._reqId2Contract = {}

    def subscribe(self):
        contracts = [
            Stock('GOOG'),
            Stock('INTC', primaryExchange='NASDAQ'),
            Forex('EURUSD'),
            CFD('IBUS500')
        ]
        for contract in contracts:
            reqId = self.getReqId()
            self._reqId2Contract[reqId] = contract
            self.reqMktData(reqId, contract, genericTickList='', snapshot=False,
                    regulatorySnapshot=False, mktDataOptions=[])

    @iswrapper
    def connectAck(self):
        self.reqAccountUpdates(1, '')
        self.reqOpenOrders()
        self.reqPositions()

    @iswrapper
    def tickPrice(self, reqId: int,
            tickType: ibapi.ticktype.TickType,
            price: float,
            attrib: ibapi.common.TickAttrib):
        contract = self._reqId2Contract[reqId]
        print('{} price {}'.format(contract.symbol, price))

    @iswrapper
    def tickSize(self, reqId: int,
            tickType: ibapi.ticktype.TickType,
            size: int):
        contract = self._reqId2Contract[reqId]
        print('{} size {}'.format(contract.symbol, size))

    @iswrapper
    def updateAccountTime(self, timeStamp: str):
        print('Time {}'.format(timeStamp))

    @iswrapper
    def accountDownloadEnd(self, accountName: str):
        self.accountName = accountName

    @iswrapper
    def updateAccountValue(self, key: str, val: str, currency: str,
            accountName: str):
        print('Account update: {} = {} {}'.format(key, val, currency))

    @iswrapper
    def position(self, account: str,
            contract: ibapi.contract.Contract,
            position: float,
            avgCost: float):
        print('Position: {} {} @ {}'.format(position, contract.symbol, avgCost))

    @iswrapper
    def positionEnd(self):
        pass


tws = TickStreamer()
tws.connect(host='127.0.0.1', port=7497, clientId=1)
tws.subscribe()
tws.run()
