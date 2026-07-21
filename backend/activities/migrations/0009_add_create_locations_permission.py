from django.db import migrations


PERMISSION = ('locations.create', 'Create checkpoints/locations')


def add_permission(apps, schema_editor):
    ActivityPermission = apps.get_model('activities', 'ActivityPermission')
    RolePermission = apps.get_model('activities', 'RolePermission')
    location_permission, _ = ActivityPermission.objects.update_or_create(
        code=PERMISSION[0], defaults={'name': PERMISSION[1]}
    )

    # Before this split, checkpoints.create also authorized the legacy locations app.
    # Preserve that access for existing roles while keeping future grants separate.
    for grant in RolePermission.objects.filter(
        permission__code='checkpoints.create'
    ).only('role_id', 'scope'):
        RolePermission.objects.get_or_create(
            role_id=grant.role_id,
            permission_id=location_permission.id,
            defaults={'scope': grant.scope},
        )


def remove_permission(apps, schema_editor):
    ActivityPermission = apps.get_model('activities', 'ActivityPermission')
    ActivityPermission.objects.filter(code=PERMISSION[0]).delete()


class Migration(migrations.Migration):
    dependencies = [('activities', '0008_add_create_routes_permission')]

    operations = [migrations.RunPython(add_permission, remove_permission)]
