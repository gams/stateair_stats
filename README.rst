#####################################################
Stateair stats - statistics on PM2.5 history in China
#####################################################

Data source
===========

All data was obtained from: http://www.stateair.net/

Data
====

To get the script to run, you need to download the csv files from the data source and put them in folders named as follow: ``_data/<cityname>``

For example, the Shanghai data should be in ``_data/shanghai``

After the source files have been downloaded, remove the comments in the first
lines of the files.

Install
=======

Get the code:

.. code-block:: sh

    $ git clone git@github.com:gams/stateair_stats.git

Install needed packages:

.. code-block:: sh

    $ pip install -r requirements.txt

Usage
=====

.. code-block:: sh

    $ python data_stats.py

or 

.. code-block:: sh

    $ python data_stats.py beijing

It will create a PNG file in the ``_data`` folder.
