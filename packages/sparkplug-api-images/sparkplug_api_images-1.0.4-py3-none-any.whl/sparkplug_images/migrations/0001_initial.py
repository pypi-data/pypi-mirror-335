import sparkplug_images.uploads
from django.db import migrations, models
import django_extensions.db.fields
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('uuid', django_extensions.db.fields.ShortUUIDField(blank=True, editable=False)),
                ('file', sorl.thumbnail.fields.ImageField(upload_to=sparkplug_images.uploads.file_location)),
            ],
        ),
    ]
