# Arranque fluido del servidor de desarrollo Drive Tec.
# Uso:
#   powershell -File .\start.ps1                       # modo simulado (todo local)
#   .\start.ps1 -WhisperModel base                     # + transcripción Whisper local
#   .\start.ps1 -GoogleServerKey "AIza..."             # + traducción/geocodificación Google
#   .\start.ps1 -GoogleMapsKey "AIza..."               # + mapa Google (solo navegador)
param(
  [string]$WhisperModel = $env:WHISPER_MODEL,
  [string]$WhisperDevice = $env:WHISPER_DEVICE,
  [string]$WhisperCompute = $env:WHISPER_COMPUTE,
  [string]$GoogleServerKey = $env:GOOGLE_SERVER_KEY,
  [string]$GoogleMapsKey = $env:GOOGLE_MAPS_KEY
)
$Host.UI.RawUI.WindowTitle = 'Drive Tec · servidor de desarrollo'
Set-Location $PSScriptRoot
$env:DEBUG = '1'
$env:WHISPER_MODEL = $WhisperModel
$env:WHISPER_DEVICE = $WhisperDevice
$env:WHISPER_COMPUTE = $WhisperCompute
$env:GOOGLE_SERVER_KEY = $GoogleServerKey
$env:GOOGLE_MAPS_KEY = $GoogleMapsKey
if ($WhisperModel)   { Write-Host "Whisper: modelo '$WhisperModel'" }
if ($GoogleServerKey){ Write-Host 'Google: Geocoding + Routes + Cloud Translation activos' }
if ($GoogleMapsKey)  { Write-Host 'Google Maps JS activo' }
python manage.py migrate --no-input
python manage.py runserver 127.0.0.1:8000
