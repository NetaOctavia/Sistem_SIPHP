# Generated manually for SIPHP optimization

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_pasar_alter_pesankontak_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='hargakomoditas',
            options={'ordering': ['-tanggal', 'pasar', 'komoditas'], 'verbose_name_plural': 'Harga Komoditas'},
        ),
        migrations.AlterModelOptions(
            name='komoditas',
            options={'ordering': ['nama'], 'verbose_name_plural': 'Komoditas'},
        ),
        migrations.AlterModelOptions(
            name='pasar',
            options={'ordering': ['nama_pasar'], 'verbose_name_plural': 'Pasar'},
        ),
        migrations.RemoveField(
            model_name='hargakomoditas',
            name='nama_pasar_lama',
        ),
        migrations.AlterField(
            model_name='hargakomoditas',
            name='pasar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='harga_komoditas_set', to='accounts.pasar'),
        ),
        migrations.AlterField(
            model_name='pasar',
            name='nama_pasar',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='hargakomoditas',
            unique_together={('komoditas', 'pasar', 'tanggal')},
        ),
    ]
