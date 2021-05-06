# Generated by Django 3.1.5 on 2021-05-04 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20210504_1512'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='label',
        ),
        migrations.AddField(
            model_name='item',
            name='downloadable_file',
            field=models.FileField(default='defaul.png', upload_to='imgrepo/downloadable-files/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='downloads',
            field=models.IntegerField(default=0),
        ),
    ]
