from django.db import migrations


PERMISSION = ('routes.create', 'Create routes')


def add_permission(apps, schema_editor):
    ActivityPermission = apps.get_model('activities', 'ActivityPermission')
    ActivityPermission.objects.update_or_create(
        code=PERMISSION[0], defaults={'name': PERMISSION[1]}
    )
    ActivityPermission.objects.filter(code='checkpoints.create').update(
        name='Create checkpoints'
    )


def remove_permission(apps, schema_editor):
    ActivityPermission = apps.get_model('activities', 'ActivityPermission')
    ActivityPermission.objects.filter(code=PERMISSION[0]).delete()
    ActivityPermission.objects.filter(code='checkpoints.create').update(
        name='Create checkpoints/locations'
    )


class Migration(migrations.Migration):
    dependencies = [('activities', '0007_activity_default_role')]

    operations = [migrations.RunPython(add_permission, remove_permission)]
