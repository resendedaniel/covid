const xTickFormat = i => {
  const dt = luxon.DateTime.fromObject({ ordinal: i }).setLocale('pt-br');
  return dt.toLocaleString({ month: 'short' }).replace('.', '');
}

const extract = (year, data) => data.filter(d => {
  const dt = luxon.DateTime.fromISO(d.d).setLocale('pt-br');
  return dt.year === year
});

const extract_years = data => ({
  '2018': extract(2018, data),
  '2019': extract(2019, data),
  '2020': extract(2020, data),
  '2021': extract(2021, data),
  '2022': extract(2022, data),
  '2023': extract(2023, data),
});
const values = data => data.filter((d) => d.deaths_daily_mean).map(d => d.deaths_daily_mean);
const order = data => data.filter((d) => d.deaths_daily_mean).map(d => d.d).map(ordinal);
const latest = data =>
  data.reduce((agg, dataPoint) => {
    const a = new Date(agg)
    const b = new Date(dataPoint.d)

    if( a > b) {
      return agg
    }

    return dataPoint
  }, '1900-01-01')

const formatDate = dateStr => {
  const dt = luxon.DateTime.fromISO(dateStr).setLocale('pt-br');
  return dt.toLocaleString();
}

const currentDayOfYear = () => luxon.DateTime.local().ordinal;

const ordinal = dateStr => {
  const dt = luxon.DateTime.fromISO(dateStr).setLocale('pt-br');
  return dt.ordinal
}

window.addEventListener('load', function () {
  /* Global required for the chart's tooltip.format.title attribute */
  let _data = null;

  const chart = c3.generate({
    bindto: '#chart',
    data: {
      columns: [],
      xs: {
        '2018': '2018_order',
        '2019': '2019_order',
        '2020': '2020_order',
        '2021': '2021_order',
        '2022': '2022_order',
        '2023': '2023_order',
      },
      colors: {
        '2018': '#A6CEE3',
        '2019': '#2377B4',
        '2020': '#F57E0D',
        '2021': '#E3221C',
        '2022': '#E3A71C',
        '2023': '#CEE21B',
      },
    },
    axis: {
      x: {
        tick: {
          format: xTickFormat,
          values: [
            ordinal('2023-01-01'),
            ordinal('2023-02-01'),
            ordinal('2023-03-01'),
            ordinal('2023-04-01'),
            ordinal('2023-05-01'),
            ordinal('2023-06-01'),
            ordinal('2023-07-01'),
            ordinal('2023-08-01'),
            ordinal('2023-09-01'),
            ordinal('2023-10-01'),
            ordinal('2023-11-01'),
            ordinal('2023-12-01'),
          ],
        },
      },
      y: {
        label: {
          text: 'Mortes por dia',
          position: 'outer-middle',
        }
      },
    },
    grid: {
      y: {
        show: true,
      }
    },
    point: {
      show: true,
      r: 0,
      focus : { expand: { r:4}}
    },
    legend: {
      position: 'inset',
      inset: {
        anchor: 'top-right',
        step: 6,
        x: 20,
      },
    },
    tooltip: {
      format: {
        title: i => {
          /*
           * C3 does not provide a way to access attributes of a data point and
           * neither a way to update the tooltip title format function.
           *
           * The quick solution was to put the data in a global variable so it
           * can be updated when the state selctor changes and accessed here.
           *
           * This is the last sign I needed to change the visualization library.
           */
          const values = _data.filter(d => ordinal(d.d) === i);
          const date = latest(values);
          return formatDate(date.d);
        },
        value: d => Math.round(d),
      },
    },
  })

  const show = async state => {
    const response = await fetch(`/html/data/transparencia_${state}.json`).then(r => r.json());
    _data = response.data;

    const lastUpdatedField = document.getElementById('last-update');
    lastUpdatedField.textContent = formatDate(response.updated_date);

    const years = extract_years(_data)
    chart.load({
      columns: [
        ['2018', ...values(years['2018'])],
        ['2018_order', ...order(years['2018'])],
        ['2019', ...values(years['2019'])],
        ['2019_order', ...order(years['2019'])],
        ['2020', ...values(years['2020'])],
        ['2020_order', ...order(years['2020'])],
        ['2021', ...values(years['2021'])],
        ['2021_order', ...order(years['2021'])],
        ['2022', ...values(years['2022'])],
        ['2022_order', ...order(years['2022'])],
        ['2023', ...values(years['2023'])],
        ['2023_order', ...order(years['2023'])],
      ],
    })

    chart.xgrids([{
      value: currentDayOfYear(),
      text: 'Hoje',
      class: 'c3-grid-highlight'
    }, {
      value: ordinal(latest(_data).d),
      text: 'Corte de 14 dias',
      class: 'c3-grid-highlight'
    }])
  }

  const router = new Navigo(window.location.protocol + '//' + window.location.host);
  const selector = document.getElementById('state-selector')

  const navigate = path => {
    gtag('config', GA_MEASUREMENT_ID, { 'page_path': path });
    router.navigate(path);
  }

  selector.addEventListener('change', e => {
    const state = e.target.value;
    const path = state === 'all' ? '/' : `/${state}`;
    navigate(path)
  })

  router.on('/', () => {
    selector.value = 'all';
    show('all');
  });

  router.on('/:state', params => {
    selector.value = params.state;
    show(params.state).catch(() => navigate('/'));
  })

  router.resolve();

  const closeAlert = document.getElementById('close');
  closeAlert.addEventListener('click', e => {
    e.preventDefault();
    document.getElementById("alert").style.display = 'none'
  });
});
