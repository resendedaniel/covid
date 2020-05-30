import os
import requests
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import portal_transparencia as transp
import oficial


FIRST_DEATH_D = dt.datetime(2020,3,17)
STATES = {
    's': ['rs', 'sc', 'pr'],
    'se': ['sp', 'mg', 'es', 'rj'],
    'co': ['ms', 'mt', 'go', 'df'],
    'n': ['ac', 'am', 'pa', 'rr', 'ro', 'ap', 'to'],
    'ne': ['ba', 'se', 'al', 'pe', 'pb', 'rn', 'ce', 'ma', 'pi'],
    'brasil': ['all'],
    'worst': ['am', 'pa', 'ce', 'pe', 'sp', 'rj', 'ma']
}
REGION_NAME = {
    's': 'Região Sul',
    'se': 'Região Sudeste',
    'co': 'Região Centro-Oeste',
    'n': 'Região Norte',
    'ne': 'Região Nordeste',
    'brasil': 'Brasil',
    'worst': 'Piores estados',
}
for x in STATES.values():
    x.sort()

def create_dirs():
    for d in ['data', 'processed_data', 'img']:
        try:
            os.makedirs(d)
        except OSError as e:
            continue

def calc_excess_death(covid_data):
    first_death_ord_d = covid_data.loc[covid_data['d'] == FIRST_DEATH_D, 'ord_d'].values[0]
    last_available_ord_d = covid_data.loc[covid_data['year'] == 2020, 'ord_d'].max()

    covid_days = covid_data[(covid_data['ord_d'] >= first_death_ord_d) & (covid_data['ord_d'] <= last_available_ord_d)]
    covid_days = covid_days.groupby('year')['value'].sum().to_dict()
    excess_deaths_abs = covid_days[2020] - covid_days[2019]
    excess_deaths_rel = excess_deaths_abs / covid_days[2019]

    return excess_deaths_abs, excess_deaths_rel, first_death_ord_d, last_available_ord_d

def calc_excess_area(covid_data):
    first_death_ord_d = covid_data.loc[covid_data['d'] == FIRST_DEATH_D, 'ord_d'].values[0]
    last_available_ord_d = covid_data.loc[covid_data['year'] == 2020, 'ord_d'].max()

    covid_days = covid_data[(covid_data['ord_d'] >= first_death_ord_d) & (covid_data['ord_d'] <= last_available_ord_d)]
    covid_2019 = covid_days.loc[covid_days['year'] == 2019, ['d', 'value']]
    covid_2019['d'] = covid_2019['d'].apply(lambda x: x.replace(year=2020))
    covid_2019 = covid_2019.rename(columns={'value':'2019_value'})
    covid_2020 = covid_days.loc[covid_days['year'] == 2020, ['ord_d', 'd', 'value']]
    covid_2020 = covid_2020.rename(columns={'value':'2020_value'})

    covid_days = pd.merge(covid_2019, covid_2020, on='d')

    return covid_days

def plot_single_state(covid_data, state, ax):
    colors = {
        2018: '#A6CEE3',
        2019: '#2377B4',
        2020: '#F57E0D',
        'excess': '#2377B4',
        'covid': '#9467BD'
    }

    # covid_data['value'] = covid_data['value'].rolling(7).mean()
    for year in covid_data['year'].unique()[::-1]:
        sub = covid_data[covid_data['year'] == year]
        ax.plot(sub['d'].apply(lambda x: x.replace(year=2020)), sub['value'], label='Mortes por dia em {}'.format(year), c=colors[year])

    ax.set(ylabel='Mortes por dia')
    # ax.set_ylim(ymin=0)

    excess_deaths_abs, excess_deaths_rel, start_ord_d, end_ord_d = calc_excess_death(covid_data)
    excess_deaths_abs = round(excess_deaths_abs/100) * 100

    min_x, max_x = ax.get_xlim() # covid_data['d'].values[-1]
    min_y, max_y = ax.get_ylim() # covid_data['value'].values[-1] / (1 + excess_deaths_rel * .75)
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
    # ax.text(min_x,
    #         max_y - (max_y - min_y) *.25,
    #         'Desde 17/03/2020\nprimeira morte por Covid19')

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

    return ax

def plot_region(region, show=True):
    global STATES, REGION_NAME
    n = len(STATES[region])

    print(region, n)
    ncols = int((n+1) ** .5)
    fig, axs = plt.subplots(int(np.ceil(n/ncols)),
                            ncols=ncols,
                            sharex=True,
                            gridspec_kw = {'wspace':.15, 'hspace':.15},
                            figsize=(10.8, 10.8))
    loci = int(np.ceil(n/ncols)) * ncols
    for i in np.arange(loci)[n:]:
        fig.delaxes(axs.flatten()[i])

    for ax, i in zip(fig.get_axes()[:n], np.arange(n)):
        state = STATES[region][i]
        covid_data = transp.get_data(state)

        ax = plot_single_state(covid_data, state, ax)
        # axs[int(i/ncols), i%ncols] = plot_single_state(covid_data, state, axs[int(i/ncols), i%ncols])

    fig.get_axes()[0].legend(loc="upper right")

    for ax in fig.get_axes()[:-ncols]:
        for label in ax.get_xticklabels(which="both"):
            label.set_visible(False)
        ax.get_xaxis().get_offset_text().set_visible(False)
        ax.set_xlabel("")
    for i in np.arange(n):
        if i % ncols > 0:
            # for label in fig.get_axes()[i].get_yticklabels(which="both"):
            #     label.set_visible(False)
            fig.get_axes()[i].get_yaxis().get_offset_text().set_visible(False)
            fig.get_axes()[i].set_ylabel("")

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, bbox_to_anchor=(2, 0),loc = 'lower right')
    plt.suptitle('Excesso de mortes por doenças respiratórias\n{}'.format(REGION_NAME[region]), fontsize=16)
    footnote = 'Fonte: Portal Transparência\nDados até {} | Atualizado em {}\nOs cartórios demoram até 3 semanas para informar os dados\nTwitter: @resende451'.format(covid_data['d'].max().strftime('%Y-%m-%d'), dt.datetime.today().strftime('%Y-%m-%d'))
    plt.figtext(.95,0.1, footnote, fontsize=10, va="top", ha="right")

    # plt.tight_layout()
    # plt.savefig('img/{}.png'.format(region), dpi=100)
    # plt.show()


create_dirs()
plot_region('worst', show=True)
plot_region('brasil', show=True)
plot_region('s', show=True)
plot_region('se', show=True)
plot_region('co', show=True)
plot_region('ne', show=True)
plot_region('n', show=True)
