import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    SeparateDatabaseAndState: tabel accounts_hargakomoditas sudah dibuat oleh
    accounts migrations. Kita hanya mendaftarkan state ke Django ORM
    tanpa eksekusi DDL di database.
    """

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0013_delete_berita_alter_hargakomoditas_unique_together_and_more'),
        ('komoditas', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='HargaKomoditas',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('tanggal', models.DateField()),
                        ('harga', models.DecimalField(decimal_places=0, max_digits=12)),
                        ('diinput_oleh', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                        ('komoditas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='harga_set', to='komoditas.komoditas')),
                        ('pasar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='harga_komoditas_set', to='accounts.pasar')),
                    ],
                    options={
                        'verbose_name_plural': 'Harga Komoditas',
                        'db_table': 'accounts_hargakomoditas',
                        'ordering': ['-tanggal', 'pasar', 'komoditas'],
                        'unique_together': {('komoditas', 'pasar', 'tanggal')},
                    },
                ),
            ],
            database_operations=[],  # Jangan buat tabel — sudah ada dari accounts migration
        ),
    ]
