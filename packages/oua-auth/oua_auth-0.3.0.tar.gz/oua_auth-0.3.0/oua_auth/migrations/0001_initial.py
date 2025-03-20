"""Initial migration creating the BlacklistedToken model."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Initial migration for the oua_auth app."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BlacklistedToken",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "token_hash",
                    models.CharField(db_index=True, max_length=64, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                (
                    "blacklisted_by",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("reason", models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                "verbose_name": "Blacklisted Token",
                "verbose_name_plural": "Blacklisted Tokens",
                "indexes": [
                    models.Index(fields=["expires_at"], name="oua__expires_6f56ee_idx"),
                ],
            },
        ),
    ]
