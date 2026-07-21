from django.db import migrations


PERMISSIONS = (
    ('checkpoints.create', 'Create checkpoints/locations'),
    ('participants.map.view', 'View participants on the map'),
)


def seed_permissions(apps, schema_editor):
    ActivityPermission = apps.get_model('activities', 'ActivityPermission')
    for code, name in PERMISSIONS:
        ActivityPermission.objects.update_or_create(
            code=code,
            defaults={'name': name},
        )


def remove_permissions(apps, schema_editor):
    ActivityPermission = apps.get_model('activities', 'ActivityPermission')
    ActivityPermission.objects.filter(code__in=[code for code, _ in PERMISSIONS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0003_activitypermission_rolepermission_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_permissions, remove_permissions),
    ]
