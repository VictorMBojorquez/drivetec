# Drive Tec — Contexto exportado para Claude

> **Archivo exportable**: sube este documento a Claude (claude.ai → Proyecto → Conocimiento,
> o pégalo al inicio de un chat) y Claude quedará con el contexto completo del sistema:
> arquitectura, comandos, reglas y anatomía del código, sin necesidad de acceder al repositorio.
> Se genera a partir de `README.md` + `AGENTS.md` + código real, en un solo archivo autocontenido.
> Fecha de corte: octubre de 2026 · Estado: «Ran 23 tests — OK».

---

## 1 · Ficha del proyecto

**Drive Tec** es un sistema de gestión inteligente de llamadas de emergencia, proyecto escolar del
Instituto Tecnológico de Tijuana (Lenguajes y Autómatas II, 2026). Flujo:

```
🎤 Llamada (micrófono / Whisper / texto)
   → ⚙️ Pipeline de análisis: tokens → idioma → traducción → semántica
   → 📄 Reporte DT-2026-XXXX + 🚑 Sugerencia de unidad más cercana
   → 🔒 Auditoría verificable (doble cadena de hashes)
```

**Principio central**: «El sistema recomienda; el operador decide». Los datos faltantes se
**señalan** (lista `errs`) y nunca se asumen (prueba PR-05). Es su argumento de diseño.

| Aspecto | Valor |
|---|---|
| Stack | Django 5.2 · Python 3.12 · SQLite (dev) / PostgreSQL (prod) |
| Frontend | **Un solo archivo**: `core/app/index.html` (HTML+CSS+JS en línea) |
| IA/ASR | faster-whisper local (opcional, `WHISPER_MODEL`) |
| Traducción | Glosarios deterministas EN/PT/FR→ES (offline) o Cloud Translation API |
| Mapa | Canvas simulado offline (clase `SimMap`) o Google Maps (con clave) |
| Estado | Público: <https://github.com/VictorMBojorquez/drivetec> (MIT, branch `main`) |

## 2 · Estructura del código

```
dt/
├── drivetec/           # settings.py (fail-fast sin SECRET_KEY si DEBUG=0) · urls.py · wsgi.py
├── core/
│   ├── models.py       # Unit · Report · AuditEvent
│   ├── views.py        # API: state/geocode/rank/transcribe/translate/audit/config + health
│   ├── admin.py        # /admin/ (bitácora de solo lectura)
│   ├── tests.py        # 23 pruebas: auth, roles, validación, ranking, auditoría
│   ├── app/index.html  # FRONTEND ÚNICO (anatomía en §4)
│   ├── migrations/     # 0001 base · 0002_seed_and_rehash (SEED de unidades + grupo «Operador» + rehash)
│   └── static/         # maps.js (sincronización + Google/sim + chip usuario) · simmap.js (NO tocar)
├── start.bat · start.ps1 · crear-admin.bat
├── Dockerfile · docker-compose.yml · requirements.txt (incl. faster-whisper>=1.0,<2)
├── CLAUDE.md · AGENTS.md   # manuales para agentes que SÍ tienen el repo
└── DriveTec_Documentacion.md
```

## 3 · Modelos de datos (exacto a `core/models.py`)

```python
class Unit:      code=Char(10, pk); kind=Char(20); lat=Float; lng=Float; busy=Bool(False)
class Report:    folio=Char(20, pk); data=JSONField; updated=DateTimeField(auto_now=True)   # ← el estado completo del reporte vive en data (JSON)
class AuditEvent:  # cadena SHA-256 verificable en servidor
                 t=Char(40); st=Char(40); d=TextField; p=Char(64); h=Char(64); sha=Char(64)
```

**Estado en cliente** (localStorage `LS='drivetec_v1'` + sync con `/api/state`):
- Reporte: `{folio, dt, lang, dur, tipo, uk, ub, her, prio, orig, es, conf, cond, errs[], unit, status(borrador|aprobado|despachado|cerrado), t0, resp, day, res}`
- Unidad: `{id, t (tipo), x, y (canvas), lat, lng (real), busy}` — tipos: `Ambulancia|Patrulla|Bomberos`
- Evento auditoría cliente: `{t, st, d, p(hash previo), h(FNV-1a)}`
- Gazetteer `GZ`: puente, hospital, centro, aeropuerto, universidad, plaza

## 4 · Anatomía de `core/app/index.html` (por orden)

- **CSS** en 8 bloques: 1 tokens (claro/oscuro) · 2 base · 3 estructura (sidebar/header) ·
  4 motion (+`prefers-reduced-motion`) · 5 componentes · 6 confianza/toasts/stepper ·
  7 estados · 8 3D inmersivo (radar `div.sim::after` + tilt `[data-tilt]`).
- **JS**: helpers (`$`, `esc`, `csrf`, `toast`) · estado (`LS`, `U0()`) · auditoría cliente
  (`h()`=FNV-1a, `mk`, `log`, `chainOK`) · glosarios (`D`,`M`,`GZ`,`NUM`) · pipeline
  (`tok`→`detect`→`translate`→`rank`→`analyze`) · UI (`TABS`, escenarios `SC`) · voz
  (`startRec` Web Speech + anti-bucle `vRep<6`, `micS` MediaRecorder 250 ms → Whisper) ·
  análisis (`run`, `paint`, `srvTr`) · reportes (`#gen`, `rRep`, stepper `STEPS`) ·
  dashboard (`rDash`, `dmap` con pulso, `chart` canvas 2D sin CDN) · unidades (`rUni`) ·
  auditoría (`rAud`) · QA (10 casos `TS` PR-01…PR-10, matrices `RQ`/`NM`) · init `rQA();run();rDash();tab('dash')`.

