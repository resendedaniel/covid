const xTickFormat = i => {
  const months = [
    'jan', 'fev', 'mar',
    'abr', 'mai', 'jun',
    'jul', 'ago', 'set',
    'out', 'nov', 'dez'
  ]

  const month = Math.floor((i+1) / 30)
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

window.addEventListener('load', function () {
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
            1-1,
            31-1,
            31+29-1,
            31+29+31-1,
            31+29+31+30-1,
            31+29+31+30+31-1,
            31+29+31+30+31+30-1,
            31+29+31+30+31+30+31-1,
            31+29+31+30+31+30+31+31-1,
            31+29+31+30+31+30+31+31+30-1,
            31+29+31+30+31+30+31+31+30+31-1,
            31+29+31+30+31+30+31+31+30+31+30-1,
          ], //[15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345],
        },
        // label: {
        //   text: 'Ano',
        //   position: 'outer-center',
        // },
      },
      y: {
        label: {
          text: 'Mortes por dia',
          position: 'outer-middle',
        }
      },
    },
    grid: {
      x: {
        show: false ,
        lines: [
          {value:0},
          //{value:31+29+31-1},
          {value:31+29+31+30+31+31-1},
          //{value:31+29+31+30+31+30+31+31+30-1},
          {value:31+29+31+30+31+30+31+31+30+31+30+31-1}
        ]
      },
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
        title: i => `Dia ${i+1}`,
        value: d => Math.round(d),
      },
    },
  })

  const selector = document.getElementById('state-selector')

  selector.addEventListener('change', async e => {
    const state = e.target.value;

    const data = await fetch(`/covid/html/data/transparencia_${state}.json`).then(r => r.json());
    const years = extract_years(data)
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
  })

  selector.dispatchEvent(new Event('change'));
});
