from django.db import migrations, models


class Migration(migrations.Migration):
    """
    SeparateDatabaseAndState: tabel accounts_pesankontak sudah dibuat oleh
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
                    name='PesanKontak',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('nama', models.CharField(max_length=100)),
                        ('email', models.EmailField(max_length=254)),
                        ('telepon', models.CharField(blank=True, max_length=20, null=True)),
                        ('subjek', models.CharField(max_length=200)),
                        ('pesan', models.TextField()),
                        ('is_read', models.BooleanField(default=False)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                    ],
                    options={
                        'verbose_name_plural': 'Pesan Kontak',
                        'db_table': 'accounts_pesankontak',
                        'ordering': ['-created_at'],
                    },
                ),
            ],
            database_operations=[],  # Jangan buat tabel — sudah ada dari accounts migration
        ),
    ]
