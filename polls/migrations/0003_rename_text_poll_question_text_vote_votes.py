# Generated by Django 4.1.2 on 2023-03-02 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_alter_poll_pub_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='poll',
            old_name='text',
            new_name='question_text',
        ),
        migrations.AddField(
            model_name='vote',
            name='votes',
            field=models.IntegerField(default=0),
        ),
    ]
