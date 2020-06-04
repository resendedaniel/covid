import requests
import pandas as pd

def get_data():
    url = 'https://radar-covid-19-data.s3.amazonaws.com/data/covid-cases.json'

    res = requests.get(url)
    data = res.json()['data']

    data_br = [x for x in data if x['id'] == 'BRASIL']
    data_br = pd.DataFrame(data_br)
    data_br['d'] = pd.to_datetime(data_br['date'])
    data_br = data_br.sort_values('d')
    data_br = data_br[['d', 'cases', 'deaths']]
    data_br['new_cases'] = data_br['cases'].diff()
    data_br['new_deaths'] = data_br['deaths'].diff()

    return data_br
