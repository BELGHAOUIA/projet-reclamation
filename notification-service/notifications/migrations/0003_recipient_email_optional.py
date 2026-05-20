from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_delete_notificationtemplate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='recipient_email',
            field=models.CharField(max_length=255, blank=True, default=''),
        ),
    ]
