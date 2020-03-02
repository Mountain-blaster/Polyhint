# Generated by Django 3.0.2 on 2020-03-02 12:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('GED', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notifs', models.CharField(max_length=45)),
                ('eleve_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GED.Eleve')),
                ('prof_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GED.Professeur')),
            ],
        ),
    ]
