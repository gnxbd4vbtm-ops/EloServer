

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elo', '0003_alter_playerelo_cat_alter_playerelo_elo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerelo',
            name='cat',
            field=models.CharField(default='no', max_length=10),
        ),
        migrations.AlterField(
            model_name='playerelo',
            name='elo',
            field=models.IntegerField(default=1000),
        ),
        migrations.AlterField(
            model_name='playerelo',
            name='gamemode',
            field=models.CharField(max_length=100),
        ),
    ]
