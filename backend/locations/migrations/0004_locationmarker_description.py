from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('locations', '0003_locationmarkerphoto')]

    operations = [
        migrations.AddField(
            model_name='locationmarker',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
