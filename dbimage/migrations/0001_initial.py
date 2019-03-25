# Generated by Django 2.1.7 on 2019-03-25 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DBImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, unique=True)),
                ('content_type', models.CharField(max_length=128)),
                ('content', models.BinaryField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
