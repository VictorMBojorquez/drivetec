import json, math, hashlib, time, requests, os, tempfile
from collections import deque
from functools import wraps, lru_cache
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from .models import Unit, Report, AuditEvent

ROUTES='https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix'

# ---------------------------------------------------------------- integridad
def fnv(s):
    """FNV-1a 32 bits, idéntico al algoritmo del cliente; verifica el hash h del cliente."""
    a=0x811c9dc5
    for c in s.encode('utf-8'):
        a=((a^c)*0x01000193)&0xffffffff
    return f'{a:08x}'

def sha(prev,e):
    """SHA-256 del servidor sobre la cadena completa: hash previo + hash del cliente + campos del evento.
    Así la verificación cubre p y h (antes solo t/st/d, lo que dejaba p y h sin protección)."""
    return hashlib.sha256((prev+e['p']+e['h']+e['t']+e['st']+e['d']).encode()).hexdigest()

# ---------------------------------------------------------------- acceso
def api(f):
    @wraps(f)
    def w(request,*a,**k):
        if not request.user.is_authenticated: return JsonResponse({'error':'No autenticado'},status=401)
        return f(request,*a,**k)
    return w

def operador(u):
    """Staff (superusuario/admin) o miembro del grupo «Operador» (lo crea la migración 0002)."""
    return u.is_staff or u.groups.filter(name='Operador').exists()

def deco_op(f):
    @wraps(f)
    def w(request,*a,**k):
        if not operador(request.user):
            return JsonResponse({'error':'Se requiere el grupo «Operador» o personal'},status=403)
        return f(request,*a,**k)
    return w

# ---------------------------------------------------------------- límite de tasa (en memoria, por proceso de Gunicorn)
_BUCKETS={}
def ratelimit(limit,window):
    def d(f):
        @wraps(f)
        def w(request,*a,**k):
            key=(f.__name__,request.user.pk); now=time.monotonic()
            q=_BUCKETS.setdefault(key,deque())
            while q and now-q[0]>window: q.popleft()
            if len(q)>=limit: return JsonResponse({'error':'Demasiadas solicitudes; espera unos segundos'},status=429)
            q.append(now)
            return f(request,*a,**k)
        return w
    return d

def jbody(request):
    """Devuelve el cuerpo JSON como dict, o None si es inválido."""
    try:
        b=json.loads(request.body.decode('utf-8'))
        return b if isinstance(b,dict) else None
    except (ValueError,UnicodeDecodeError): return None

def bad(msg): return JsonResponse({'error':msg},status=400)

# ---------------------------------------------------------------- vistas
@login_required
@ensure_csrf_cookie
def index(request):
    p=Path(__file__).parent/'app'/'index.html'
    # en producción se cachea; en DEBUG se recarga para ver cambios al instante
    if settings.DEBUG: return HttpResponse(p.read_text(encoding='utf-8'))
    return HttpResponse(_index_cached())
@lru_cache(maxsize=1)
def _index_cached(): return (Path(__file__).parent/'app'/'index.html').read_text(encoding='utf-8')

@login_required
def config(request):
    return HttpResponse('window.DT='+json.dumps({'key':settings.GOOGLE_MAPS_KEY})+';',content_type='application/javascript')

@api
@ratelimit(120,60)
def state(request):
    if request.method=='PUT':
        if not operador(request.user): return JsonResponse({'error':'Se requiere el grupo «Operador» o personal'},status=403)
        b=jbody(request)
        if b is None: return bad('Cuerpo JSON inválido')
        reps=b.get('reports',[]); us=b.get('units',[]); lg=b.get('log',[])
        if not (isinstance(reps,list) and isinstance(us,list) and isinstance(lg,list)): return bad('Formato inválido')
        if len(reps)>2000 or len(us)>200 or len(lg)>10000: return bad('Demasiados datos')
        for r in reps:
            if not (isinstance(r,dict) and isinstance(r.get('folio'),str)): return bad('Reporte inválido')
        for u in us:
            if not (isinstance(u,dict) and isinstance(u.get('id'),str)): return bad('Unidad inválida')
        # cadena de auditoría del cliente: cada evento nuevo debe encadenar con el hash anterior
        # y h debe ser el FNV-1a correcto de p+t+st+d (probar eventos falsificados)
        have=AuditEvent.objects.count()
        prevh=AuditEvent.objects.order_by('-id').values_list('h',flat=True).first() or '0'
        new=lg[have:]
        for e in new:
            if not (isinstance(e,dict) and all(isinstance(e.get(k),str) for k in ('t','st','d','p','h'))):
                return bad('Evento de auditoría inválido')
            if e['p']!=prevh or e['h']!=fnv(e['p']+e['t']+e['st']+e['d']):
                return bad('Cadena de auditoría inválida')
            prevh=e['h']
        with transaction.atomic():
            for r in reps: Report.objects.update_or_create(folio=r['folio'],defaults={'data':r})
            for u in us: Unit.objects.filter(code=u['id']).update(busy=bool(u.get('busy')))
            sprev=AuditEvent.objects.order_by('-id').values_list('sha',flat=True).first() or '0'
            for e in new:
                s=sha(sprev,e); AuditEvent.objects.create(t=e['t'],st=e['st'],d=e['d'],p=e['p'],h=e['h'],sha=s); sprev=s
        return JsonResponse({'ok':True})
    if request.method!='GET': return JsonResponse({'error':'Método no permitido'},status=405)
    reps=[r.data for r in Report.objects.order_by('-folio')]
    nums=[]
    for r in reps:
        f=r.get('folio') if isinstance(r,dict) else None
        if isinstance(f,str):
            try: nums.append(int(f.split('-')[-1]))
            except ValueError: pass
    seq=max([2041]+nums)
    return JsonResponse({'units':[{'id':u.code,'t':u.kind,'lat':u.lat,'lng':u.lng,'busy':u.busy} for u in Unit.objects.order_by('code')],
        'reports':reps,'seq':seq,'log':[{'t':e.t,'st':e.st,'d':e.d,'p':e.p,'h':e.h} for e in AuditEvent.objects.order_by('id')]})

