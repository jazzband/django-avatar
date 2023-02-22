from django.db import migrations

import avatar.models


class Migration(migrations.Migration):
    dependencies = [
        ("avatar", "0002_add_verbose_names_to_avatar_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="avatar",
            name="avatar",
            field=avatar.models.AvatarField(),
        ),
    ]
