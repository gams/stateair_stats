# -*- coding: utf-8 -*-
import argparse
import datetime
import glob
import os
import os.path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATA_FILES = [
    '_data/shanghai/Shanghai_2011_HourlyPM25_created20140423.csv',
    '_data/shanghai/Shanghai_2012_HourlyPM25_created20140423.csv',
    '_data/shanghai/Shanghai_2013_HourlyPM25_created20140423.csv',
    '_data/shanghai/Shanghai_2014_HourlyPM25_created20150203.csv',
    '_data/shanghai/Shanghai_2015_HourlyPM25_created20150901.csv',
]

EPA_BP = {
    'good': (0, 12),
    'moderate': (12.1, 35.4),
    'unhealthy_sensitive': (35.5, 55.4),
    'unhealthy': (55.5, 150.4),
    'very_unhealthy': (150.5, 250.4),
    'hazardous': (250.5, 500.4),
}

DATAROOT = '_data'
DEFAULT_CITY = 'shanghai'
AQI_BP = EPA_BP
START_YEAR = -1
END_YEAR = -1


def src_process(data, source):
    """Process a CSV file from stateair, return month-ly aggregated data with
counts for each AQI level.

.. warning:: undefined data is simply dropped
    """
    df = pd.read_csv(source, usecols=[2, 7, 10], index_col=0,
                     parse_dates=True,
                     na_values=['-999', '-1']).dropna()

    for chunk in df.itertuples():
        ts = chunk[0]
        pm25 = chunk[1]
        monthdt = datetime.date(ts.year, ts.month, 1)
        if monthdt not in data:
            data[monthdt] = {
                'good': 0,
                'moderate': 0,
                'unhealthy_sensitive': 0,
                'unhealthy': 0,
                'very_unhealthy': 0,
                'hazardous': 0,
                'out_of_scale': 0,
            }
    
        match = False
        for (name, bp) in AQI_BP.items():
            if pm25 >= bp[0] and pm25 <= bp[1]:
                match = True
                data[monthdt][name] += 1
                break
        if match is False:
            data[monthdt]['out_of_scale'] += 1

def year_range(data):
    y_range = []
    for date in data.keys():
        if date.year not in y_range:
            y_range.append(date.year)
    y_range.sort()
    return y_range


def get_datasets(data):
    datasets = {}
    for year in year_range(data):
        if year not in datasets:
            datasets[year] = {
                'months': [],
                'good': [],
                'moderate': [],
                'unhealthy_sensitive': [],
                'unhealthy': [],
                'very_unhealthy': [],
                'hazardous': [],
                'out_of_scale': [],
            }
        for month in range(1, 13):
            date = datetime.date(year, month, 1)
            if date in data:
                datasets[year]['months'].append(month)
                datasets[year]['good'].append(data[date]['good'])
                datasets[year]['moderate'].append(data[date]['moderate'])
                datasets[year]['unhealthy_sensitive'].append(data[date]['unhealthy_sensitive'])
                datasets[year]['unhealthy'].append(data[date]['unhealthy'])
                datasets[year]['very_unhealthy'].append(data[date]['very_unhealthy'])
                datasets[year]['hazardous'].append(data[date]['hazardous'])
                datasets[year]['out_of_scale'].append(data[date]['out_of_scale'])
            else:
                datasets[year]['months'].append(month)
                datasets[year]['good'].append(0)
                datasets[year]['moderate'].append(0)
                datasets[year]['unhealthy_sensitive'].append(0)
                datasets[year]['unhealthy'].append(0)
                datasets[year]['very_unhealthy'].append(0)
                datasets[year]['hazardous'].append(0)
                datasets[year]['out_of_scale'].append(0)
    return datasets

def plot_stacked_bars(data, city):
    datasets = get_datasets(data)
    N = 12
    width = 0.9 / len(datasets.keys())
    fig, ax = plt.subplots()
    offset = 0
    for year in datasets:
        ind = np.arange(N) + 0.05 + width * offset
        ax.bar(ind, datasets[year]['good'], width, color='#00e400')
        btm = np.array(datasets[year]['good'])
        ax.bar(ind, datasets[year]['moderate'], width, bottom=btm,
               color='#ffff00')
        btm += np.array(datasets[year]['moderate'])
        ax.bar(ind, datasets[year]['unhealthy_sensitive'], width,
               bottom=btm, color='#ff7e00')
        btm += np.array(datasets[year]['unhealthy_sensitive'])
        ax.bar(ind, datasets[year]['unhealthy'], width, bottom=btm,
               color='#ff0000')
        btm += np.array(datasets[year]['unhealthy'])
        ax.bar(ind, datasets[year]['very_unhealthy'], width, bottom=btm,
               color='#99004c')
        btm += np.array(datasets[year]['very_unhealthy'])
        ax.bar(ind, datasets[year]['hazardous'], width, bottom=btm,
               color='#7e0023')
        btm += np.array(datasets[year]['hazardous'])
        ax.bar(ind, datasets[year]['out_of_scale'], width, bottom=btm,
               color='#000000')
        offset += 1
    ax.set_ylabel(u'PM2.5 (µg/m³)')
    dates = datasets.keys()
    dates.sort()
    ax.set_title('Stateair PM2.5 concentration from {} to {} ({})'.format(
        dates[0], dates[-1], city))

    ax.set_xticks(np.arange(N) + 0.05 + width * 2)
    ax.set_xticklabels( ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec') )


if __name__ == '__main__':
    if os.path.isdir(DATAROOT) is False:
        sys.stderr.write("data folder not found ({})\n".format(DATAROOT))
        sys.exit(1)
    parser = argparse.ArgumentParser(description='stateair stats')
    parser.add_argument('city', nargs='?', default=DEFAULT_CITY,
                        help='city to process')
    args = parser.parse_args()

    datafolder = os.path.join(DATAROOT, args.city.lower())
    if os.path.isdir(datafolder) is False:
        sys.stderr.write("city data folder not found ({})\n".format(datafolder))
        sys.exit(1)

    datasources = glob.glob(os.path.join(datafolder, '*.csv'))
    if len(datasources) == 0:
        sys.stdout.write("no CSV file found in the data folder ({})\n".format(datafolder))
        sys.exit(0)

    data = {}
    for source in datasources:
        src_process(data, source)

    plot_stacked_bars(data, args.city)
    plt.savefig(os.path.join(DATAROOT, 'stateair-{}-{}.png'.format(
        args.city.lower(),
        datetime.datetime.now().strftime('%Y%m%d%H%M%S'))))
