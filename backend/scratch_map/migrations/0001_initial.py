import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ScratchDiscovery',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('h3_index', models.CharField(max_length=16)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('discovered_at', models.DateTimeField(auto_now_add=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='scratch_discoveries',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['discovered_at', 'id'],
                'indexes': [
                    models.Index(fields=['user'], name='scratch_disc_user_idx'),
                    models.Index(fields=['h3_index'], name='scratch_disc_h3_idx'),
                    models.Index(fields=['user', 'discovered_at'], name='scratch_disc_user_date_idx'),
                ],
                'constraints': [
                    models.UniqueConstraint(
                        fields=('user', 'h3_index'),
                        name='scratch_discovery_user_h3_unique',
                    ),
                ],
            },
        ),
    ]
