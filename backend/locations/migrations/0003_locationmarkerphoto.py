import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('locations', '0002_locationmarker_color')]

    operations = [
        migrations.CreateModel(
            name='LocationMarkerPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='location-markers/%Y/%m/')),
                ('is_main', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('marker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='locations.locationmarker')),
            ],
            options={'ordering': ['-is_main', 'created_at']},
        ),
    ]
