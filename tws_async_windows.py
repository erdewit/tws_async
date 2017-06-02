import sys
import asyncio

import PyQt5.Qt as qt
import quamash
from tws_async import TWSClient, iswrapper

# plug the Qt event loop into asyncio
qApp = qt.QApplication(sys.argv)
loop = quamash.QEventLoop()
asyncio.set_event_loop(loop)


class TWS(TWSClient):
    """
    Example to connect to a running Trader Work Station (TWS)
    from Interactive Brokers.
    """
    def __init__(self):
        TWSClient.__init__(self)

    @iswrapper
    def connectAck(self):
        self.reqAccountUpdates(1, '')

    @iswrapper
    def updateAccountValue(self, key: str, val: str, currency: str,
            accountName: str):
        print('Account update: {} = {} {}'.format(key, val, currency))


if __name__ == '__main__':
    tws = TWS()
    tws.connect(host='127.0.0.1', port=7497, clientId=1)
    loop.call_later(5, loop.stop)
    loop.run_forever()
