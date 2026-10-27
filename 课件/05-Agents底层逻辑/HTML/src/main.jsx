import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import { PrimeReactProvider } from 'primereact/api'
import 'primereact/resources/themes/lara-dark-blue/theme.css'
import 'primeicons/primeicons.css'
import './styles/index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <PrimeReactProvider>
      <HashRouter>
        <App />
      </HashRouter>
    </PrimeReactProvider>
  </StrictMode>,
)
