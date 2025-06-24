# Generated manually

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0004_alter_product_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='unique_id',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]