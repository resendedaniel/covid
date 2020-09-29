import transparencia
import oficial
import viz
import os


def create_dirs():
    for d in ['cache', '../html/data', 'img']:
        try:
            os.makedirs(d)
        except OSError as e:
            continue

create_dirs()

# of_data = oficial.process_data(oficial.get_data())

STATES = ['all', 'ac', 'al', 'am', 'ap', 'ba', 'ce', 'df', 'es', 'go', 'ma', 'mg', 'ms', 'mt', 'pa', 'pb', 'pe', 'pi', 'pr', 'rj', 'rn', 'ro', 'rr', 'rs', 'sc', 'se', 'sp', 'to']
for state in STATES:
    if transparencia.check_cache(state):
        data = transparencia.load_cache(state)
    else:
        data = transparencia.fetch_data(state)
        transparencia.save_cache(data, state)

    data = transparencia.process_data(data, state)
    data = transparencia.bind_excess(data)
    # data = transparencia.bind_oficial_data(data, of_data, state)
    print(data.tail())

    transparencia.save_processed(data, state)

    # viz.plot_deaths(data, state)
    # viz.plot_covid(data, state)
