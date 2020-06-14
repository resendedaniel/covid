import requests
import json
import os
import datetime as dt
import pandas as pd

raw_filename = 'cache/transparencia_{}.json'
processed_filename = '../html/data/transparencia_{}.json'

def check_cache(state):
    filename = raw_filename.format(state)
    if os.path.exists(filename):
        return (dt.datetime.today() - dt.datetime.fromtimestamp(os.path.getmtime(filename))).seconds < 12*60*60
    else:
        return False


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
            values.append({'d': key, 'type': x[0]['tipo_doenca'], 'deaths_daily': int(x[0]['total'])})

    df = pd.DataFrame(values)
    df['d'] = pd.to_datetime(df['d'], dayfirst=True)

    if state in ['rj', 'mt', 'all']:
        df = df[df['d'] >= dt.datetime(2018,9,1)]
    if state == 'pr':
        df = df[df['d'] >= dt.datetime(2018,4,1)]

    df = df.groupby('d')['deaths_daily'].sum().reset_index()
    df = df.sort_values('d')
    df['year'] = [x.year for x in df['d']]
    df['ord_d'] = df.groupby('year').cumcount()

    df['deaths_daily_mean'] = df['deaths_daily'].rolling(7, min_periods=1).mean()
    df['deaths_cum'] = df.groupby('year')[['deaths_daily']].cumsum()

    df = df[:-cutoff]

    df['state'] = state

    df = df[['state', 'year', 'ord_d', 'd', 'deaths_daily', 'deaths_daily_mean', 'deaths_cum']]

    return df

def bind_excess(df):
    df_2020 = df[df['year'] == 2020][['ord_d', 'year', 'deaths_daily']].rename(columns={'deaths_daily':'deaths_daily_2020'}).copy()
    df_2019 = df[df['year'] == 2019][['ord_d', 'deaths_daily']].rename(columns={'deaths_daily':'deaths_daily_2019'}).copy()
    df_excess = pd.merge(df_2020, df_2019, on='ord_d', how='left')
    df_excess['excess'] = df_excess['deaths_daily_2020'] - df_excess['deaths_daily_2019']
    df_excess['excess_cum'] = df_excess['excess'].cumsum()
    df_excess = df_excess[['ord_d', 'year', 'excess', 'excess_cum']]

    df = pd.merge(df, df_excess, on=['ord_d', 'year'], how='left')

    return df

def bind_oficial_data(df, of_data, state):
    of_data_subset = of_data[of_data['state'] == state]
    of_data_subset = of_data_subset.drop('state', axis=1)
    df = pd.merge(df, of_data_subset, on='d', how='left')

    return df
