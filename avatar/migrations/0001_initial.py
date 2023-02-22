import django.core.files.storage
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import avatar.models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Avatar",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("primary", models.BooleanField(default=False)),
                (
                    "avatar",
                    models.ImageField(
                        storage=django.core.files.storage.FileSystemStorage(),
                        max_length=1024,
                        upload_to=avatar.models.avatar_file_path,
                        blank=True,
                    ),
                ),
                (
                    "date_uploaded",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
        ),
    ]
