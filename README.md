# tws_async
Integrate the Python IB API from Interactive Brokers with asyncio.

## Unix
Unix users can use the tws_async.py script. It requires Python version >= 3.5 and the [Interactive Brokers API](http://interactivebrokers.github.io).

## Windows
Windows users are encouraged to use the tws_async_windows.py script that bypasses some reconnect issues. It requires two additional packages which can be installed as 
```
pip install PyQt5
pip install quamash
```
