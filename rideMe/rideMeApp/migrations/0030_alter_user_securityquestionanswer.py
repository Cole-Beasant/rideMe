# Generated by Django 4.1.6 on 2023-03-27 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rideMeApp', '0029_user_securityquestion_user_securityquestionanswer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='securityQuestionAnswer',
            field=models.CharField(default='rideMe', max_length=256),
        ),
    ]
