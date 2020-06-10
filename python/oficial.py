import requests
import pandas as pd

def get_data():
    url = 'https://radar-covid-19-data.s3.amazonaws.com/data/covid-cases.json'

    res = requests.get(url)
    data = res.json()['data']

    return data

def process_data(data):
    data = pd.DataFrame(data)
    data = data.rename(columns={
        'id': 'state',
        'date': 'd',
        'cases': 'covid_cases_cum',
        'deaths': 'covid_deaths_cum'
    })
    data = data[['d', 'state', 'covid_deaths_cum']]
    data['state'] = data['state'].str.lower()
    data['state'] = data['state'].replace('brasil', 'all')
    data = data[data['covid_deaths_cum'] > 0]
    data['d'] = pd.to_datetime(data['d'])
    data = data.sort_values(['state', 'd'])
    data['covid_deaths_daily'] = data.groupby('state')[['covid_deaths_cum']].diff().fillna(0)
    data['covid_deaths_daily_mean'] = data['covid_deaths_daily'].rolling(7, min_periods=1).mean()

    return data
