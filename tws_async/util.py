import datetime
import logging
import signal

__all__ = ['dateRange', 'allowCtrlC', 'logToFile', 'logToConsole', 'LogFilter']


def dateRange(startDate, endDate, skipWeekend=True):
    """
    Iterate the days from given start date up to and including end date.
    """
    day = datetime.timedelta(days=1)
    date = startDate
    while True:
        if skipWeekend:
            while date.weekday() >= 5:
                date += day
        if date > endDate:
            break
        yield date
        date += day


def allowCtrlC():
    """
    Allow Control-C to end program.
    """
    signal.signal(signal.SIGINT, signal.SIG_DFL)


def logToFile(path, level=logging.INFO, ibapiLevel=logging.ERROR):
    """
    Create a log handler that logs to the given file.
    """
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addFilter(LogFilter('root', ibapiLevel))
    formatter = logging.Formatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s')
    handler = logging.FileHandler(path)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def logToConsole(level=logging.INFO, ibapiLevel=logging.ERROR):
    """
    Create a log handler that logs to the console.
    """
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addFilter(LogFilter('root', ibapiLevel))
    formatter = logging.Formatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class LogFilter(logging.Filter):
    """
    Filter log records from module with given name below a given level.
    """
    def __init__(self, name, level):
        logging.Filter.__init__(self)
        self.name = name
        self.level = level

    def filter(self, record):
        return record.name != self.name or record.levelno >= self.level
