export function info(message, meta){
  try{ console.info(`[INFO] ${message}`, meta||{}) }catch(e){}
  // Optional: send to telemetry endpoint (uncomment to enable)
  // navigator.sendBeacon('/api/telemetry', JSON.stringify({level:'info', message, meta}))
}

export function error(message, err){
  try{ console.error(`[ERROR] ${message}`, err) }catch(e){}
  // Optional: send error details to server for centralized logging
  // fetch('/api/telemetry', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({level:'error', message, err: String(err)})})
}

export default { info, error }
