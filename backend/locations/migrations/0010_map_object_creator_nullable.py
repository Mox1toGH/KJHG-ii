from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('locations', '0009_activityzone_trigger_action_and_more')]
    operations = [
        migrations.AlterField(model_name='locationmarker', name='created_by', field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='created_markers', to='accounts.user')),
        migrations.AlterField(model_name='activityzone', name='created_by', field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='created_zones', to='accounts.user')),
    ]
