const xTickFormat = i => {
  const dt = luxon.DateTime.fromObject({ ordinal: i+1 }).setLocale('pt-br');
  return dt.toLocaleString({ month: 'short' }).replace('.', '');
}

const extract = (year, data) => data.filter(d => d.year === year);
const extract_years = data => ({
  '2018': extract(2018, data),
  '2019': extract(2019, data),
  '2020': extract(2020, data),
});
const values = data => data.map(d => d.value);
const order = data => data.map(d => d.ord_d);
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
      },
      colors: {
        '2018': '#A6CEE3',
        '2019': '#2377B4',
        '2020': '#F57E0D',
      },
    },
    axis: {
      x: {
        tick: {
          format: xTickFormat,
          values: [
            ordinal('2020-01-01') - 1,
            ordinal('2020-02-01') - 1,
            ordinal('2020-03-01') - 1,
            ordinal('2020-04-01') - 1,
            ordinal('2020-05-01') - 1,
            ordinal('2020-06-01') - 1,
            ordinal('2020-07-01') - 1,
            ordinal('2020-08-01') - 1,
            ordinal('2020-09-01') - 1,
            ordinal('2020-10-01') - 1,
            ordinal('2020-11-01') - 1,
            ordinal('2020-12-01') - 1,
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
        step: 1,
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
          const values = _data.filter(d => d.ord_d === i);
          const date = latest(values);
          return formatDate(date.d);
        },
        value: d => Math.round(d),
      },
    },
  })

  const selector = document.getElementById('state-selector')

  selector.addEventListener('change', async e => {
    const state = e.target.value;

    const response = await fetch(`/covid/html/data/transparencia_${state}.json`).then(r => r.json());
    _data = response.data;

    const latestDataPoint = latest(_data);
    const lastUpdatedField = document.getElementById('last-update');
    lastUpdatedField.textContent = formatDate(latestDataPoint.d);

    const years = extract_years(_data)
    chart.load({
      columns: [
        ['2018', ...values(years['2018'])],
        ['2018_order', ...order(years['2018'])],
        ['2019', ...values(years['2019'])],
        ['2019_order', ...order(years['2019'])],
        ['2020', ...values(years['2020'])],
        ['2020_order', ...order(years['2020'])],
      ],
    })

    chart.xgrids([{
      value: currentDayOfYear(),
      text: 'Hoje',
      class: 'c3-grid-highlight'
    }, {
      value: latestDataPoint.ord_d,
      text: 'Última atualização',
      class: 'c3-grid-highlight'
    }])
  })

  selector.dispatchEvent(new Event('change'));
});
