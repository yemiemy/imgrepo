# Generated by Django 3.1.5 on 2021-05-06 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20210506_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='description',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='item',
            name='dimension',
            field=models.CharField(default='1920x1080', help_text='1920x1080, 2400x1600', max_length=50),
        ),
        migrations.AlterField(
            model_name='item',
            name='downloadable_file',
            field=models.FileField(help_text='Please upload as a zip file.', upload_to='imgrepo/downloadable-files/'),
        ),
        migrations.AlterField(
            model_name='item',
            name='format',
            field=models.CharField(default='JPG', help_text='JPG, PNG etc.', max_length=50),
        ),
    ]
