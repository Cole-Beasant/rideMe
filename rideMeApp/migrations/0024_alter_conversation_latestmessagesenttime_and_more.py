# Generated by Django 4.1.6 on 2023-03-04 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rideMeApp', '0023_alter_conversation_latestmessagesenttime_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='latestMessageSentTime',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='timeSent',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='posting',
            name='submissionTime',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='registrationTime',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
