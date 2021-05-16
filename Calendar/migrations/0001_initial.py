# Generated by Django 3.2.3 on 2021-05-16 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('urlAddr', models.CharField(default='', max_length=500)),
                ('meetAddr', models.CharField(default='', max_length=500)),
                ('title', models.CharField(default='', max_length=50)),
                ('meetType', models.CharField(default='', max_length=25)),
                ('description', models.CharField(default='', max_length=1000)),
            ],
        ),
    ]
