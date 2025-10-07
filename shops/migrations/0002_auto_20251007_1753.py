
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0001_initial'),  # جایگزین با نام آخرین migration
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
