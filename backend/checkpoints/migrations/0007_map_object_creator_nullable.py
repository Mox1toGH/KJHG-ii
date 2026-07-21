from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('checkpoints', '0006_checkpointqrcode_points')]
    operations = [
        migrations.AlterField(model_name='checkpoint', name='created_by', field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='created_checkpoints', to='accounts.user')),
        migrations.AlterField(model_name='checkpointqrcode', name='created_by', field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='created_checkpoint_qr_codes', to='accounts.user')),
        migrations.AlterField(model_name='route', name='created_by', field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='created_routes', to='accounts.user')),
    ]
