# Generated by Django 4.1.2 on 2023-03-04 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_remove_vote_votes'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='votes',
            field=models.IntegerField(default=0),
        ),
    ]
