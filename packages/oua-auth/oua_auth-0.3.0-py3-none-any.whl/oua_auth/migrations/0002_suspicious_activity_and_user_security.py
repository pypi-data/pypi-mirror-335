"""
Migration to add SuspiciousActivity and UserSecurityProfile models.
"""

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("oua_auth", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blacklistedtoken",
            name="reason",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="SuspiciousActivity",
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
                ("user_identifier", models.CharField(db_index=True, max_length=255)),
                (
                    "ip_address",
                    models.CharField(
                        blank=True, db_index=True, max_length=45, null=True
                    ),
                ),
                ("activity_type", models.CharField(db_index=True, max_length=50)),
                ("details", models.TextField(blank=True, null=True)),
                (
                    "timestamp",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
            ],
            options={
                "verbose_name": "Suspicious Activity",
                "verbose_name_plural": "Suspicious Activities",
                "ordering": ["-timestamp"],
            },
        ),
        migrations.CreateModel(
            name="UserSecurityProfile",
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
                ("is_locked", models.BooleanField(default=False)),
                (
                    "lock_reason",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("locked_until", models.DateTimeField(blank=True, null=True)),
                ("failed_login_attempts", models.PositiveIntegerField(default=0)),
                ("last_failed_login", models.DateTimeField(blank=True, null=True)),
                (
                    "last_login_ip",
                    models.CharField(blank=True, max_length=45, null=True),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="security_profile",
                        to="auth.user",
                    ),
                ),
            ],
            options={
                "verbose_name": "User Security Profile",
                "verbose_name_plural": "User Security Profiles",
            },
        ),
        migrations.AddIndex(
            model_name="suspiciousactivity",
            index=models.Index(
                fields=["user_identifier", "timestamp"],
                name="oua__user_id_e5e87f_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="suspiciousactivity",
            index=models.Index(
                fields=["ip_address", "timestamp"],
                name="oua__ip_addr_36d88f_idx",
            ),
        ),
    ]
