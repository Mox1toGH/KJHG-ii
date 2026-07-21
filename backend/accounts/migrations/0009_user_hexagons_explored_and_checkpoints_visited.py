# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_friend_status_friend_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='hexagons_explored',
            field=models.PositiveIntegerField(default=0, verbose_name='Hexagons explored'),
        ),
        migrations.AddField(
            model_name='user',
            name='checkpoints_visited',
            field=models.PositiveIntegerField(default=0, verbose_name='Checkpoints visited'),
        ),
    ]
