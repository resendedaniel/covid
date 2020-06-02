import requests
import json
import os
import datetime as dt
import pandas as pd

raw_filename = 'transparencia_cache/transparencia_{}.json'
processed_filename = 'html/data/transparencia_{}.json'

def check_cache(state):
    return os.path.exists(raw_filename.format(state))

def load_cache(state):
    print('fetching {} data from cache'.format(state))
    with open(raw_filename.format(state)) as json_file:
        data = json.load(json_file)
    return data

def save_cache(data, state):
    with open(raw_filename.format(state), 'w') as outfile:
        json.dump(data, outfile)

def save_processed(data, state):
    data = data.copy()
    data['d'] = data['d'].dt.strftime('%Y-%m-%d')
    data = data.to_json(processed_filename.format(state), orient='records')

def get_data(state='all'):
    if not check_cache(state):
        data = fetch_data(state=state)
        save_cache(data, state)
    else:
        data = load_cache(state)

    data = process_data(data, state)
    save_processed(data, state)

    return data


def fetch_data(state='all', start_date='2018-01-01', end_date=dt.datetime.today().strftime('%Y-%m-%d')):
    print('fetching {} data from transparencia.registrocivil.org.br'.format(state))
    client = requests.session()
    client.get('https://transparencia.registrocivil.org.br')
    xsrf_token = client.cookies['XSRF-TOKEN']

    url = 'https://transparencia.registrocivil.org.br/api/covid-covid-registral?start_date={}&end_date={}&state={}&chart=chart5&places[]=HOSPITAL&places[]=DOMICILIO&places[]=VIA_PUBLICA&places[]=OUTROS'
    if state != 'all':
        state = state.upper()
    url = url.format(start_date, end_date, state)
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'transparencia.registrocivil.org.br',
        'Referer': 'https://transparencia.registrocivil.org.br/registral-covid',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'X-XSRF-TOKEN': xsrf_token,
    }

    res = requests.get(url, headers=headers)

    if res.ok:
        data = res.json()['chart']
        return data
    else:
        print(res, res.text)
        raise ValueError()


def process_data(data, state, cutoff=14):
    values = []
    for key, row in data.items():
        for x in row.values():
            values.append({'d': key, 'type': x[0]['tipo_doenca'], 'value': int(x[0]['total'])})

    df = pd.DataFrame(values)
    df['d'] = pd.to_datetime(df['d'], dayfirst=True)

    all = df.groupby('d')['value'].sum().reset_index()
    all = all.sort_values('d')
    all['value'] = all['value'].rolling(7, min_periods=1).mean()

    all['year'] = [x.year for x in all['d']]
    all['ord_d'] = all.groupby('year').cumcount()
    all['cumvalue'] = all.groupby('year')[['value']].cumsum()
    all['state'] = state

    if state in ['rj', 'mt', 'all']:
        all = all[all['d'] >= dt.datetime(2018,9,1)]
    if state == 'pr':
        all = all[all['d'] >= dt.datetime(2018,4,1)]

    all = all[:-cutoff]

    return all

def download_all_data(cutoff=14):
    states = [
        'rs', 'sc', 'pr', 'se',
        'sp', 'mg', 'es', 'rj',
        'ms', 'mt', 'go', 'df',
        'ac', 'am', 'pa', 'rr', 'ro', 'ap', 'to',
        'ba', 'se', 'al', 'pe', 'pb', 'rn', 'ce', 'ma', 'pi',
        'all'
    ]
    for state in states:
        raw_data = fetch_data(state)
        data = process_data(raw_data, state, cutoff=cutoff)
        save_cache(raw_data, state)
        save_processed(data, state)