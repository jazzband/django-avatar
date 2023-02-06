import django.core.files.storage
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import avatar.models


class Migration(migrations.Migration):
    dependencies = [
        ("avatar", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="avatar",
            options={"verbose_name": "avatar", "verbose_name_plural": "avatars"},
        ),
        migrations.AlterField(
            model_name="avatar",
            name="avatar",
            field=models.ImageField(
                blank=True,
                max_length=1024,
                storage=django.core.files.storage.FileSystemStorage(),
                upload_to=avatar.models.avatar_path_handler,
                verbose_name="avatar",
            ),
        ),
        migrations.AlterField(
            model_name="avatar",
            name="date_uploaded",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="uploaded at"
            ),
        ),
        migrations.AlterField(
            model_name="avatar",
            name="primary",
            field=models.BooleanField(default=False, verbose_name="primary"),
        ),
        migrations.AlterField(
            model_name="avatar",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
    ]
