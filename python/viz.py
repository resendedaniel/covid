import os
import requests
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import transparencia
import oficial


colors = {
    2018: '#A6CEE3',
    2019: '#2377B4',
    2020: '#F57E0D',
    'excess': '#2377B4',
    'covid': '#9467BD'
}

FIRST_DEATH_D = dt.datetime(2020, 3, 17)

def calc_excess_death(covid_data):
    first_death_ord_d = covid_data.loc[covid_data['d'] == FIRST_DEATH_D, 'ord_d'].values[0]
    last_available_ord_d = covid_data.loc[covid_data['year'] == 2020, 'ord_d'].max()

    covid_days = covid_data[(covid_data['ord_d'] >= first_death_ord_d) & (covid_data['ord_d'] <= last_available_ord_d)]
    covid_days = covid_days.groupby('year')['deaths_daily_mean'].sum().to_dict()
    excess_deaths_abs = covid_days[2020] - covid_days[2019]
    excess_deaths_rel = excess_deaths_abs / covid_days[2019]

    return excess_deaths_abs, excess_deaths_rel, first_death_ord_d, last_available_ord_d

def calc_excess_area(covid_data):
    first_death_ord_d = covid_data.loc[covid_data['d'] == FIRST_DEATH_D, 'ord_d'].values[0]
    last_available_ord_d = covid_data.loc[covid_data['year'] == 2020, 'ord_d'].max()

    covid_days = covid_data[(covid_data['ord_d'] >= first_death_ord_d) & (covid_data['ord_d'] <= last_available_ord_d)]
    covid_2019 = covid_days.loc[covid_days['year'] == 2019, ['d', 'deaths_daily_mean']]
    covid_2019['d'] = covid_2019['d'].apply(lambda x: x.replace(year=2020))
    covid_2019 = covid_2019.rename(columns={'deaths_daily_mean':'2019_value'})
    covid_2020 = covid_days.loc[covid_days['year'] == 2020, ['ord_d', 'd', 'deaths_daily_mean']]
    covid_2020 = covid_2020.rename(columns={'deaths_daily_mean':'2020_value'})

    covid_days = pd.merge(covid_2019, covid_2020, on='d')

    return covid_days


def plot_deaths(covid_data, state):
    fig, ax = plt.subplots()

    for year in covid_data['year'].unique()[::-1]:
        sub = covid_data[covid_data['year'] == year]
        ax.plot(sub['d'].apply(lambda x: x.replace(year=2020)), sub['deaths_daily_mean'], label='Mortes por dia em {}'.format(year), c=colors[year])

    ax.set(ylabel='Mortes por dia')
    ax.set_ylim(ymin=0)

    excess_deaths_abs, excess_deaths_rel, start_ord_d, end_ord_d = calc_excess_death(covid_data)
    excess_deaths_abs = round(excess_deaths_abs/100) * 100

    min_x, max_x = ax.get_xlim()
    min_y, max_y = ax.get_ylim()
    excess_text = '{:.1%}'.format(excess_deaths_rel)
    if excess_deaths_rel > 0:
        excess_text = '+{}'.format(excess_text)

    ax.text(covid_data[covid_data['year'] == 2020]['d'].min(),
            max_y,
            excess_text,
            va='top',
            ha='left',
            fontsize=12,
            color=colors[2020])

    covid_days = calc_excess_area(covid_data)

    ax.fill_between(covid_days['d'], covid_days['2019_value'], covid_days['2020_value'], facecolor=colors[2020], alpha=.4)


    ax.set_xlim([dt.datetime(2020,1,1), dt.datetime(2020,12,31)])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=True)
    ax.tick_params(axis='y', which='both', right=False, left=False, labelleft=True)

    if state == 'all':
        state = 'Brasil'
    ax.set_title(state.upper())

    plt.show()

def plot_covid(data, state):
    df = data[data['year'] == 2020].copy()

    fig, ax = plt.subplots()

    plt.scatter(df['d'], df['covid_deaths_daily'], label='Notificação oficial de mortes por Covid', s=2, alpha=.5)
    plt.plot(df['d'], df['covid_deaths_daily_mean'], label='Média móvel mortes por Covid')
    plt.plot(df['d'], df['excess_mean'], label='Excesso de mortes de causas naturais em 2020')

    plt.legend()
    plt.title(state)

    plt.show()
