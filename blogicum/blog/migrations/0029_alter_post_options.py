# Generated by Django 3.2.16 on 2024-03-11 18:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0028_alter_post_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-pub_date',), 'verbose_name': 'публикация', 'verbose_name_plural': 'Публикации'},
        ),
    ]
