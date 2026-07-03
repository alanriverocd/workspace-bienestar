# Plataforma On-Premise de Control, Auditoría e Idempotencia Bancaria

Entrega mínima funcional que cumple los requisitos de la convocatoria.

Estructura principal:
- `backend/` - FastAPI app, modelos SQLAlchemy, endpoints y utilidades.
- `frontend/` - React + PrimeReact dashboard con búsqueda debounced y lista virtualizada.
- `docker-compose.yml` - Orquestación con redes separadas (frontend_net, backend_net).
- `scripts/` - `up.sh`, `clean.sh`, `test.sh`.
- `Jenkinsfile` - Pipeline declarativo para ejecución local.

Para iniciar localmente:

```bash
./scripts/up.sh
```

Servicios expuestos:
- Frontend: http://localhost:5173 (servicio `control_frontend`)
- Backend: http://localhost:8000 (servicio `control_backend`)

La base de datos corre en el servicio `control_db` y está aislada en la red `backend_net`.
