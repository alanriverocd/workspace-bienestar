import React, { useEffect, useState, useRef } from 'react'
import axios from 'axios'
import { VirtualScroller } from 'primereact/virtualscroller'
import { info, error as logError } from '../utils/logger'

function useDebouncedValue(value, delay = 300){
  const [v, setV] = useState(value)
  useEffect(()=>{
    const t = setTimeout(()=> setV(value), delay)
    return ()=> clearTimeout(t)
  },[value, delay])
  return v
}

// Using PrimeReact VirtualScroller for efficient virtualization
function VirtualList({items, rowHeight=60, height=400, renderItem}){
  const itemTemplate = (item) => renderItem(item)
  return (
    <div style={{height}}>
      <VirtualScroller items={items} itemSize={rowHeight} style={{height: '100%'}} itemTemplate={itemTemplate} />
    </div>
  )
}

export default function Dashboard(){
  const [dashboard, setDashboard] = useState({sincronizaciones:[]})
  const [query, setQuery] = useState('')
  const debounced = useDebouncedValue(query, 300)
  const [logs, setLogs] = useState([])
  const [modal, setModal] = useState(null)

  useEffect(()=>{
    axios.get('http://localhost:8000/dashboard')
      .then(r=> { setDashboard(r.data); info('Loaded dashboard', {count: r.data.sincronizaciones?.length}) })
      .catch(e=> { logError('Failed loading dashboard', e) })
  },[])

  useEffect(()=>{
    axios.get('http://localhost:8000/logs', {params: {q: debounced}})
      .then(r=> setLogs(r.data.logs))
      .catch(e=> { logError('Failed loading logs', e) })
  },[debounced])

  return (
    <div>
      <section className="card">
        <h2>Sincronizaciones</h2>
        <div className="sync-grid">
          {(dashboard.sincronizaciones || []).map((s,i)=> (
            <div key={i} className="sync-item">
              <div className="sync-title">{s.nombre || `Sync ${i+1}`}</div>
              <div className="sync-meta">{s.estado || '—'}</div>
            </div>
          ))}
          {(!dashboard.sincronizaciones || dashboard.sincronizaciones.length === 0) && <div className="muted">No hay sincronizaciones registradas</div>}
        </div>
      </section>

      <section className="card">
        <h2>Logs</h2>
        <div className="toolbar">
          <input aria-label="buscar-logs" className="search" placeholder="Buscar logs" value={query} onChange={e=> setQuery(e.target.value)} />
        </div>
        <VirtualList items={logs} renderItem={(l)=> (
          <div key={l.id} className="log-row">
            <div className="log-code">{l.codigo}</div>
            <div className="log-message">{l.mensaje}</div>
            <div className="log-actions"><button onClick={()=> setModal(l)} className="btn-sm">Detalle</button></div>
          </div>
        )} />
      </section>

      {modal && (
        <Modal onClose={()=> setModal(null)}>
          <h3>Log {modal.id}</h3>
          <pre>{modal.mensaje}</pre>
        </Modal>
      )}
    </div>
  )
}

function Modal({children, onClose}){
  const ref = useRef(null)
  const lastFocused = useRef(null)
  useEffect(()=>{
    lastFocused.current = document.activeElement
    const el = ref.current
    const getFocusable = () => el ? el.querySelectorAll('button, [href], input, textarea, select, [tabindex]:not([tabindex="-1"])') : []
    const focusable = getFocusable()
    const first = focusable[0]
    const last = focusable[focusable.length-1]
    const handler = (e)=>{
      if(e.key === 'Escape') return onClose()
      if(e.key === 'Tab'){
        // If no focusable elements, trap on modal container
        if(focusable.length === 0){ e.preventDefault(); return }
        if(e.shiftKey){ if(document.activeElement === first){ e.preventDefault(); last && last.focus() } }
        else { if(document.activeElement === last){ e.preventDefault(); first && first.focus() } }
      }
    }
    document.addEventListener('keydown', handler)
    // set initial focus
    if (first) {
      first.focus()
    } else if (el) {
      el.focus()
    }
    return ()=>{
      document.removeEventListener('keydown', handler)
      // restore focus
      try{ lastFocused.current && lastFocused.current.focus() }catch(e){}
    }
  },[onClose])

  return (
    <div className="overlay" role="presentation" onClick={(e)=>{ if(e.target === e.currentTarget) onClose() }}>
      <div className="modal" ref={ref} role="dialog" aria-modal="true">
        {children}
        <div style={{textAlign:'right'}}>
          <button onClick={onClose}>Cerrar</button>
        </div>
      </div>
    </div>
  )
}
