import requests
import json
import os
import datetime as dt
import pandas as pd

raw_filename = 'transparencia_cache/transparencia_{}.json'
processed_filename = '../html/data/transparencia_{}.json'

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

    output = {
        'last_date': data['d'].max().isoformat(),
        'updated_date': dt.datetime.today().isoformat()
    }

    data['d'] = data['d'].dt.strftime('%Y-%m-%d')
    output['data'] = [ v.dropna().to_dict() for k,v in data.iterrows() ]

    with open(processed_filename.format(state), 'w') as fp:
        json.dump(output, fp)

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

    if state in ['rj', 'mt', 'all']:
        df = df[df['d'] >= dt.datetime(2018,9,1)]
    if state == 'pr':
        df = df[df['d'] >= dt.datetime(2018,4,1)]

    df = df.groupby('d')['value'].sum().reset_index()
    df = df.sort_values('d')
    df['value'] = df['value'].rolling(7, min_periods=1).mean()

    df['year'] = [x.year for x in df['d']]
    df['ord_d'] = df.groupby('year').cumcount()


    df_2020 = df[df['year'] == 2020][['ord_d', 'year', 'value']].rename(columns={'value':'value_2020'}).copy()
    df_2019 = df[df['year'] == 2019][['ord_d', 'value']].rename(columns={'value':'value_2019'}).copy()
    df_excess = pd.merge(df_2020, df_2019, on='ord_d', how='left')
    df_excess['excess'] = df_excess['value_2020'] - df_excess['value_2019']
    df_excess['cum_excess'] = df_excess['excess'].cumsum()
    df_excess = df_excess[['ord_d', 'year', 'excess', 'cum_excess']]

    df = pd.merge(df, df_excess, on=['ord_d', 'year'], how='left')

    df = df[:-cutoff]

    df['state'] = state

    return df

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
