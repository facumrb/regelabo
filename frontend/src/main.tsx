import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { SesionProvider } from './context/SesionContext'
import { SimulacionesEnCursoProvider } from './context/SimulacionesEnCurso'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <SesionProvider>
        <SimulacionesEnCursoProvider>
          <App />
        </SimulacionesEnCursoProvider>
      </SesionProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
