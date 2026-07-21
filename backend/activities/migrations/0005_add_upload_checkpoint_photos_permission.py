from django.db import migrations


PERMISSION = ('checkpoints.photos.upload', 'Upload photos to checkpoints/locations')


def add_permission(apps, schema_editor):
    ActivityPermission = apps.get_model('activities', 'ActivityPermission')
    ActivityPermission.objects.update_or_create(
        code=PERMISSION[0], defaults={'name': PERMISSION[1]}
    )


def remove_permission(apps, schema_editor):
    ActivityPermission = apps.get_model('activities', 'ActivityPermission')
    ActivityPermission.objects.filter(code=PERMISSION[0]).delete()


class Migration(migrations.Migration):
    dependencies = [('activities', '0004_seed_activity_permissions')]

    operations = [migrations.RunPython(add_permission, remove_permission)]