## 5 · Endpoints reales (`drivetec/urls.py`)

| Ruta | Método | Rol mínimo | Límite |
|---|---|---|---|
| `/` · `/config.js` | GET | logueado | — |
| `/api/state` | GET/PUT | PUT: staff o grupo «Operador» (sino `403`) | 120/min |
| `/api/geocode` | POST | logueado | 20/min |
| `/api/rank` | POST | logueado | 60/min |
| `/api/transcribe` | POST | logueado | 10/min |
| `/api/translate` | POST | logueado | 30/min |
| `/api/audit/verify` | GET | logueado | — |
| `/healthz` · `/health` | GET | público | — |

Errores esperados: `401` sin sesión · `403` sin rol · `400` JSON inválido · `429` exceso.
**Nunca `500`**: toda entrada se valida en `views.py`.
`/config.js` sirve `window.DT={key,user}` (clave Maps de navegador + nombre de usuario).

## 6 · Comandos (Windows/PowerShell; Linux/macOS: `VAR=1 cmd`)

| Acción | Comando |
|---|---|
| Instalar | `python -m pip install -r requirements.txt` |
| Migrar | `$env:DEBUG='1'; python manage.py migrate` |
| Superusuario | `python manage.py createsuperuser` (o `.\crear-admin.bat`) |
| Servidor | `$env:DEBUG='1'; python manage.py runserver` (o `.\start.bat`) → http://127.0.0.1:8000/ |
| **Pruebas** | `$env:DEBUG='1'; python manage.py test` → «OK», 23 pruebas |
| Chequeo | `$env:DEBUG='1'; python manage.py check` |
| JS syntax | `node --check core/static/maps.js` + validar TODOS los `<script>` inline de index.html (hay más de uno: el anti-FOUC es el primero y no es el principal) |
| Con IA | `.\start.ps1 -WhisperModel base -GoogleServerKey "AIza…"` |
| Producción | `docker compose up -d --build` · HTTPS recomendado (`HTTPS=1`) |

## 7 · Reglas y convenciones (adherirse siempre)

1. **Todo en español** (código, comentarios, commits, UI).
2. Las **23 pruebas deben quedar en verde** tras cada cambio; verificar con `manage.py test`.
3. Frontend de un archivo, **estilo compacto deliberado** (constants minificadas, varias statements
   por línea, atributos con comillas simples, templates con backticks). No reformatear.
4. Voz del producto: español neutro mexicano; se señala con calma el dato faltante, sin asumirlo ni regañar.
5. Auditoría doble: cliente FNV-1a (`h()`), servidor SHA-256 (`AuditEvent.sha`), encadenadas
   por `p`+`t`+`st`+`d`. Cualquier cambio al formato rompe la verificación.
6. Sin CDN que el runtime exija: la gráfica es canvas 2D propio; paleta documentada (p. ej., incidente `#e11d48`, acento indigo `#4f46e5`/`#818cf8`).
7. Sin secretos en el repo; claves solo por variables de entorno.
8. `simmap.js` no se toca; `maps.js` sí es editable.
9. Anti-regresiones por grep: `alert(` = **0** en index.html (usar `toast`), paleta vieja (`#f5365c`,`#5e72e4`,`#2dce89`,`#1479f5`) = **0**.

## 8 · Pendientes conocidos (por si te lo piden)

- **CI**: `ci.yml` no está en el repo — el token `gh` no tiene scope `workflow`
  (`gh auth refresh -h github.com -s workflow` lo resuelve); respaldo congelado en `../ci.yml.backup`.
- **Capturas** en `docs/img/` para el README (no existentes todavía).
- Limitaciones válidas: sin GPS en vivo, roles granulares pendientes, cifrado en reposo pendiente.

## 9 · Glosario

| Término | Significado |
|---|---|
| `folio` | Identificador de reporte `DT-2026-NNNN` (secuencia `S.seq`) |
| `SEED` | Unidades de demostración fijadas en la migración `0002` |
| `chainOK` | Verificación de la cadena de hashes en cliente |
| `SimMap` | Componente de mapa canvas simulado (`core/static/simmap.js`) |
| `Operador` | Grupo de Django con permiso de escritura en la API |
| `toasts` | Notificaciones no bloqueantes (`#toasts`, `toast(msg, 'ok'\|'err')`) |
| PR-01…PR-10 | 10 pruebas automáticas en la pestaña «Calidad y normas» |

## 10 · Plantillas de petición (ejemplos que Claude entenderá con este contexto)

- «Agrega un escenario de prueba en portugués para incendio»: tocar `SC` + glosario `D.pt` si faltan contenidos.
- «Activa un toggle de tema claro/oscuro con localStorage»: extender tokens (ya existen `[data-theme=]`) + botón en header.
- «Explícame por qué la barra de confianza se puso roja»: `paint()` → `a.conf<.6` → gradient rosa/naranja.
- «Antes de publicar mi parche, dime qué pruebas correr»: §6 + reglas §7.
