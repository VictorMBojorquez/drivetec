# Guía para agentes de IA — Drive Tec

> Contexto operativo para trabajar en este repositorio con IA (Claude Code, OpenCode, Codex,
> Cursor o cualquier agente). Los humanos: ver `README.md`. Última verificación: 23 pruebas OK.

## 0 · Reglas de oro (leer primero)

1. **Todo en español**: código, comentarios, commits, UI y mensajes de error incluidos.
2. **Numerales de calidad**: las 23 pruebas de backend (`DEBUG=1 python manage.py test`) deben
   terminar en `OK` después de cada cambio. Un cambio que rompe pruebas es un cambio incompleto.
3. **El frontend es UN archivo**: `core/app/index.html` (HTML + CSS + JS en línea). Estilo compacto
   deliberado: constantes minificadas, varias statements por línea, atributos HTML con comillas
   simples, templates JS con backticks. **No reformatear** al estilo "bonito".
4. **Cero dependencias externas de runtime**: la app funciona sin internet ni claves (modo
   simulado). La gráfica es canvas 2D nativo (sin Chart.js); la única petición externa opcional es
   Google Fonts con fallback `system-ui`.
5. **No modificar** `core/static/simmap.js` (mapa simulado estable). `maps.js` sí es editable.
6. **Ningún secreto en el repo**: claves solo por variables de entorno
   (`GOOGLE_MAPS_KEY`, `GOOGLE_SERVER_KEY`, `WHISPER_MODEL`, …).
7. **Retrocompatibilidad**: la migración `0002` recalcula hashes de auditoría existentes; el
   cliente versiona su estado con `LS='drivetec_v1'` (subir la versión invalida el localStorage).
8. Repo en **Windows/PowerShell**, saltos CRLF (los warnings LF→CRLF de git son inofensivos).
   Branch `main`; commits y push en español.

## 1 · Comandos (Windows/PowerShell; en Linux/macOS usar `VAR=1 cmd`)

| Acción | Comando |
|---|---|
| Instalar dependencias | `python -m pip install -r requirements.txt` |
| Migraciones | `$env:DEBUG='1'; python manage.py migrate` |
| Crear superusuario | `python manage.py createsuperuser` (o `.\crear-admin.bat`) |
| Servidor de desarrollo | `$env:DEBUG='1'; python manage.py runserver` (o `.\start.bat`) |
| **Pruebas (23)** | `$env:DEBUG='1'; python manage.py test` |
| Chequeo de sistema | `$env:DEBUG='1'; python manage.py check` |
| Sintaxis JS | `node --check core/static/maps.js` + extraer el `<script>` de `index.html` |
| Con Whisper + Google | `.\start.ps1 -WhisperModel base -GoogleServerKey "AIza…"` |
| Producción (VPS) | `docker compose up -d --build` |

## 2 · Mapa del código

```
dt/
├── drivetec/           # settings.py (fail-fast sin SECRET_KEY si DEBUG=0), urls, wsgi
├── core/
│   ├── models.py       # Unit · Report · AuditEvent
│   ├── views.py        # API: state/geocode/rank/transcribe/translate/audit/config + health
│   ├── admin.py        # /admin/ (bitácora de solo lectura)
│   ├── tests.py        # 23 pruebas: auth, roles, validación, ranking, auditoría
│   ├── app/index.html  # FRONTEND ÚNICO (ver desglose abajo)
│   ├── migrations/     # 0001 base · 0002_seed_and_rehash (SEED + grupo «Operador» + rehash)
│   └── static/         # maps.js (sincronización + Google/sim) · simmap.js (NO tocar)
├── start.bat · start.ps1 · crear-admin.bat · Dockerfile · docker-compose.yml
├── CLAUDE.md           # importa AGENTS.md para Claude Code
└── README.md
```

### Desglose de `core/app/index.html` (por orden de aparición)

- **CSS**: tokens (bloque 1), base (2), estructura sidebar/header (3), motion (4), componentes
  (5), confianza/toasts/stepper (6), estados (7), 3D inmersivo radar+tilt (8).
