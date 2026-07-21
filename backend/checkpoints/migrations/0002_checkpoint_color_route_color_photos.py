from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('checkpoints', '0001_initial')]

    operations = [
        migrations.AddField('checkpoint', 'color', models.CharField(default='#9333EA', max_length=20)),
        migrations.AddField('route', 'color', models.CharField(default='#8B5CF6', max_length=20)),
        migrations.CreateModel(
            name='CheckpointPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='checkpoints/%Y/%m/')),
                ('is_main', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('checkpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='checkpoints.checkpoint')),
            ],
        ),
        migrations.CreateModel(
            name='RoutePhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='routes/%Y/%m/')),
                ('is_main', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='checkpoints.route')),
            ],
        ),
    ]