@api
def verify(request):
    """Verifica la doble cadena: encadenamiento de hashes del cliente (p→h) y SHA-256 del servidor."""
    pchain='0'; sprev='0'
    for i,e in enumerate(AuditEvent.objects.order_by('id'),1):
        d={'p':e.p,'h':e.h,'t':e.t,'st':e.st,'d':e.d}
        if e.p!=pchain or e.h!=fnv(e.p+e.t+e.st+e.d) or sha(sprev,d)!=e.sha:
            return JsonResponse({'ok':False,'bad':i})
        pchain=e.h; sprev=e.sha
    return JsonResponse({'ok':True,'count':AuditEvent.objects.count()})

@api
@deco_op
@ratelimit(20,60)   # geocodificación es una API de pago: límite estricto por usuario
@require_POST
def geocode(request):
    b=jbody(request)
    if b is None: return bad('Cuerpo JSON inválido')
    q=str(b.get('q','')).strip()[:300]
    if not q: return bad('Falta la dirección')
    k=settings.GOOGLE_SERVER_KEY
    if not k: return JsonResponse({'error':'Falta GOOGLE_SERVER_KEY en el servidor'},status=503)
    try: r=requests.get('https://maps.googleapis.com/maps/api/geocode/json',params={'address':q,'region':'mx','components':'country:MX','bounds':'32.40,-117.15|32.60,-116.60','key':k},timeout=6).json()
    except requests.RequestException: return JsonResponse({'error':'No se pudo contactar el servicio de geocodificación'},status=502)
    if r.get('status')!='OK': return JsonResponse({'error':'Sin resultados ('+r.get('status','?')+')'},status=404)
    x=r['results'][0]; l=x['geometry']['location']
    return JsonResponse({'lat':l['lat'],'lng':l['lng'],'formatted':x['formatted_address']})

# ---------------------------------------------------------------- transcripción en servidor (Whisper local)
_ASR={'m':None,'stat':'idle','err':''}   # 'idle': lista para cargar · 'ok' · 'fail'
MAX_AUDIO=25*1024*1024

def whisper_model():
    """Carga perezosa del modelo Whisper; None si no está configurado o falló. El modelo
    se descarga en el primer uso (~75 MB para 'base' en int8) y queda en caché."""
    if not settings.WHISPER_MODEL: return None
    if _ASR['m'] is not None: return _ASR['m'] if _ASR['stat']=='ok' else None
    try:
        from faster_whisper import WhisperModel
        _ASR['m']=WhisperModel(settings.WHISPER_MODEL,device=settings.WHISPER_DEVICE,compute_type=settings.WHISPER_COMPUTE)
        _ASR['stat']='ok'
    except Exception as e:
        _ASR['stat']='fail'; _ASR['err']=str(e); _ASR['m']=None
    return _ASR['m'] if _ASR['stat']=='ok' else None

