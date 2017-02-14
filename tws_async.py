import struct
import asyncio

import ibapi
from ibapi.client import EClient
from ibapi.wrapper import EWrapper


class TWSClient(EClient):
    """
    Modification of EClient that plays well with an event loop.
    
    This example uses the event loop from asyncio.
    """
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)

    def reset(self):
        EClient.reset(self)
        self._data = b''

    def run(self):
        # not needed anymore
        pass

    def connect(self, host, port, clientId):
        self.host = host
        self.port = port
        self.clientId = clientId
        self.setConnState(EClient.CONNECTING)
        self.conn = TWSConnection(host, port)
        self.conn.connected += [self._onSocketConnected]
        self.conn.hasData += [self._onSocketHasData]
        self.conn.connect()

    def _prefix(self, msg):
        # prefix a message with its length
        return struct.pack('>I', len(msg)) + msg

    def _onSocketConnected(self, socket):
        # start handshake
        msg = b'API\0'
        msg += self._prefix(b'v%d..%d' % (
                ibapi.server_versions.MIN_CLIENT_VER,
                ibapi.server_versions.MAX_CLIENT_VER))
        self.conn.sendMsg(msg)
        self.decoder = ibapi.decoder.Decoder(self.wrapper, None)

    def _onSocketHasData(self, socket, data):
        self._data += data

        while True:
            if len(self._data) <= 4:
                break
            # 4 byte prefix tells the message length
            msgEnd = 4 + struct.unpack('>I', self._data[:4])[0]
            if len(self._data) < msgEnd:
                # insufficient data for now
                break
            msg = self._data[4:msgEnd]
            self._data = self._data[msgEnd:]
            fields = msg.split(b'\0')
            fields.pop()  # pop off last empty element

            if not self.serverVersion_ and len(fields) == 2:
                # this concludes the handshake
                version, self.connTime = fields
                self.serverVersion_ = int(version)
                self.decoder.serverVersion = self.serverVersion_
                self.setConnState(EClient.CONNECTED)
                self.startApi()
                self.wrapper.connectAck()
            else:
                # decode and handle the message
                self.decoder.interpret(fields)


class TWSConnection:
    """
    Replacement for ibapi.connection.Connection that uses asyncio.
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.wrapper = None
        self.socket = None
        # the following are lists of callbacks for socket events
        self.hasData = []
        self.connected = []

    def connect(self):
        loop = asyncio.get_event_loop()
        coro = loop.create_connection(lambda: TWSSocket(self),
                self.host, self.port)
        _, self.socket = loop.run_until_complete(coro)
        for callback in self.connected:
            callback(self)

    def disconnect(self):
        self.socket.transport.close()
        self.socket = None

    def isConnected(self):
        return self.socket is not None

    def sendMsg(self, msg):
        self.socket.transport.write(msg)

    def addData(self, data):
        for callback in self.hasData:
            callback(self, data)


class TWSSocket(asyncio.Protocol):

    def __init__(self, twsConnection):
        self.transport = None
        self.twsConnection = twsConnection

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        print('Connection lost')

    def data_received(self, data):
        self.twsConnection.addData(data)


def isIBAPI(f):
    """
    Visual marker for methods implementing the IB API callbacks.
    """
    return f


class TWS(EWrapper, TWSClient):
    """
    Example to connect to a running Trader Work Station (TWS)
    from Interactive Brokers.
    """
    def __init__(self):
        TWSClient.__init__(self, self)
        self.accountName = ''
        self._reqIdSeq = 0
        self._reqId2Contract = {}

    def getReqId(self):
        """
        Get new request ID (integer).
        """
        assert self._reqIdSeq
        newId = self._reqIdSeq
        self._reqIdSeq += 1
        return newId

    def subscribe(self):
        for symbol in ('GOOG', 'TSLA', 'AAPL'):
            c = ibapi.contract.Contract()
            c.symbol = symbol
            c.secType = 'STK'
            c.currency = 'USD'
            c.exchange = 'SMART'
            reqId = self.getReqId()
            self._reqId2Contract[reqId] = c
            self.reqMktData(reqId, c, genericTickList='',
                    snapshot=False, mktDataOptions=[])

    @isIBAPI
    def connectAck(self):
        self.reqAccountUpdates(1, '')
        self.reqOpenOrders()
        self.reqPositions()

    @isIBAPI
    def nextValidId(self, reqId: int):
        self._reqIdSeq = reqId
        self.subscribe()

    @isIBAPI
    def tickPrice(self, reqId: int,
            tickType: ibapi.ticktype.TickType,
            price: float,
            attrib: ibapi.common.TickAttrib):
        contract = self._reqId2Contract[reqId]
        print('{} price {}'.format(contract.symbol, price))

    @isIBAPI
    def tickSize(self, reqId: int,
            tickType: ibapi.ticktype.TickType,
            size: int):
        contract = self._reqId2Contract[reqId]
        print('{} size {}'.format(contract.symbol, size))

    @isIBAPI
    def updateAccountTime(self, timeStamp: str):
        print('Time {}'.format(timeStamp))

    @isIBAPI
    def accountDownloadEnd(self, accountName: str):
        self.accountName = accountName

    @isIBAPI
    def updateAccountValue(self, key: str, val: str, currency: str,
            accountName: str):
        print('Account update: {} = {} {}'.format(key, val, currency))

    @isIBAPI
    def position(self, account: str,
            contract: ibapi.contract.Contract,
            position: float,
            avgCost: float):
        print('Position: {} {} @ {}'.format(position, contract.symbol, avgCost))

    @isIBAPI
    def positionEnd(self):
        pass


if __name__ == '__main__':
    tws = TWS()
    tws.connect(host='localhost', port=7496, clientId=1)
    loop = asyncio.get_event_loop()
    loop.run_forever()

