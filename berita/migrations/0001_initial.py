from django.db import migrations, models


class Migration(migrations.Migration):
    """
    SeparateDatabaseAndState: tabel accounts_berita sudah dibuat oleh
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
                    name='Berita',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('judul', models.CharField(max_length=255)),
                        ('ringkasan', models.TextField(blank=True, null=True)),
                        ('url_sumber', models.URLField(max_length=500)),
                        ('gambar_url', models.URLField(blank=True, max_length=500, null=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        'verbose_name_plural': 'Berita',
                        'db_table': 'accounts_berita',
                        'ordering': ['-created_at'],
                    },
                ),
            ],
            database_operations=[],  # Jangan buat tabel — sudah ada dari accounts migration
        ),
    ]
