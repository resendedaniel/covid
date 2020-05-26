const xTickFormat = i => {
  const months = [
    'jan', 'fev', 'mar',
    'abr', 'mai', 'jun',
    'jul', 'ago', 'set',
    'out', 'nov', 'dez'
  ]

  const month = Math.floor(i / 30)
  return months[month];
}

const extract = (year, data) => data.filter(d => d.year === year);
const extract_years = data => ({
  '2018': extract(2018, data),
  '2019': extract(2019, data),
  '2020': extract(2020, data),
});
const values = data => data.map(d => d.value);
const order = data => data.map(d => d.ord_d);

window.addEventListener('load', async function () {
  const data = await fetch('/data/transparencia_sp.json').then(r => r.json());

  const years = extract_years(data)

  const chart = c3.generate({
    bindto: '#chart',
    data: {
      xs: {
        '2018': '2018_order',
        '2019': '2019_order',
        '2020': '2020_order',
      },
      columns: [
        ['2018', ...values(years['2018'])],
        ['2018_order', ...order(years['2018'])],
        ['2019', ...values(years['2019'])],
        ['2019_order', ...order(years['2019'])],
        ['2020', ...values(years['2020'])],
        ['2020_order', ...order(years['2020'])],
      ],
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
          values: [15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345],
        },
        label: {
          text: 'Dia do ano',
          position: 'outer-center',
        },
      },
      y: {
        label: {
          text: 'Mortes por dia',
          position: 'outer-middle',
        },
      },
    },
    point: {
      show: false,
    },
    legend: {
      position: 'inset',
      inset: {
        anchor: 'top-right',
        step: 1,
      },
    },
    tooltip: {
      format: {
        title: i => `Dia ${i+1}`,
      },
    },
  });
});
