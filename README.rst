# tws_async
Integrate the Python IB API from Interactive Brokers with an event loop.
This allows the API to be used asynchonously within a single-threaded
application.

[Python](http://www.python.org) version >= 3.5 is required as well as the
[Interactive Brokers API](http://interactivebrokers.github.io).

## asyncio event loop
[tws_async.py](tws_async.py)
uses the native event loop from the
[asyncio](https://docs.python.org/3.5/library/asyncio.html)
standard library.

#### For Windows users:
While the regular asyncio script work on Windows too, there is an issue when trying to reconnect to
the TWS/gateway application; It will leave the API port of the TWS/gateway application 
in an unresponsive state. The [tws_async_windows.py](tws_async_windows.py) script
bypasses this issue, but requires some additional dependencies. These dependencies can
be installed as:
```
pip install --upgrade PyQt5 quamash
```

## PyQt5 event loop
The [tws_async_qt.py](tws_async_qt.py) script uses the PyQt5 event loop. To install PyQt5:
```
pip install --upgrade PyQt5
```

## Jupyter Notebook
As an example of how to use the Interactive Brokers API in a fully interactive way inside a Jupyter notebook,
have a look at the [example notebook](tws.ipynb). To run it, download [this script](tws_async_qt.py)
as well and place it in the same directory as the notebook.

To install Jupyter as well as everything that is used in the notebook:
```
pip install --upgrade jupyter numpy pandas seaborn PyQt5 quamash
```
Note that on some systems the `pip` command for Python 3 is called `pip3`. Jupyter can be started with the command
```
jupyter notebook
```