- **JS**: helpers (`$`, `esc`, `csrf`, `toast`), estado local (`LS`), auditoría cliente
  (`h()` FNV-1a, `mk`, `log`, `chainOK`), glosarios (`D`/`M`/`GZ`/`NUM`), pipeline
  (`tok`→`detect`→`translate`→`rank`→`analyze`), UI (`TABS`, escenarios `SC`), voz
  (`startRec` Web Speech con anti-bucle, `micS` MediaRecorder→`/api/transcribe`),
  análisis/traducción (`run`, `paint`, `srvTr`), reportes (`#gen`, `rRep`, stepper),
  dashboard (`rDash`, `dmap`, `chart` canvas 2D), unidades (`rUni`), auditoría (`rAud`),
  QA en-app (`TS` PR-01…PR-10, matriz `RQ`/`NM`).

### Endpoints (`core/urls.py` → `views.py`)

| Ruta | Método | Rol mínimo | Límite de tasa |
|---|---|---|---|
| `/` y `/config.js` | GET | logueado | — |
| `/api/state` | GET / PUT | GET logueado · PUT staff o grupo «Operador» | 120/min |
| `/api/geocode` | POST | logueado | 20/min |
| `/api/rank` | POST | logueado | 60/min |
| `/api/transcribe` | POST | logueado | 10/min |
| `/api/translate` | POST | logueado | 30/min |
| `/api/audit/verify` | GET | logueado | — |
| `/healthz` · `/health` | GET | público | — |

Errores esperados: `401` sin sesión, `403` sin rol, `400` cuerpo inválido, `429` exceso.
**Nunca `500`**: validar toda entrada en `views.py`.

## 3 · Arquitectura conceptual (útil para responder correctamente)

- **Pipeline tipo compilador** (Aho/Lam/Sethi/Ullman): audio → tokens acústicos → detección de
  idioma → traducción → estructura semántica → decisión de recursos.
- **«El sistema recomienda; el operador decide»**: los datos faltantes se **señalan** en
  `errs`, jamás se asumen (prueba PR-05). Es el argumento central del proyecto.
- **Doble cadena de auditoría**: cliente FNV-1a (`h()` + `chainOK` en el HTML) y servidor
  SHA-256 (models/views). No romper el encadenado (`p` + `t` + `st` + `d`).
- **Modos operativos**: sin claves = glosarios deterministas + mapa canvas simulado
  (`simmap.js`, clase `SimMap`); con `GOOGLE_SERVER_KEY` = Geocoding/Routes/Translation reales;
  con `WHISPER_MODEL` = faster-whisper local en `views.py`.
- **`window.DT`** (desde `/config.js`, cargado tras el script inline): `{key, user}`; el chip
  `#who` del header lo consume en `maps.js`.

## 4 · Pendientes y ganchos conocidos

- **CI**: `ci.yml` NO está en el repo — el token `gh` no tiene scope `workflow`
  (`gh auth refresh -h github.com -s workflow` para resolverlo). Respaldo congelado en
  `..\ci.yml.backup` (fuera del repo).
- **Capturas de pantalla**: carpeta `docs/img/` pendiente para el README.
- **Limitaciones declaradas** en el README (sección «Limitaciones y siguientes pasos»): sin GPS
  en vivo, roles granulares pendientes, sin cifrado en reposo.

## 5 · Flujo de verificación tras cada cambio

```powershell
$env:DEBUG='1'; python manage.py test      # → "OK" (23 pruebas)
python manage.py check                     # → sin problemas
node --check core/static/maps.js           # → silencio = válido
# Extraer y revisar el <script> inline de index.html si se tocó el frontend:
node -e "const fs=require('fs');const m=fs.readFileSync('core/app/index.html','utf8').match(/<script>([\s\S]*?)<\/script>/);fs.writeFileSync(process.env.TEMP+'/inline.js',m[1]);" ; node --check "$env:TEMP/inline.js"
```

Anti-regresiones por grep: `alert(` debe dar **0** en `index.html` (usar `toast`);
colores de paleta antiguos (`#f5365c`, `#5e72e4`, `#2dce89`, `#1479f5`) deben dar **0**.

## 6 · Estilo de commits

Mensaje en español, en una línea, describiendo el cambio con sustantivo concreto:

```
front: gráfica nativa canvas sin CDN
api: límite de tasa para /api/translate
docs: guion de demostración en README
```
