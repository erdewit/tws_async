import struct
import asyncio
import logging

import ibapi
from ibapi.client import EClient
from ibapi.wrapper import EWrapper, iswrapper

import tws_async.util as util

__all__ = ['TWSClient', 'TWSException', 'iswrapper']


class TWSException(Exception):
    pass


class TWSClient(EWrapper, EClient):
    """
    Modification of EClient that uses the event loop from asyncio.
    """
    def __init__(self):
        self.readyEvent = asyncio.Event()
        EClient.__init__(self, wrapper=self)
        self._logger = logging.getLogger(__class__.__name__)

    def reset(self):
        EClient.reset(self)
        self.readyEvent.clear()
        self._data = b''
        self._reqIdSeq = 0

    def run(self, coro=None):
        """
        Per default run the asyncio event loop forever.
        If a coroutine is given then run it until completion.
        """
        loop = asyncio.get_event_loop()
        if coro is None:
            loop.run_forever()
        else:
            loop.run_until_complete(coro)

    def connect(self, host, port, clientId, asyncConnect=False):
        self._logger.info('Connecting to {}:{} with clientId {}...'.
                format(host, port, clientId))
        self.host = host
        self.port = port
        self.clientId = clientId
        self.setConnState(EClient.CONNECTING)
        self.conn = TWSConnection(host, port)
        self.conn.connected = self._onSocketConnected
        self.conn.connectionLost = self._onSocketConnectionLost
        self.conn.hasData = self._onSocketHasData
        connect_future = self.conn.connect()
        if not asyncConnect:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.gather(connect_future,
                    self.readyEvent.wait()))

    def getReqId(self) -> int:
        """
        Get new request ID.
        """
        assert self._reqIdSeq
        newId = self._reqIdSeq
        self._reqIdSeq += 1
        return newId

    def dataHandlingPre(self):
        pass

    def dataHandlingPost(self):
        pass

    def _prefix(self, msg):
        # prefix a message with its length
        return struct.pack('>I', len(msg)) + msg

    def _onSocketConnected(self):

        # start handshake
        msg = b'API\0'
        msg += self._prefix(b'v%d..%d' % (
                ibapi.server_versions.MIN_CLIENT_VER,
                ibapi.server_versions.MAX_CLIENT_VER))
        self.conn.sendMsg(msg)
        self.decoder = ibapi.decoder.Decoder(self.wrapper, None)

    def _onSocketConnectionLost(self):
        self._logger.error('Connection lost')

    def _onSocketHasData(self, data):
        self.dataHandlingPre()
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
                self._logger.info('Logged on to server version {}'.
                        format(self.serverVersion_))
            else:
                # snoop for next valid id response,
                # it signals readiness of the client
                if fields[0] == b'9':
                    _, _, validId = fields
                    self._reqIdSeq = int(validId)
                    self.readyEvent.set()

                # decode and handle the message
                self.decoder.interpret(fields)

        self.dataHandlingPost()


class TWSConnection:
    """
    Replacement for ibapi.connection.Connection that uses asyncio.
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.wrapper = None
        self.socket = None
        # the following are callbacks for socket events
        self.hasData = None
        self.connected = None
        self.connectionLost = None

    def _onConnectionCreated(self, future):
        _, self.socket = future.result()
        self.connected()

    def connect(self) -> asyncio.Future:
        loop = asyncio.get_event_loop()
        coro = loop.create_connection(lambda: TWSSocket(self),
                self.host, self.port)
        future = asyncio.ensure_future(coro)
        future.add_done_callback(self._onConnectionCreated)
        return future

    def disconnect(self):
        self.socket.transport.close()
        self.socket = None

    def isConnected(self):
        return self.socket is not None

    def sendMsg(self, msg):
        self.socket.transport.write(msg)


class TWSSocket(asyncio.Protocol):

    def __init__(self, twsConnection):
        self.transport = None
        self.twsConnection = twsConnection

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.twsConnection.connectionLost()

    def data_received(self, data):
        self.twsConnection.hasData(data)



class TWS_Test(TWSClient):
    """
    Test to connect to a running TWS or gateway server.
    """
    def __init__(self):
        TWSClient.__init__(self)

    @iswrapper
    def updateAccountValue(self, key: str, val: str, currency: str,
            accountName: str):
        print('Account update: {} = {} {}'.format(key, val, currency))


if __name__ == '__main__':
    util.logToConsole()
    tws = TWS_Test()
    tws.connect(host='127.0.0.1', port=7497, clientId=1)
    tws.reqAccountUpdates(1, '')
    tws.run()

