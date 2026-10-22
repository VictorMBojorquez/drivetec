import json
from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from .models import AuditEvent, Report, Unit


def fnv(s):
    """FNV-1a 32 bits, igual que en el cliente."""
    a = 0x811c9dc5
    for c in s.encode('utf-8'):
        a = ((a ^ c) * 0x01000193) & 0xffffffff
    return f'{a:08x}'


def chain(n=3):
    """Cadena de eventos de auditoría válida (p encadena con h anterior, h = FNV correcto)."""
    ev = []
    p = '0'
    for i in range(n):
        e = {'t': f'2026-01-01T00:0{i}:00Z', 'st': 'folio', 'd': f'evento {i}', 'p': p}
        e['h'] = fnv(e['p'] + e['t'] + e['st'] + e['d'])
        ev.append(e)
        p = e['h']
    return ev


class Base(TestCase):
    def setUp(self):
        self.c = Client()
        self.u = User.objects.create_user('op', 'op@example.com', 'pw')
        Group.objects.get_or_create(name='Operador')
        self.u.groups.add(Group.objects.get(name='Operador'))
        self.c.force_login(self.u)


class AccesoTests(Base):
    def test_api_sin_sesion_devuelve_401(self):
        r = Client().get('/api/state')
        self.assertEqual(r.status_code, 401)

    def test_index_requiere_login(self):
        self.assertEqual(Client().get('/').status_code, 302)

    def test_config_requiere_login(self):
        self.assertEqual(Client().get('/config.js').status_code, 302)

    def test_usuario_sin_grupo_no_puede_escribir(self):
        User.objects.create_user('solo', 's@example.com', 'pw')
        c = Client()
        c.force_login(User.objects.get(username='solo'))
        r = c.put('/api/state', json.dumps({'reports': [], 'units': [], 'log': []}), content_type='application/json')
        self.assertEqual(r.status_code, 403)


class DatosTests(Base):
    def test_semilla_de_seis_unidades(self):
        self.assertEqual(Unit.objects.count(), 6)
        self.assertIn('A-12', list(Unit.objects.values_list('code', flat=True)))

    def test_grupo_operador_existe(self):
        self.assertTrue(Group.objects.filter(name='Operador').exists())

    def test_estado_guarda_y_lee(self):
        self.c.force_login(self.u)
        body = {'reports': [{'folio': 'DT-2026-2042', 'tipo': 'choque'}],
                'units': [{'id': 'A-12', 'busy': True}], 'log': chain()}
        r = self.c.put('/api/state', json.dumps(body), content_type='application/json')
        self.assertEqual(r.json()['ok'], True)
        self.assertTrue(Unit.objects.get(code='A-12').busy)
        st = self.c.get('/api/state').json()
        self.assertEqual(st['reports'][0]['folio'], 'DT-2026-2042')
        self.assertEqual(st['seq'], 2042)
        self.assertEqual(AuditEvent.objects.count(), 3)


class ValidacionTests(Base):
    def test_json_malformado_devuelve_400(self):
        r = self.c.put('/api/state', 'no-json', content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_eventos_invalidos_devuelve_400(self):
        r = self.c.put('/api/state', json.dumps({'log': [{'t': 'x', 'st': 'y'}]}), content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_cadena_de_auditoria_alterada_se_rechaza(self):
        ev = chain()
        ev[1]['p'] = '00000000'  # rompe el encadenamiento
        r = self.c.put('/api/state', json.dumps({'log': ev}), content_type='application/json')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(AuditEvent.objects.count(), 0)

    def test_hash_cliente_falso_se_rechaza(self):
        ev = chain()
        ev[2]['h'] = 'deadbeef'
        r = self.c.put('/api/state', json.dumps({'log': ev}), content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_metodo_no_permitido_en_state(self):
        r = self.c.delete('/api/state')
        self.assertEqual(r.status_code, 405)


class RankTests(Base):
    def test_unidad_mas_cercana_sugiere_a12(self):
        r = self.c.post('/api/rank', json.dumps({'lat': 32.5276, 'lng': -117.0240, 'tipo': 'choque', 'her': 1}),
                        content_type='application/json')
        d = r.json()
        self.assertEqual(d['source'], 'estimate')
        self.assertTrue(d['units'][0]['need'])
        self.assertEqual(d['units'][0]['id'], 'A-12')

    def test_coordenadas_invalidas_devuelve_400(self):
        r = self.c.post('/api/rank', json.dumps({'lat': 'x', 'lng': None, 'tipo': 'choque'}),
                        content_type='application/json')
        self.assertEqual(r.status_code, 400)


class AuditoriaTests(Base):
    def test_verificacion_ok(self):
        self.c.put('/api/state', json.dumps({'log': chain(4)}), content_type='application/json')
        r = self.c.get('/api/audit/verify').json()
        self.assertTrue(r['ok'])
        self.assertEqual(r['count'], 4)

    def test_verificacion_detecta_alteracion(self):
        self.c.put('/api/state', json.dumps({'log': chain(3)}), content_type='application/json')
        e = AuditEvent.objects.all()[1]
        AuditEvent.objects.filter(pk=e.pk).update(d='alterado')
        r = self.c.get('/api/audit/verify').json()
        self.assertFalse(r['ok'])
        self.assertEqual(r['bad'], 2)


class TranscripcionTraduccionTests(Base):
    def test_transcribe_requiere_sesion(self):
        self.assertEqual(Client().post('/api/transcribe').status_code, 401)

    def test_transcribe_sin_archivo_400(self):
        r = self.c.post('/api/transcribe')
        self.assertEqual(r.status_code, 400)

    def test_transcribe_sin_modelo_503(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        info = self.c.post('/api/transcribe', {'audio': SimpleUploadedFile('a.webm', b'RIFF')}, format='multipart')
        self.assertEqual(info.status_code, 503)
        self.assertIn('WHISPER_MODEL', info.json()['error'])

    def test_translate_requiere_sesion(self):
        self.assertEqual(Client().post('/api/translate', data='{}', content_type='application/json').status_code, 401)

    def test_translate_sin_clave_503(self):
        r = self.c.post('/api/translate', json.dumps({'q': 'hello'}), content_type='application/json')
        self.assertEqual(r.status_code, 503)
        self.assertIn('GOOGLE_SERVER_KEY', r.json()['error'])

    def test_translate_texto_vacio_400(self):
        r = self.c.post('/api/translate', json.dumps({'q': '   '}), content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_metodo_get_405(self):
        self.assertEqual(self.c.get('/api/translate').status_code, 405)
