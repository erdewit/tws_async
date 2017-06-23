import sys
import struct
import logging

import ibapi
from ibapi.client import EClient
from ibapi.wrapper import EWrapper, iswrapper

import PyQt5.Qt as qt
import PyQt5.QtNetwork as qtnetwork

import tws_async.util as util

util.allowCtrlC()

__all__ = ['TWSClientQt', 'iswrapper']


class TWSClientQt(EWrapper, EClient):
    """
    Version of ibapi.client.EClient that integrates with the Qt event loop.
    """
    def __init__(self):
        EClient.__init__(self, wrapper=self)
        self.qApp = qt.QApplication.instance() or qt.QApplication(sys.argv)
        self.readyTrigger = Trigger()
        self._logger = logging.getLogger(__class__.__name__)

    def reset(self):
        EClient.reset(self)
        self._data = b''
        self._reqIdSeq = 0

    def run(self):
        self.qApp.exec_()

    def connect(self, host, port, clientId, asyncConnect=False):
        self._logger.info('Connecting to {}:{} with clientId {}...'.
                format(host, port, clientId))
        self.host = host
        self.port = port
        self.clientId = clientId
        self.conn = TWSConnection(host, port)
        self.conn.connect()
        self.conn.socket.connected.connect(self._onSocketConnected)
        self.conn.socket.disconnected.connect(self._onSocketDisonnected)
        self.conn.socket.readyRead.connect(self._onSocketReadyRead)
        self.conn.socket.error.connect(self._onSocketError)
        self.setConnState(EClient.CONNECTING)
        if not asyncConnect:
            self.readyTrigger.wait()

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

    def _onSocketDisonnected(self):
        EClient.disconnect(self)

    def _onSocketError(self, socketError):
        if self.conn.socket:
            self._logger.error(self.conn.socket.errorString())

    def _onSocketReadyRead(self):
        self.dataHandlingPre()
        self._data += bytes(self.conn.socket.readAll())

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
                    self.readyTrigger.go()

                # decode and handle the message
                self.decoder.interpret(fields)

        self.dataHandlingPost()


class TWSConnection:
    """
    Replacement for ibapi.connection.Connection that uses a QTcpSocket.
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        self.socket = qtnetwork.QTcpSocket()
        # set TCP_NODELAY (disable Nagle's algorithm)
        self.socket.setSocketOption(
                qtnetwork.QAbstractSocket.LowDelayOption, True)
        self.socket.connectToHost(self.host, self.port)

    def disconnect(self):
        self.socket.close()
        self.socket = None

    def isConnected(self):
        return self.socket is not None

    def sendMsg(self, msg):
        self.socket.write(msg)
        self.socket.flush()


class Trigger(qt.QObject):
    """
    Wait synchronously on a trigger.
    """
    trigger = qt.pyqtSignal()

    def __init__(self):
        qt.QObject.__init__(self)

    def go(self):
        self.trigger.emit()

    def wait(self, timeout=5000):
        spy = qt.QSignalSpy(self.trigger)
        spy.wait(timeout)


class TWS_TestQt(TWSClientQt):
    """
    Test to connect to a running TWS or gateway server.
    """
    def __init__(self):
        TWSClientQt.__init__(self)

    @iswrapper
    def updateAccountValue(self, key: str, val: str, currency: str,
            accountName: str):
        print('Account update: {} = {} {}'.format(key, val, currency))


if __name__ == '__main__':
    util.logToConsole()
    tws = TWS_TestQt()
    tws.connect(host='127.0.0.1', port=7497, clientId=1)
    tws.reqAccountUpdates(1, '')
    tws.run()
