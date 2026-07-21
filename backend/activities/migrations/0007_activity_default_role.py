import django.db.models.deletion
from django.db import migrations, models


DEFAULT_ROLE_NAME = 'User'
VIEW_PERMISSION_CODE = 'participants.map.view'


def create_defaults_for_existing_activities(apps, schema_editor):
    Activity = apps.get_model('activities', 'Activity')
    ActivityRole = apps.get_model('activities', 'ActivityRole')
    ActivityPermission = apps.get_model('activities', 'ActivityPermission')
    RolePermission = apps.get_model('activities', 'RolePermission')
    view_permission = ActivityPermission.objects.get(code=VIEW_PERMISSION_CODE)

    for activity in Activity.objects.all():
        role, _ = ActivityRole.objects.get_or_create(
            activity=activity,
            name=DEFAULT_ROLE_NAME,
            defaults={'description': 'Default activity participant'},
        )
        RolePermission.objects.get_or_create(
            role=role,
            permission=view_permission,
            defaults={'scope': {'visibility': 'everyone'}},
        )
        activity.default_role_id = role.pk
        activity.save(update_fields=['default_role'])


class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0006_add_set_meeting_points_permission'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='default_role',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='default_for_activities',
                to='activities.activityrole',
            ),
        ),
        migrations.RunPython(create_defaults_for_existing_activities, migrations.RunPython.noop),
    ]