@api
@deco_op
@ratelimit(10,60)   # la transcripción es pesada (CPU/GPU): límite estricto
@require_POST
def transcribe(request):
    f=request.FILES.get('audio')
    if f is None: return bad('Falta el archivo de audio')
    if f.size>MAX_AUDIO: return bad('Archivo demasiado grande (máx 25 MB)')
    m=whisper_model()
    if m is None:
        if not settings.WHISPER_MODEL:
            msg='Transcripción en servidor no disponible (define WHISPER_MODEL para habilitarla)'
        elif _ASR['stat']=='idle':
            msg='Descargando el modelo Whisper en el primer uso; reintenta en unos minutos'
        else:
            msg='Transcripción en servidor no disponible: '+_ASR['err']
        return JsonResponse({'error':msg},status=503)
    lang=(request.POST.get('lang') or '').strip()[:8]   # vacío = detectar idioma automáticamente
    suf='.'+(f.name.rsplit('.',1)[1] if '.' in f.name else 'webm')
    with tempfile.NamedTemporaryFile(suffix=suf,delete=False) as t:
        t.write(f.read()); path=t.name
    try:
        gen,info=m.transcribe(path,language=lang or None,vad_filter=True)
        text=' '.join(s.text.strip() for s in gen)
        return JsonResponse({'text':text[:6000],'lang':info.language,'dur':round(info.duration,1)})
    except Exception as e:
        return JsonResponse({'error':'No se pudo transcribir: '+str(e)},status=502)
    finally:
        try: os.unlink(path)
        except OSError: pass

# ---------------------------------------------------------------- traducción automática (Cloud Translation API)
_TFAIL={'until':0}   # recuerda fallos de Google 10 min para no martillar la API

@api
@deco_op
@ratelimit(30,60)
@require_POST
def translate(request):
    b=jbody(request)
    if b is None: return bad('Cuerpo JSON inválido')
    q=str(b.get('q','')).strip()[:5000]
    if not q: return bad('Falta el texto')
    k=settings.GOOGLE_SERVER_KEY
    if not k: return JsonResponse({'error':'Traducción automática no configurada (GOOGLE_SERVER_KEY con Cloud Translation API activada)'},status=503)
    if time.monotonic()<_TFAIL['until']:
        return JsonResponse({'error':'El servicio de traducción falló hace poco; reintenta en unos minutos'},status=503)
    src=str(b.get('src','') or '')[:8]; tgt=str(b.get('tgt','') or 'es')[:8] or 'es'
    data={'q':q,'target':tgt,'format':'text'}
    if src: data['source']=src
    try:
        r=requests.post('https://translation.googleapis.com/language/translate/v2',params={'key':k},data=data,timeout=8)
        r.raise_for_status()
        d=r.json()['data']['translations'][0]
        return JsonResponse({'es':d['translatedText'],'dst':d.get('detectedSourceLanguage') or src or '?','engine':'google'})
    except requests.RequestException as e:
        _TFAIL['until']=time.monotonic()+600
        return JsonResponse({'error':'No se pudo contactar Google Translate: '+str(e)},status=502)
    except (KeyError,ValueError):
        return JsonResponse({'error':'Respuesta inesperada de Google Translate'},status=502)

def hav(a,b,c,d):
    p=math.pi/180; h=math.sin((c-a)*p/2)**2+math.cos(a*p)*math.cos(c*p)*math.sin((d-b)*p/2)**2
    return 12742*math.asin(math.sqrt(h))

@api
@deco_op
@ratelimit(60,60)
@require_POST
def rank(request):
    b=jbody(request)
    if b is None: return bad('Cuerpo JSON inválido')
    try: lat,lng=float(b['lat']),float(b['lng'])
    except (KeyError,TypeError,ValueError): return bad('Coordenadas inválidas')
    t=b.get('tipo'); her=b.get('her')
    need={'choque':'Ambulancia' if her else 'Patrulla','incendio':'Bomberos','robo':'Patrulla','medico':'Ambulancia'}.get(t)
    us=list(Unit.objects.filter(busy=False)); out=[]; src='estimate'
    for u in us:
        km=hav(u.lat,u.lng,lat,lng)*1.3; out.append({'id':u.code,'t':u.kind,'km':round(km,1),'min':round(km/40*60,1)})
    k=settings.GOOGLE_SERVER_KEY
    if k and us:
        try:
            wp=lambda a,c:{'waypoint':{'location':{'latLng':{'latitude':a,'longitude':c}}}}
            r=requests.post(ROUTES,headers={'X-Goog-Api-Key':k,'X-Goog-FieldMask':'originIndex,duration,distanceMeters,condition'},timeout=8,
                json={'origins':[wp(u.lat,u.lng) for u in us],'destinations':[wp(lat,lng)],'travelMode':'DRIVE','routingPreference':'TRAFFIC_AWARE'})
            r.raise_for_status()
            for e in r.json():
                if e.get('condition')=='ROUTE_EXISTS':
                    o=out[e['originIndex']]; o['km']=round(e['distanceMeters']/1000,1); o['min']=round(int(e['duration'].rstrip('s'))/60,1)
            src='google'
        except Exception: pass
    for o in out: o['need']=o['t']==need
    out.sort(key=lambda o:(not o['need'],o['min']))
    return JsonResponse({'units':out,'source':src})
