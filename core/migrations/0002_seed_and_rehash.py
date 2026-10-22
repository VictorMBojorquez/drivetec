# Siembra inicial de unidades, grupo «Operador» y migración del esquema de hashes.
#
# La fórmula del SHA-256 del servidor cambió (ahora incluye p y h del cliente, que
# antes quedaban fuera de la verificación). Este RunPython recalcula la cadena
# existente con la fórmula nueva para que /api/audit/verify siga íntegra.
#
# Nota: la semilla de unidades se movió aquí (antes se creaba en el GET de
# /api/state); edítala en este archivo si necesitas otras bases.

from django.db import migrations

SEED = [
    ("A-12", "Ambulancia", 32.5280, -117.0290),
    ("A-07", "Ambulancia", 32.5090, -116.9800),
    ("P-07", "Patrulla", 32.5330, -117.0200),
    ("P-03", "Patrulla", 32.4980, -117.0050),
    ("B-03", "Bomberos", 32.5400, -117.0100),
    ("B-01", "Bomberos", 32.5200, -117.0400),
]


def seed(apps, schema_editor):
    Unit = apps.get_model('core', 'Unit')
    if not Unit.objects.exists():
        Unit.objects.bulk_create([Unit(code=c, kind=k, lat=la, lng=lo) for c, k, la, lo in SEED])
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Operador')


def rehash(apps, schema_editor):
    import hashlib

    AuditEvent = apps.get_model('core', 'AuditEvent')
    prev = '0'
    for e in AuditEvent.objects.order_by('id'):
        e.sha = hashlib.sha256((prev + e.p + e.h + e.t + e.st + e.d).encode()).hexdigest()
        e.save(update_fields=['sha'])
        prev = e.sha


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
        migrations.RunPython(rehash, migrations.RunPython.noop),
    ]
