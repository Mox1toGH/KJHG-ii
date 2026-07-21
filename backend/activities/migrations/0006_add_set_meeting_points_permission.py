from django.db import migrations


PERMISSION = ('meeting_points.set', 'Set meeting points')


def add_permission(apps, schema_editor):
    ActivityPermission = apps.get_model('activities', 'ActivityPermission')
    ActivityPermission.objects.update_or_create(
        code=PERMISSION[0], defaults={'name': PERMISSION[1]}
    )


def remove_permission(apps, schema_editor):
    ActivityPermission = apps.get_model('activities', 'ActivityPermission')
    ActivityPermission.objects.filter(code=PERMISSION[0]).delete()


class Migration(migrations.Migration):
    dependencies = [('activities', '0005_add_upload_checkpoint_photos_permission')]

    operations = [migrations.RunPython(add_permission, remove_permission)]
