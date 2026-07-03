import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import 'primereact/resources/themes/saga-blue/theme.css'
import 'primereact/resources/primereact.min.css'
import 'primeicons/primeicons.css'
import './styles.css'

createRoot(document.getElementById('root')).render(<App />)
