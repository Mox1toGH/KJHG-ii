import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('checkpoints', '0003_routepointphoto_delete_routephoto'),
        ('activities', '0011_participant_current_zones'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckpointQRCode',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('qr_token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('image', models.ImageField(upload_to='checkpoint_qrcodes/%Y/%m/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('checkpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qr_codes', to='checkpoints.checkpoint')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_checkpoint_qr_codes', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['created_at']},
        ),
        migrations.CreateModel(
            name='CheckpointQRCodeScan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('scanned_at', models.DateTimeField(auto_now_add=True)),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkpoint_qr_scans', to='activities.participant')),
                ('qr_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scans', to='checkpoints.checkpointqrcode')),
            ],
            options={
                'ordering': ['-scanned_at'],
                'constraints': [models.UniqueConstraint(fields=('qr_code', 'participant'), name='unique_qr_code_participant_scan')],
            },
        ),
    ]
