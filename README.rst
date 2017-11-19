Notice
======

This project has evolved into `IB-insync <https://github.com/erdewit/ib_insync>`_
and all development is happening there now.

To port code:

* ``TWSClient`` has moved to ``ib_insync.client.Client`` (with much improvements);
* ``TWSClientQt``: The new ``Client`` can be used with PyQt and quamash.

Introduction
============

The ``tws_async`` package allows the Python API from Interactive Brokers (IBAPI)
to be used asynchronously and single-threaded with the
asyncio_ standard library or with the PyQt5_ framework.

This offers a simpler, safer and more performant approach to concurrency than
multithreading.


Installation
============

Install using pip::

    pip3 install -U tws_async

Note that on some systems the ``pip3`` command is just ``pip``.

Python_ version 3.5 or higher is required as well as the
`Interactive Brokers Python API`_.


Usage
=====

This package offers two clients that can be used as a drop-in replacement for
the standard EClient as provided by IBAPI:

* ``TWSClient``, for use with the asyncio event loop;
* ``TWSClientQt``, for use with the PyQt5 event loop.

These clients also inherit from ``ibapi.wrapper.EWrapper`` and can be used exactly
as one would use the standard IBAPI version. The asynchronous clients use
their own event-driven networking code that replaces the networking code
of the standard ``EClient``, and they also replace the infinite loop of
``EClient.run()`` with an event loop.

To simplify working with contracts, this package provides
``Contract``, ``Stock``, ``Option``, ``Future``, ``Forex``, ``Index``, ``CFD`` and ``Commodity``
classes that can be used anywhere where a ``ibapi.contract.Contract`` is expected.
Examples of some simple cases are
``Stock('AMD')``, ``Forex('EURUSD')``, ``CFD('IBUS30')`` or
``Future('ES', '201612', 'GLOBEX')``.
To specify more complex contracts, any property can be given as a keyword.

To learn more, consult the `official IBAPI documentation`_ or have a look at
these sample use cases:

Historical data downloader
--------------------------
The HistRequester_ downloads historical data and saves it to CSV files;
`histrequester demo`_ illustrates how to use it.

Realtime streaming ticks
------------------------
The `tick streamer`_ subscribes to realtime tick data.

Jupyter Notebook
----------------
To use the Interactive Brokers API fully interactively in a Jupyter notebook,
have a look at the `example notebook`_.

Jupyter can be started with the command ``jupyter notebook``.

This notebook uses the Qt version of the client, where the
Qt event loop is started with the ``%gui qt5`` directive at the very top.
It is not necessary to call the ``run()`` method of the client.

Notes on using asycio in a notebook
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Currently there does not seem to be a single-threaded way to directly run
the asyncio event loop in Jupyter. What can be done is to use the
Qt event loop (which does have good integration with the Jupyter kernel)
with the quamash_ adaptor. With quamash the Qt event loop is used to drive
the asyncio event loop. This can be done by placing the following code at
the top of the notebook:

.. code:: python

    %gui qt5
    import asyncio, quamash
    loop = quamash.QEventLoop()
    asyncio.set_event_loop(loop)

One thing that does not work in the combination of quamash and Jupyter is the
``loop.run_until_finished`` method. It can be patched like this:

.. code:: python

    def run_until_complete(self, future):
        future = asyncio.ensure_future(future)
        qApp = qt.QApplication.instance()
        while not future.done():
            qApp.processEvents(qt.QEventLoop.WaitForMoreEvents)
        return future.result()
    
    quamash.QEventLoop.run_until_complete = run_until_complete

The asyncio version of the client relies on ``loop.run_until_finished`` to connect
synchonously. So in order to run the asyncio client in the notebook, apply the patch
or just connect asynchonously (i.e. give asyncConnect=True to the connect call).

Changelog
=========

Version 0.5.7
-------------

* HistRequester fix for endDateTime formatting

Version 0.5.6
-------------

* HistRequester updated to version 9.73.04 of the API

Version 0.5.5
-------------
* small simplifications

Version 0.5.4
-------------
* connect() call of the clients will now by default block until client is ready to serve requests.
* getReqId() method added to both clients.
* dataHandlingPre() and dataHandlingPost() event hooks added to clients.
* logging added.
* util module aded.
* file tws_async.py renamed to twsclient.py, tws_asyncqt.py to twsclientqt.py.
 

Version 0.5.3
-------------
* Added optional ``asyncConnect`` argument to ``client.connect()`` method. The default is now to connect synchronously (block until connected).
* Fixed bug in HistRequester when downloading daily data.

Version 0.5.0
-------------
* Initial pip package release.

Good luck and enjoy,

:author: Ewald de Wit  <ewald.de.wit@gmail.com>

.. _asyncio: https://docs.python.org/3.6/library/asyncio.html
.. _PyQt5: https://pypi.python.org/pypi/PyQt5
.. _Python: http://www.python.org
.. _`Interactive Brokers Python API`: http://interactivebrokers.github.io
.. _`official IBAPI documentation`: https://interactivebrokers.github.io/tws-api/#gsc.tab=0
.. _quamash: https://github.com/harvimt/quamash
.. _`HistRequester`: https://github.com/erdewit/tws_async/blob/master/tws_async/histrequester.py
.. _`histrequester demo`: https://github.com/erdewit/tws_async/blob/master/samples/histrequester_demo.py
.. _`tick streamer`: https://github.com/erdewit/tws_async/blob/master/samples/tickstreamer_demo.py
.. _`example notebook`: https://github.com/erdewit/tws_async/blob/master/samples/tws.ipynb


