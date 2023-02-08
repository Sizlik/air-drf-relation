# Generated by Django 3.2.4 on 2022-05-13 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('table', '0003_auto_20220513_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='company',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='materials', to='table.company'),
            preserve_default=False,
        ),
    ]