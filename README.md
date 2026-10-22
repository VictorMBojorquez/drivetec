# Drive Tec · Django + Google Maps

Backend Django (PostgreSQL, Gunicorn, WhiteNoise) con el frontend Argon de Drive Tec y mapa de Google.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green)](https://www.djangoproject.com/)

## 1. Google Cloud
1. Crea un proyecto y activa facturación (hay capa gratuita mensual, pero **las APIs se cobran por uso**).
2. Activa: **Maps JavaScript API**, **Geocoding API** y **Routes API**.
3. Crea **dos** claves:
   - `GOOGLE_MAPS_KEY` (navegador): restringe por *HTTP referrer* a tu dominio y solo a Maps JavaScript API.
   - `GOOGLE_SERVER_KEY` (servidor): restringe por IP del servidor y solo a Geocoding + Routes. Nunca llega al cliente.
4. Define cuotas diarias máximas para evitar cargos inesperados.

## 2. Despliegue (VPS con Docker)
```
cp .env.example .env      # edita los valores
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```
Pon un proxy HTTPS delante (Caddy o Nginx) hacia el puerto 8000 y deja `HTTPS=1`.
Entra en `https://tu-dominio/` (inicia sesión con el usuario creado; los operadores se administran en `/admin/`).
Verificación: `GET /healthz`. Otras plataformas (Cloud Run, Render, Railway): usa el Dockerfile y define las mismas variables de entorno, con `DATABASE_URL` hacia su PostgreSQL gestionado.

## 3. Desarrollo local
```
pip install -r requirements.txt
DEBUG=1 python manage.py migrate && DEBUG=1 python manage.py createsuperuser
DEBUG=1 python manage.py runserver
```
En Windows: doble clic en `start.bat` (aplica migraciones, abre el navegador y arranca en modo simulado) o `powershell -File .\start.ps1 -WhisperModel base` para habilitar Whisper/Google; `crear-admin.bat` crea el superusuario. Detener con Ctrl+C en esa ventana.
**Modo simulado (sin APIs):** si `GOOGLE_MAPS_KEY` está vacía, la app usa automáticamente `core/static/simmap.js`: mapa con estilo Google dibujado en canvas (arrastrar, zoom, calles, río, parques), geocodificación local por gazetteer, ETA estimado y animación de la unidad al despachar. No hace ninguna llamada externa. Al definir la clave, cambia solo a Google Maps.

## API (requiere sesión)
| Ruta | Función |
|---|---|
| `GET/PUT /api/state` | Unidades, reportes y bitácora (persistencia en BD) |
| `POST /api/geocode` | Dirección → coordenadas (Google Geocoding) |
| `POST /api/rank` | ETA por unidad con tráfico (Google Routes); estimación si falla |
| `GET /api/audit/verify` | Verifica la cadena SHA-256 de auditoría |
| `POST /api/transcribe` | Audio grabado en el navegador → texto con Whisper local (`faster-whisper`) |
| `POST /api/translate` | Traducción a español con Cloud Translation API; sin clave usa el glosario del cliente |

Notas de la API:
- Solo lectura requiere sesión. Las escrituras (`PUT /api/state`, `/api/geocode`, `/api/rank`, `/api/transcribe`, `/api/translate`) exigen el grupo **Operador** o ser staff (el grupo lo crea la migración; asígñalo a usuarios en `/admin/`).
- Entradas validadas: JSON malformado o con tipos inesperados devuelve `400`; un evento de auditoría que no encadene o con hash de cliente falso se rechaza tras una verificación doble (encadenamiento client-side FNV-1a + SHA-256 server-side, que ahora cubre también `p` y `h`).
- Límites de tasa por usuario: geocodificación 20/min, ETA 60/min, estado 120/min, traducción 30/min, transcripción 10/min (el excedente devuelve `429`). Protegen la cuota de las APIs de pago de Google y la CPU del servidor.

## Transcripción y traducción en servidor (opcional)

El reconocimiento por micrófono del navegador (Web Speech API) y el glosario determinista siguen siendo el modo por defecto. Ahora hay dos capacidades adicionales en el backend:

- **Transcripción con Whisper (`faster-whisper`, local y offline):** define `WHISPER_MODEL=base` (o `small`; `tiny` para pruebas). El modelo se descarga automáticamente en el primer uso (~40–150 MB según tamaño) y queda en caché. La pestaña «Llamada en vivo» graba con MediaRecorder y sube el audio a `POST /api/transcribe`. Variables: `WHISPER_DEVICE` (`cpu` por defecto, `cuda` si hay GPU) y `WHISPER_COMPUTE` (`int8` por defecto). En VPS con 2 vCPU usa `base`; `small` es más preciso pero más lento.
- **Traducción automática (Cloud Translation API):** si la clave `GOOGLE_SERVER_KEY` tiene la **Translation API** activada (además de Geocoding y Routes), el botón «🌐 Servidor (Google)» y la casilla «Traducir automáticamente» envían el texto a `POST /api/translate` y la traducción entra al mismo pipeline de extracción/sugerencia. La extracción y la tabla de símbolos se siguen calculando en el cliente sobre el texto traducido, y el operador ve el motor usado. Sin clave, todo se queda local y nada se envía a terceros.

Ambas funciones requieren el grupo Operador y están limitadas por tasa. Si Google falla, la vista recuerda el fallo 10 minutos y el cliente vuelve al glosario local sin perder capacidad.

## Pendientes antes de producción real
Coordenadas de unidades y lugares son aproximadas (edita `SEED` en `core/migrations/0002_seed_and_rehash.py`); GPS en vivo de unidades; roles granulares (supervisor vs operador); cifrado de datos en reposo y respaldos; pruebas de carga.
