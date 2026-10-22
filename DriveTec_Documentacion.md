# Drive Tec

**Traducción, transcripción y gestión inteligente de llamadas de emergencia**

Instituto Tecnológico de Tijuana · Ingeniería en Sistemas Computacionales · Lenguajes y Autómatas II
Profesor: Luis Alfonso Gaxiola Vega · Primera revisión: 28 de septiembre al 01 de octubre de 2026 · Tijuana, Baja California

**Integrantes**
- Ballesteros Cruz Aldo Juvetino
- Bojorquez Valdez Victor Manuel
- Grande Ortega Maximiliano Alberto

---

## Índice

1. [Resumen](#1-resumen)
2. [Introducción](#2-introducción)
3. [Objetivos](#3-objetivos)
4. [Ventajas y desventajas](#4-ventajas-y-desventajas)
5. [Características principales](#5-características-principales)
6. [Marco teórico](#6-marco-teórico)
7. [Diseño del sistema](#7-diseño-del-sistema)
8. [Funcionalidad implementada](#8-funcionalidad-implementada)
9. [Guía de uso](#9-guía-de-uso)
10. [Backend y API](#10-backend-y-api)
11. [Mapa: Google Maps y modo simulado](#11-mapa-google-maps-y-modo-simulado)
12. [Despliegue](#12-despliegue)
13. [Calidad: requisitos, pruebas y normas](#13-calidad-requisitos-pruebas-y-normas)
14. [Seguridad y privacidad](#14-seguridad-y-privacidad)
15. [Limitaciones conocidas](#15-limitaciones-conocidas)
16. [Conclusiones](#16-conclusiones)
17. [Recomendaciones y trabajo futuro](#17-recomendaciones-y-trabajo-futuro)
18. [Referencias](#18-referencias)
19. [Entregables y estructura de archivos](#19-entregables-y-estructura-de-archivos)

---

## 1. Resumen

Drive Tec convierte una llamada de emergencia en información accionable. Escucha el audio, lo transcribe y lo traduce en tiempo real, detecta los datos clave del incidente (tipo, ubicación, número de heridos y prioridad) y prepara un reporte para que el operador asigne ayuda con rapidez y precisión.

El proyecto se modela desde la teoría de compiladores: el sistema es un **traductor especializado** que analiza una señal de entrada no estructurada (voz), construye significado y genera una salida operativa verificable.

**Palabras clave:** traductor, compilador, llamadas de emergencia, transcripción, traducción multilingüe, análisis semántico, reporte automático.

## 2. Introducción

En una emergencia cada segundo cuenta. El operador debe escuchar, comprender, capturar datos, priorizar y movilizar recursos al mismo tiempo. Si quien llama habla otro idioma, la fricción aumenta cuando existe menor margen de error.

Drive Tec sigue una sola cadena de decisión: **escuchar, transcribir, traducir y asignar**. Su idea central es *entender primero para actuar antes*.

Lenguajes y Autómatas II aporta el enfoque teórico: un compilador recibe una entrada, la analiza por etapas (léxica, sintáctica y semántica) y produce una representación destino equivalente en significado. Drive Tec aplica esa lógica al habla humana.

## 3. Objetivos

### 3.1 Objetivo general

Desarrollar Drive Tec para escuchar, transcribir y traducir llamadas de emergencia en tiempo real, generando reportes y asignaciones de personal de forma automática.

### 3.2 Objetivos particulares

1. **Capturar audio con baja latencia**, junto con sus metadatos, sin retrasos que afecten la atención.
2. **Transcribir con precisión operativa**, aun con ruido o acentos.
3. **Traducir múltiples idiomas** al español conservando intención, ubicación, síntomas y nivel de riesgo.
4. **Extraer datos críticos automáticamente:** tipo de incidente, ubicación, número de heridos y prioridad.
5. **Generar reportes y sugerir unidades**, dejando la decisión final al operador.

## 4. Ventajas y desventajas

### 4.1 Ventajas

| Ventaja | Descripción |
|---|---|
| Comprensión multilingüe | El operador entiende la llamada en tiempo real sin intérprete externo. |
| Registro inmediato | Transcripción y datos se guardan durante la llamada, sin captura manual posterior. |
| Priorización consistente | Aplica los mismos criterios a cada llamada, lo que reduce la variabilidad por cansancio. |
| Menor carga operativa | Automatiza capturar, traducir y redactar el reporte. |
| Trazabilidad completa | Cada transformación deja evidencia auditable. |

> La tecnología no sustituye el criterio del operador: lo amplifica.

### 4.2 Desventajas

| Desventaja | Descripción |
|---|---|
| Precisión limitada | Ruido, acentos o mala señal degradan la transcripción y la traducción. |
| Privacidad | Se manejan datos y grabaciones sensibles que requieren protección estricta. |
| Dependencia tecnológica | Requiere conectividad e infraestructura estables. |
| Sesgos de los modelos | Cobertura desigual entre idiomas, regiones y acentos. |
| Adopción | Exige capacitación y confianza operativa del personal. |

## 5. Características principales

| Característica | Descripción |
|---|---|
| Multimodal | Integra audio, texto y metadatos en un flujo único. |
| Contextual | Identifica entidades, intención y prioridad clínico-operativa. |
| Tiempo real | Procesamiento incremental con baja latencia. |
| Trazable | Cada transformación deja evidencia auditable. |
| Robusto | Tolera ruido, pausas, acentos y código mixto (alternancia de idiomas). |
| Humano al centro | El sistema recomienda; el operador decide. |

**Arquitectura de cuatro módulos conectados:** (1) captura de audio, (2) transcripción y traducción, (3) reporte automático y (4) asignación de unidades. Una llamada entra una sola vez y la información fluye a todo el sistema.

## 6. Marco teórico

### 6.1 Compilador, intérprete y traductor

| Concepto | Definición |
|---|---|
| Compilador | Transforma un programa completo a una representación destino antes de ejecutarlo. |
| Intérprete | Analiza y ejecuta las instrucciones durante el recorrido, con retroalimentación inmediata. |
| Traductor | Convierte expresiones entre lenguajes preservando significado y propósito. |

Base conceptual: Aho, Lam, Sethi y Ullman (2008).

### 6.2 Fases de compilación y su equivalente en Drive Tec

| Fase de compilación | Equivalente en Drive Tec | Resultado |
|---|---|---|
| Análisis léxico | Voz convertida en unidades (tokens acústicos y palabras) | Transcripción |
| Análisis sintáctico | Estructura de la frase y detección de entidades | Frases y entidades reconocidas |
| Análisis semántico | Interpretación de intención, riesgo y prioridad; validación de datos | Estructura semántica |
| Generación de código destino | Traducción al español y reporte normalizado | Texto destino |
| Ejecución / acción | Guía al operador y asignación de unidades | Decisión |

Como un compilador maneja errores léxicos, sintácticos y semánticos, Drive Tec debe manejar entradas incompletas o ambiguas (datos faltantes, traducciones de baja confianza) y **señalarlas al operador en lugar de asumirlas**.

### 6.3 Caso de estudio: atención de emergencias multilingüe

El área de aplicación es un centro de atención de llamadas de emergencia. El idioma no debe convertirse en tiempo perdido. Se evalúa con tres criterios: **precisión**, **latencia** y **trazabilidad**.

Identificadores que el traductor reconoce y valida en cada reporte (tabla de símbolos): `tipo_vehiculo`, `accion_incidente`, `num_personas`, `condicion_victima`, `nivel_triage`, `ubicacion_escena`, además de `tipo_incidente`.

### 6.4 Aplicaciones en el mundo real

- **Centros 911:** recepción de llamadas con transcripción y traducción.
- **Despacho asistido:** sugerencia de la unidad más adecuada según tipo de incidente y distancia.
- **Telemedicina:** comprensión precisa de síntomas e idioma del paciente.
- **Subtitulado en vivo:** transcripción y traducción en tiempo real, útil para accesibilidad.

### 6.5 Ejemplos prácticos

**Ejemplo A: choque vehicular en inglés.** «I need an ambulance, there was a crash near the bridge…» → «Necesito una ambulancia; hubo un choque cerca del puente…». Datos detectados: incidente, choque vehicular; ubicación, Puente Central; heridos, 2 posibles; prioridad, alta.

| Campo del reporte | Valor |
|---|---|
| Folio | DT-2026-2041 |
| Fecha y hora | 23 sep 2026 · 14:32 |
| Idioma original | Inglés |
| Duración | 04:18 |
| Tipo de incidente | Choque vehicular |
| Resumen | Colisión de dos vehículos cerca del Puente Central; dos posibles heridos y bloqueo parcial de la vía. |
| Unidad asignada | Ambulancia A-12 (a 2.4 km; alternativas: patrulla P-07 a 3.1 km y bomberos B-03 a 5.8 km) |

**Ejemplo B: una llamada, cinco transformaciones.**

| Tiempo | Etapa | Resultado |
|---|---|---|
| 00:00 | Audio | Voz entrecortada con ruido vial |
| 00:04 | Transcripción | «Mi padre no puede respirar» |
| 00:07 | Contexto | Disnea · adulto · prioridad alta |
| 00:10 | Traducción | Mensaje normalizado al operador |
| 00:12 | Acción | Despacho médico y protocolo |

### 6.6 Pipeline y transformación de la información

Cinco etapas: (1) captura de audio y metadatos; (2) análisis, que convierte la voz en unidades; (3) contexto, que extrae intención y entidades; (4) traducción a la representación destino; (5) respuesta, que guía al operador.

`audio → tokens acústicos → estructura semántica → texto destino → decisión`

### 6.7 Riesgos y ética

| Riesgo | Control de diseño |
|---|---|
| Error de traducción | Validación humana y nivel de confianza |
| Sesgo lingüístico | Pruebas por acento, región y código mixto |
| Privacidad | Minimización de datos, cifrado y control de acceso |
| Automatización excesiva | Decisión final reservada al operador |

## 7. Diseño del sistema

### 7.1 Pipeline implementado

El analizador (función `analyze`) funciona como un compilador de tres fases más generación de destino:

1. **Léxico.** Normaliza el texto y lo divide en tokens (minúsculas, sin puntuación, apóstrofes unificados).
2. **Detección de idioma.** Cuenta palabras marcadoras de inglés, portugués, francés y español; elige el idioma con más coincidencias (español por defecto).
3. **Traducción (código destino).** Busca frases de hasta 5 palabras, de la más larga a la más corta, en el glosario del idioma detectado y, si no hay coincidencia, en los otros glosarios (esto permite código mixto). Los términos no reconocidos se conservan y reducen la **confianza** (`tokens reconocidos / tokens totales`).
4. **Sintáctico y semántico.** Extrae del texto en español:
   - **Tipo de incidente:** incendio, robo/agresión armada, choque vehicular o emergencia médica.
   - **Heridos / personas:** por número o palabra (un, dos, tres…), o 1 si se menciona a un familiar.
   - **Ubicación:** por gazetteer (puente, hospital, centro, aeropuerto, universidad, plaza).
   - **Condición de la víctima:** disnea, inconsciente o herido.
   - **Prioridad:** *alta* (dificultad respiratoria, inconsciencia, fuego, arma/disparos o heridos ≥ 1), *media* (choque o robo sin heridos), *baja* (otros).
5. **Errores semánticos señalados** (nunca asumidos): tipo sin clasificar, ubicación no identificada, número de heridos no indicado, traducción con confianza menor a 60 %.
6. **Sugerencia de unidad:** según el tipo (choque con heridos → ambulancia; choque sin heridos → patrulla; incendio → bomberos; robo → patrulla; médica → ambulancia) y la unidad libre más cercana. Se muestran alternativas de otros tipos.

### 7.2 Glosarios

Glosarios de emergencia de inglés, portugués y francés hacia español canónico (emergencias, lugares, síntomas, números, conectores). Son deterministas, auditables y fáciles de ampliar, pero no cubren lenguaje libre.

### 7.3 Interfaz

Diseño tipo **Argon** (panel de control): menú lateral con íconos, banda superior con degradado violeta-azul, tarjetas de indicadores superpuestas, mapa y gráfica en el centro de mando. Tipografía Open Sans, íconos SVG propios, gráfica con Chart.js 4.4.1. Es responsive, soporta modo oscuro e impresión a PDF del reporte.

## 8. Funcionalidad implementada

| Módulo | Qué hace |
|---|---|
| Centro de mando | Llamadas activas, reportes del día, unidades libres, tiempo de respuesta promedio, mapa operativo, gráfica por tipo de incidente y reportes recientes. |
| Llamada en vivo | Captura por micrófono (Web Speech API), grabación → Whisper en servidor, o texto; traducción con el glosario local o con Cloud Translation API si hay clave; tabla de símbolos, errores señalados y unidad sugerida en tiempo real. |
| Reporte | Folio `DT-2026-NNNN`, edición de campos, estados (borrador → aprobado → despachado → cerrado), asignación de unidad y exportación a PDF. |
| Unidades | Mapa, geocodificación de dirección, tiempos de llegada por unidad, asignación, liberación manual y animación de despacho. |
| Auditoría | Bitácora de eventos con hashes encadenados y verificación de integridad. |
| Calidad y normas | 10 pruebas automáticas, matriz de requisitos y matriz de alineación normativa. |

Los datos de demostración incluyen 6 unidades: ambulancias A-12 y A-07, patrullas P-07 y P-03, bomberos B-03 y B-01.

## 9. Guía de uso

### 9.1 Probar la página publicada

Abrir `https://claude.ai/artifact/98xXFQFXsiTpxgv276tR6a`. Los datos se guardan solo en el navegador.

1. **Llamada en vivo:** elegir un escenario de prueba, escribir texto o pulsar «🎙 Escuchar» (mejor en Chrome o Edge).
2. Revisar traducción, idioma, confianza, tabla de símbolos y alertas.
3. Pulsar **Generar reporte automático**.
4. En **Reporte:** corregir campos, **Aprobar**, **Despachar unidad** y **Cerrar y liberar unidad**. «Exportar a PDF» abre el diálogo de impresión.
5. En **Unidades:** escribir una dirección, pulsar «Ubicar y calcular ETA» y asignar la unidad deseada.
6. En **Auditoría:** «Verificar integridad».
7. En **Calidad y normas:** «Ejecutar pruebas».

### 9.2 Escenarios de prueba incluidos

| Escenario | Texto |
|---|---|
| Inglés · choque | I need an ambulance, there was a crash near the bridge and two people hurt |
| Español · disnea | Mi padre no puede respirar, estamos en el hospital |
| Portugués · acidente | Preciso de uma ambulância, houve um acidente perto da ponte |
| Francés · incendie | Il y a eu un incendie près du pont, au secours |
| Datos faltantes | help please |

### 9.3 Buenas prácticas

- Revisar siempre las alertas y la confianza antes de aprobar.
- Si la ubicación no se detectó, elegirla a mano en el reporte.
- El sistema solo sugiere; el operador confirma el despacho.

## 10. Backend y API

Proyecto Django 5 con PostgreSQL (SQLite en desarrollo), Gunicorn y WhiteNoise. El acceso requiere sesión (usuarios administrados en `/admin/`).

### 10.1 Modelos

| Modelo | Campos |
|---|---|
| `Unit` | `code`, `kind`, `lat`, `lng`, `busy` |
| `Report` | `folio`, `data` (JSON), `updated` |
| `AuditEvent` | `t`, `st`, `d`, `p`, `h`, `sha` (cadena SHA-256 del servidor) |

### 10.2 Endpoints

| Ruta | Método | Función |
|---|---|---|
| `/` | GET | Aplicación (requiere sesión) |
| `/config.js` | GET | Entrega la clave pública de Maps al cliente |
| `/api/state` | GET / PUT | Lee y guarda unidades, reportes y bitácora |
| `/api/geocode` | POST | Dirección → coordenadas (Google Geocoding) |
| `/api/rank` | POST | Tiempo y distancia por unidad (Google Routes, con respaldo estimado) |
| `/api/transcribe` | POST | Audio → texto con Whisper local (`faster-whisper`), se activa con `WHISPER_MODEL` |
| `/api/translate` | POST | Traducción a español (Cloud Translation API); sin clave usa el glosario del cliente |
| `/api/audit/verify` | GET | Verifica la cadena SHA-256 |
| `/healthz` | GET | Comprobación de salud |

Pruebas de backend en `core/tests.py` (16 casos con el cliente de pruebas de Django): acceso sin sesión devuelve 401; usuario sin grupo «Operador» no puede escribir; el estado se guarda y se lee; se crean 6 unidades iniciales; el orden por tiempo de llegada sugiere A-12 para un choque con heridos; JSON malformado devuelve 400; una cadena de auditoría alterada o con hash de cliente falso se rechaza; la verificación SHA-256 detecta una alteración. Ejecutar con `DEBUG=1 python manage.py test`.

## 11. Mapa: Google Maps y modo simulado

### 11.1 Google Maps (con claves)

Si `GOOGLE_MAPS_KEY` está definida, se carga Google Maps JavaScript en el dashboard y en Unidades, con marcadores de unidades e incidentes. La geocodificación y los tiempos de llegada con tráfico se calculan en el servidor con **Geocoding API** y **Routes API**.

Configuración en Google Cloud:

1. Crear el proyecto y activar facturación (las APIs se cobran por uso; hay capa gratuita mensual).
2. Activar Maps JavaScript API, Geocoding API y Routes API.
3. Crear dos claves:
   - `GOOGLE_MAPS_KEY` (navegador): restringir por *HTTP referrer* y solo a Maps JavaScript API.
   - `GOOGLE_SERVER_KEY` (servidor): restringir por IP y solo a Geocoding y Routes. Nunca llega al cliente.
4. Definir cuotas diarias máximas.

### 11.2 Mapa simulado (sin APIs)

Si `GOOGLE_MAPS_KEY` está vacía, se usa `simmap.js`, sin llamadas externas:

- Mapa dibujado en canvas con estilo Google (tierra, calles, río, parques, vía rápida), modo oscuro, arrastre y zoom.
- Geocodificación local: por nombre de lugar o, si no hay coincidencia, una intersección fija de la cuadrícula derivada del texto.
- Tiempo de llegada estimado: distancia × 1.3 a 40 km/h.
- Animación de la unidad al despachar, con el tiempo estimado acelerado 60 veces.

El mapa simulado es ilustrativo: calles y lugares no corresponden a Tijuana real.

## 12. Despliegue

### 12.1 Con Docker

```bash
cp .env.example .env        # editar valores
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

Poner un proxy HTTPS (Caddy o Nginx) hacia el puerto 8000 y dejar `HTTPS=1`.

### 12.2 Variables de entorno

| Variable | Uso |
|---|---|
| `SECRET_KEY` | Clave secreta de Django (cadena larga y aleatoria) |
| `DB_PASSWORD` | Contraseña de PostgreSQL |
| `DATABASE_URL` | Conexión a la base (la define `docker-compose.yml`) |
| `ALLOWED_HOSTS` | Dominios permitidos |
| `CSRF_TRUSTED_ORIGINS` | Orígenes HTTPS de confianza |
| `HTTPS` | `1` activa cookies seguras, redirección SSL y HSTS |
| `DEBUG` | `1` solo en desarrollo |
| `GOOGLE_MAPS_KEY` | Clave de navegador (vacía = mapa simulado) |
| `GOOGLE_SERVER_KEY` | Clave de servidor para Geocoding, Routes y (opcional) Cloud Translation |
| `WHISPER_MODEL` | Transcripción en servidor con `faster-whisper` (`tiny`, `base`, `small`…; vacío = solo navegador) |
| `WHISPER_DEVICE` | Dispositivo de Whisper: `cpu` (predeterminado) o `cuda` |
| `WHISPER_COMPUTE` | Precisión de Whisper: `int8` (predeterminado), `int8_float16`, `float16` |

### 12.3 Desarrollo local

```bash
pip install -r requirements.txt
DEBUG=1 python manage.py migrate
DEBUG=1 python manage.py createsuperuser
DEBUG=1 python manage.py runserver
```

Otras plataformas (Cloud Run, Render, Railway): usar el `Dockerfile` y las mismas variables, con `DATABASE_URL` hacia un PostgreSQL gestionado.

## 13. Calidad: requisitos, pruebas y normas

### 13.1 Requisitos verificables

| ID | Requisito | Módulo | Prueba |
|---|---|---|---|
| RF-01 | Capturar audio o texto con metadatos de hora e idioma | Llamada en vivo | PR-01 |
| RF-02 | Transcribir y mostrar en vivo (Web Speech API del navegador) | Llamada en vivo | Manual |
| RF-03 | Traducir EN/PT/FR a español, con código mixto, indicando confianza | Panel de traducción | PR-01, 03, 04, 08 |
| RF-04 | Extraer tipo, ubicación, heridos y prioridad | Tabla de símbolos | PR-01, 02 |
| RF-05 | Señalar datos faltantes sin asumirlos | Errores semánticos | PR-05 |
| RF-06 | Generar reporte editable, aprobable y exportable a PDF | Reporte | Manual |
| RF-07 | Sugerir unidad más cercana; decisión final del operador | Unidades | PR-06, 07 |
| RF-08 | Trazabilidad auditable de cada transformación | Auditoría | PR-09 |
| RNF-01 | Latencia de análisis menor a 50 ms | Panel de traducción | PR-10 |

### 13.2 Pruebas automáticas

| Caso | Verifica |
|---|---|
| PR-01 | Inglés: choque con 2 heridos, ubicación y prioridad alta |
| PR-02 | Español: disnea, prioridad alta, 1 persona |
| PR-03 | Portugués: acidente cerca del puente |
| PR-04 | Francés: incendio asignado a bomberos |
| PR-05 | Datos faltantes se señalan, no se asumen |
| PR-06 | Unidad más cercana: A-12 para el puente |
| PR-07 | Una unidad ocupada se excluye |
| PR-08 | Traducción de baja confianza se marca |
| PR-09 | La cadena de auditoría detecta alteraciones |
| PR-10 | Latencia de análisis menor a 50 ms |

Se ejecutan desde la pestaña **Calidad y normas** con «Ejecutar pruebas».

### 13.3 Alineación normativa

| Norma | Alcance | Cómo se atiende |
|---|---|---|
| ISO/IEC/IEEE 12207 | Ciclo de vida del software | Requisitos → diseño → construcción → verificación con evidencia trazable |
| ISO/IEC/IEEE 29148 (sucesor de IEEE 830) | Ingeniería de requisitos | Requisitos con ID, verificables y ligados a pruebas |
| IEEE 1016 | Descripción del diseño | Arquitectura de 4 módulos y pipeline de 5 etapas como compilador |
| ISO/IEC 25010 | Calidad del producto | Adecuación funcional, eficiencia, usabilidad, fiabilidad, seguridad y mantenibilidad |
| ISO/IEC 29119 · IEEE 829 | Pruebas de software | 10 casos automáticos con resultado aprobado/falló |
| ISO/IEC 27001 · 27701 | Seguridad y privacidad | Minimización de datos e integridad con hashes encadenados |
| ISO 22320 | Gestión de emergencias | Flujo de alerta, priorización y asignación con validación humana |
| IEEE 828 · CMMI CM | Gestión de configuración | Folios únicos e historial de cambios en la bitácora |
| CMMI RD / TS | Requisitos y solución técnica | Matriz de requisitos y diseño documentado |
| CMMI VER / VAL | Verificación y validación | Pruebas automáticas y validación por el operador |
| CMMI PPQA | Aseguramiento de calidad | Alertas de baja confianza y datos faltantes antes de aprobar |

> **Aclaración:** es una alineación de diseño y proceso con estas normas. No constituye una certificación ni una evaluación formal CMMI, que requieren un auditor externo.

## 14. Seguridad y privacidad

- Acceso con sesión y protección CSRF; API con respuesta 401 sin autenticación.
- Cookies seguras, redirección SSL y HSTS con `HTTPS=1`.
- La clave de servidor de Google no se envía al cliente; la de navegador se restringe por dominio.
- Bitácora con doble cadena de hashes: FNV en el cliente y SHA-256 en el servidor; ambas encadenadas (el SHA del servidor cubre también `p` y `h`) y verificables.
- Minimización de datos: la versión publicada guarda todo solo en el navegador.
- Roles base: las escrituras de la API exigen el grupo «Operador» o ser staff; límites de tasa por usuario en geocodificación y ETA para proteger la cuota de Google.
- **Pendiente para producción:** cifrado en reposo, roles granulares (supervisor), respaldos y política de retención de grabaciones.
- Aviso: con Google activo, las direcciones del incidente se envían a Geocoding para ubicarlas y el texto de la traducción a Cloud Translation. Con Whisper (`faster-whisper`), el audio se transcribe en tu servidor y no sale de él.

## 15. Limitaciones conocidas

- **Traducción:** por defecto usa glosarios deterministas que no cubren lenguaje libre; con `GOOGLE_SERVER_KEY` y la Translation API activada, la traducción automática se realiza en el backend (Cloud Translation) y el texto libre ya no depende del glosario. La transcripción por voz sigue dependiendo del navegador salvo que se habilite Whisper en el servidor (`WHISPER_MODEL`).
- **Transcripción:** depende del reconocimiento de voz del navegador (mejor en Chrome o Edge).
- **Ubicaciones y unidades:** coordenadas aproximadas y unidades simuladas, sin GPS en vivo.
- **Mapa simulado:** ilustrativo, sin calles reales ni tráfico.
- **Normas:** alineación, no certificación.
- **Pruebas:** el backend se probó con el cliente de Django; el mapa de Google y la interfaz no se verificaron en un navegador desde este entorno.
- **No incluye aún:** SRS completa y plan de pruebas formales, roles granulares (supervisor vs operador), cifrado en reposo ni pruebas de carga.

## 16. Conclusiones

1. **El modelo de traductor es válido.** Las fases de compilación (léxica, sintáctica, semántica y generación) tienen un equivalente directo en el procesamiento de una llamada.
2. **Los errores se señalan, no se asumen.** Como un compilador reporta errores, Drive Tec marca al operador los datos faltantes o las traducciones de baja confianza.
3. **El humano está al centro.** El sistema traduce, redacta el reporte y sugiere la unidad; la decisión final queda en el operador.
4. **El éxito es medible.** Precisión, latencia y trazabilidad permiten evaluar el sistema de forma objetiva y auditable.

Balance: 5 ventajas (multilingüe en tiempo real, registro inmediato, priorización consistente, menor carga, trazabilidad) frente a 5 limitaciones (ruido y acentos, privacidad, conectividad, sesgos, adopción). Estado: flujo central implementado, 4 módulos conectados, 5 etapas de pipeline y 4 riesgos con control de diseño.

> Escuchar mejor para responder más rápido.

## 17. Recomendaciones y trabajo futuro

| Área | Recomendación |
|---|---|
| Gramática | Formalizar la gramática de intenciones y entidades (incidente, ubicación, heridos, prioridad) con su tabla de símbolos y errores semánticos. |
| Pipeline | Integrar audio en vivo y medir latencia y exactitud en cada etapa, de la captura a la asignación. |
| Validación | Probar la traducción en escenarios multilingües con supervisión humana y con operadores. |
| Precisión | Entrenar y evaluar con audio de llamadas reales y ruido vial; incluir un glosario de términos de emergencia. |
| Sesgos | Probar por acento, región y código mixto; ampliar los idiomas por etapas. |
| Privacidad | Minimizar datos, cifrar grabaciones y registrar cada acceso. |
| Dependencia | Definir un modo de respaldo con captura manual ante fallas de conectividad. |
| Latencia | Procesar de forma incremental y fijar metas de tiempo por etapa. |
| Adopción | Capacitar con pilotos y mostrar el nivel de confianza en la interfaz. |

Ruta del prototipo a la operación: maqueta → prueba operativa → optimizaciones → mejoras. Siguiente hito: prototipo funcional con audio en vivo.

## 18. Referencias

- Aho, A. V., Lam, M. S., Sethi, R. y Ullman, J. D. (2008). *Compiladores: principios, técnicas y herramientas* (2.ª ed.). Pearson Educación.
- Equipo Drive Tec (2026). *Drive Tec: traducción, transcripción y gestión inteligente de llamadas de emergencia* [Presentación de avance, 21-25 de septiembre]. Instituto Tecnológico de Tijuana.
- Equipo Drive Tec (2026). *Marco teórico: Drive Tec* [Presentación]. Lenguajes y Autómatas II, Instituto Tecnológico de Tijuana.

*Nota:* una de las presentaciones cita la edición en inglés de Aho et al. (2007, Pearson Addison-Wesley). Conviene unificar la referencia en la entrega final.

## 19. Entregables y estructura de archivos

| Entregable | Descripción |
|---|---|
| Página publicada | Versión autónoma con mapa simulado, para demostración sin servidor. |
| `drivetec-django.zip` | Proyecto Django completo para despliegue propio. |
| `DriveTec_Documentacion.md` | Este documento. |

Estructura del proyecto Django:

```
dt/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── README.md
├── drivetec/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── core/
    ├── models.py            # Unit, Report, AuditEvent
    ├── admin.py             # Modelos en /admin/ (bitácora de solo lectura)
    ├── tests.py             # 16 pruebas de backend con el cliente de Django
    ├── views.py             # estado, geocodificación, ETA, verificación, límites de tasa
    ├── migrations/          # 0001 esquema · 0002 semilla, grupo Operador y recálculo de hashes
    ├── app/index.html       # frontend Argon + pipeline
    └── static/
        ├── maps.js          # integración Google Maps / mapa simulado
        └── simmap.js        # mapa simulado en canvas
```
