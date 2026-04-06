

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerelo',
            name='cat',
            field=models.CharField(default='no', max_length=10),
        ),
    ]
