from django.db import migrations, models


class Migration(migrations.Migration):
    """
    SeparateDatabaseAndState: tabel accounts_komoditas sudah dibuat oleh
    accounts migrations. Kita hanya mendaftarkan state ke Django ORM
    tanpa eksekusi DDL di database.
    """

    initial = True

    dependencies = [
        ('accounts', '0013_delete_berita_alter_hargakomoditas_unique_together_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Komoditas',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('nama', models.CharField(max_length=100, unique=True)),
                        ('satuan', models.CharField(default='kg', max_length=20)),
                        ('keterangan', models.TextField(blank=True, null=True)),
                    ],
                    options={
                        'verbose_name_plural': 'Komoditas',
                        'db_table': 'accounts_komoditas',
                        'ordering': ['nama'],
                    },
                ),
            ],
            database_operations=[],  # Jangan buat tabel — sudah ada dari accounts migration
        ),
    ]
