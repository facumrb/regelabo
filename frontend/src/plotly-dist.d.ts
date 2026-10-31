// react-plotly.js usa este build de Plotly: importarlo desde acá evita sumar otra copia al bundle
declare module 'plotly.js/dist/plotly' {
  import * as Plotly from 'plotly.js'
  export default Plotly
}
