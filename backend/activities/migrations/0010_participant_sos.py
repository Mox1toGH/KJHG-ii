from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('activities', '0009_add_create_locations_permission')]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='sos_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='participant',
            name='sos_activated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
