import numpy as np
import datetime as dt
import pandas as pd
import calendar
import requests
import json
import glob


def download_year_month_data(start_date, end_date):
    print('Downloading {}'.format(start_date.strftime('%Y-%m')))
    url = 'https://transparencia.registrocivil.org.br/api/record/death?start_date={}&end_date={}'
    url = url.format(start_date.strftime('%Y-%m-%d'),
                     end_date.strftime('%Y-%m-%d'))

    res = requests.get(url)

    file_url = 'data/{}.json'.format(start_date.strftime('%Y-%m'))
    with open(file_url, 'w') as outfile:
        json.dump(res.json(), outfile)

def download_full_data():
    for year in np.arange(2020,2020+1):
        for month in np.arange(1,12+1):
            _, end_day = calendar.monthrange(year, month)
            start_date = dt.datetime(year, month, 1)
            end_date = dt.datetime(year, month, end_day)

            if start_date > dt.datetime.today():
                continue

            download_year_month_data(start_date, end_date)

def read_file(file):
    year = int(file[7:11])
    month = int(file[12:14])

    with open(file) as json_file:
        json_read = json.load(json_file)
        df = pd.DataFrame(json_read['data'])
        df['year'] = year
        df['month'] = month
        return df

def read_all_files():
    files = glob.glob('./data/*.json')
    files.sort()
    files = files[:-1]

    data = pd.DataFrame()
    for file in files:
        df = read_file(file)
        data = data.append(df)

    return data

if not len(glob.glob('./data/*.json')):
    download_full_data()

data = read_all_files()

import matplotlib.pyplot as plt
state = 'SC'

data['month_dec'] = data['year'] + data['month'] / 12
# data = data[data['name'] == state]
data = data.groupby(['year', 'month', 'month_dec'])[['total']].sum().reset_index()


fig, ax = plt.subplots(2)

ax[0].plot(data['month_dec'], data['total'])
ax[0].set(ylabel = 'Registros de óbitos mensal')

for year in data['year'].unique():
    sub = data[data['year'] == year]
    ax[1].plot(sub['month'], sub['total'], label=str(year))

ax[1].set(ylabel = 'Registros de óbitos de cada mês')
ax[1].legend(loc='lower center', ncol=len(data['year'].unique()))

plt.suptitle('Excesso de mortes {}'.format(state))

plt.show()
