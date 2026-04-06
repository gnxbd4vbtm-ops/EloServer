

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elo', '0002_playerelo_cat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerelo',
            name='cat',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='playerelo',
            name='elo',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='playerelo',
            name='gamemode',
            field=models.CharField(max_length=50),
        ),
    ]
