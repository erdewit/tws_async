import ibapi.contract

__all__ = ['Contract', 'Stock', 'Option', 'Future', 'Forex', 'Index',
        'CFD', 'Commodity']


class Contract(ibapi.contract.Contract):
    """
    Simplify working with IBAPI contracts.
    """
    def __init__(self, **kwargs):
        ibapi.contract.Contract.__init__(self)
        for k, v in kwargs.items():
            setattr(self, k, v)


class Stock(Contract):
    def __init__(self, symbol='', primaryExchange='', exchange='SMART',
            currency='USD', **kwargs):
        Contract.__init__(self, secType='STK', symbol=symbol,
                primaryExchange=primaryExchange,
                exchange=exchange, currency=currency, **kwargs)


class Option(Contract):
    def __init__(self, symbol='', lastTradeDateOrContractMonth='',
            strike='', right='', multiplier=100, exchange='SMART',
            currency='USD', **kwargs):
        Contract.__init__(self, secType='OPT', symbol=symbol,
                lastTradeDateOrContractMonth=lastTradeDateOrContractMonth,
                strike=strike, right=right, multiplier=multiplier,
                exchange=exchange, currency=currency, **kwargs)


class Future(Contract):
    def __init__(self, symbol='', lastTradeDateOrContractMonth='',
            exchange='SMART', localSymbol='', multiplier='',
            currency='USD', **kwargs):
        Contract.__init__(self, secType='FUT', symbol=symbol,
                lastTradeDateOrContractMonth=lastTradeDateOrContractMonth,
                exchange=exchange, localSymbol=localSymbol,
                multiplier=multiplier, currency=currency, **kwargs)


class Forex(Contract):
    def __init__(self, pair='', exchange='IDEALPRO',
            symbol='', currency='', **kwargs):
        if pair:
            assert len(pair) == 6
            symbol = symbol or pair[:3]
            currency = currency or pair[3:]
        Contract.__init__(self, secType='CASH', symbol=symbol,
                exchange=exchange, currency=currency, **kwargs)


class Index(Contract):
    def __init__(self, symbol='', exchange='', currency='USD', **kwargs):
        Contract.__init__(self, secType='IND', symbol=symbol,
                exchange=exchange, currency=currency, **kwargs)


class CFD(Contract):
    def __init__(self, symbol='', exchange='SMART', currency='USD', **kwargs):
        Contract.__init__(self, secType='CFD', symbol=symbol,
                exchange=exchange, currency=currency, **kwargs)


class Commodity(Contract):
    def __init__(self, symbol='', exchange='', currency='USD', **kwargs):
        Contract.__init__(self, secType='CMDTY', symbol=symbol,
                exchange=exchange, currency=currency, **kwargs)

