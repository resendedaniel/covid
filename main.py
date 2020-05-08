import numpy as np
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

url = 'https://dev.api.covid19.nguy.dev/?q=p2'

res = requests.get(url)

raw_deaths = res.json()['deaths']

deaths = pd.DataFrame()
for loc in raw_deaths['locations']:
    curr_df = pd.DataFrame()
    curr_df['d'] = loc['history'].keys()
    curr_df['d'] = pd.to_datetime(curr_df['d'])
    curr_df['deaths'] = loc['history'].values()
    curr_df['country'] = loc['country']
    curr_df['province'] = loc['province']

    deaths = pd.concat([deaths, curr_df])

deaths = deaths.groupby(['country', 'd']).sum().reset_index()
deaths['daily_deaths'] = deaths.groupby('country')['deaths'].diff()
deaths['daily_deaths'] = deaths['daily_deaths'].fillna(deaths['deaths'])


max_deaths = deaths.groupby('country')['deaths'].max().to_dict()
deaths['max_deaths'] = deaths['country'].map(max_deaths)

global_deaths = deaths.groupby('d')[['deaths', 'daily_deaths']].sum().reset_index()
global_deaths['deahts_growth'] = global_deaths['daily_deaths'].diff().fillna(
    global_deaths['daily_deaths'])
global_deaths['deahts_growth'] = global_deaths['deahts_growth'] / \
    (global_deaths['daily_deaths'] - global_deaths['deahts_growth'])
global_deaths['deahts_growth'] = global_deaths['deahts_growth'] * \
    (global_deaths['daily_deaths'] > 200)

fig, (ax1, ax2) = plt.subplots(2)
plt.suptitle('Covid19 Global Deaths')

ax1.bar(global_deaths['d'], global_deaths['daily_deaths'])
ax1.set(ylabel='Daily deaths')
ax1.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
ax1.spines['top'].set_visible(False)
ax1.spines['bottom'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_visible(False)
ax1.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=True)
ax1.tick_params(axis='y', which='both', right=False, left=False, labelleft=True)
ax1.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, pos: '{0:g}k'.format(x/1000)))

ax2.plot(global_deaths['d'], global_deaths['deahts_growth'])
ax2.set(ylabel='Daily deaths growth')
ax2.set_ylim([-.5, .5])
ax2.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
ax2.spines['top'].set_visible(False)
ax2.spines['bottom'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax2.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=True)
ax2.tick_params(axis='y', which='both', right=False, left=False, labelleft=True)
ax2.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))


plt.show()


country_deaths = deaths.groupby(['d', 'country'])[['deaths', 'daily_deaths']].sum().reset_index()
country_deaths['max_deaths'] = country_deaths['country'].map(max_deaths)
#country_deaths = country_deaths[country_deaths['max_deaths'] > 100]

for country in country_deaths['country'].unique():
    sub = country_deaths[country_deaths['country'] == country]
    sub['weekly_deaths'] = sub['daily_deaths'].rolling(7).sum()
    sub['weekly_deaths_growth'] = sub['weekly_deaths'].diff().fillna(sub['weekly_deaths'])
    sub['weekly_deaths_growth'] = sub['weekly_deaths_growth'] / \
        (sub['weekly_deaths'] - sub['weekly_deaths_growth'])
    sub = sub[sub['weekly_deaths'].cummax() > 30]
    sub['ord_d'] = sub.groupby('country').cumcount()
    plt.plot(sub['ord_d'], sub['weekly_deaths'])
    if sub['weekly_deaths'].max() > 1000 or country == 'Brazil' or sub['ord_d'].max() > 40:
        plt.text(sub['ord_d'].values[-1],
                 sub['weekly_deaths'].values[-1],
                 country)

# plt.yscale('log')
plt.title('Weekly deaths by country')
plt.show()

country = 'Brazil'
sub = country_deaths[country_deaths['country'] == country]
# sub.append({'d': '2020-05-06', 'deaths': 7921, 'daily_deaths': })
# sub.loc[sub.index[-1], 'deaths'] = 7921
# sub.loc[sub.index[-1], 'daily_deaths'] = 554
sub['weekly_deaths'] = sub['daily_deaths'].rolling(7).sum()
sub['weekly_deaths_growth'] = sub['weekly_deaths'].diff().fillna(sub['weekly_deaths'])
sub['weekly_deaths_growth'] = sub['weekly_deaths_growth'] / \
    (sub['weekly_deaths'] - sub['weekly_deaths_growth'])
sub = sub[sub['weekly_deaths'].cummax() > 30]
sub['ord_d'] = sub.groupby('country').cumcount()

fig, axs = plt.subplots(3)
# axs[0].fill(sub['d'], sub['deaths'])
axs[0].grid(axis='y')
axs[0].fill_between(sub['d'], np.repeat(0, len(sub['deaths'])), sub['deaths'])
axs[0].set(ylabel='Total de mortes')

axs[1].grid(axis='y')
axs[1].bar(sub['d'], sub['weekly_deaths'])
axs[1].set(ylabel='Mortes semanais\n(primeira derivada)')

axs[2].scatter(sub['d'], sub['weekly_deaths_growth'])
axs[2].axhline(y=0, color='r', alpha = .8)
axs[2].set(ylabel='Taxa crescimento das mortes semanais\n(segunda derivada)')
axs[2].set_yticklabels(['{:,.0%}'.format(x) for x in axs[2].get_yticks()])

for i in [0,1,2]:
    axs[i].grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
    axs[i].spines['top'].set_visible(False)
    axs[i].spines['bottom'].set_visible(False)
    axs[i].spines['right'].set_visible(False)
    axs[i].spines['left'].set_visible(False)
    axs[i].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=True)
    axs[i].tick_params(axis='y', which='both', right=False, left=False, labelleft=True)


plt.suptitle('Covid Brasil')
plt.show()
