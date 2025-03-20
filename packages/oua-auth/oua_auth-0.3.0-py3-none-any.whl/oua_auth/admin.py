"""Admin configuration for the oua_auth app."""

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from .models import BlacklistedToken, SuspiciousActivity, UserSecurityProfile


@admin.register(BlacklistedToken)
class BlacklistedTokenAdmin(admin.ModelAdmin):
    """Admin interface for BlacklistedToken."""

    list_display = (
        "token_hash_truncated",
        "blacklisted_by",
        "created_at",
        "expires_at",
        "is_expired",
    )
    list_filter = ("created_at", "expires_at")
    search_fields = ("token_hash", "blacklisted_by", "reason")
    readonly_fields = ("token_hash", "created_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    actions = ["delete_expired_tokens", "extend_expiration"]

    def token_hash_truncated(self, obj):
        """Display truncated token hash for better readability."""
        return obj.token_hash[:10] + "..."

    token_hash_truncated.short_description = "Token Hash"

    def is_expired(self, obj):
        """Display if the token is expired with color coding."""
        is_expired = obj.expires_at < timezone.now()
        return format_html(
            '<span style="color: {};">{}</span>',
            "red" if is_expired else "green",
            "Expired" if is_expired else "Active",
        )

    is_expired.short_description = "Status"

    def get_urls(self):
        """Add custom URLs for admin actions."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "clean_expired/",
                self.admin_site.admin_view(self.clean_expired_view),
                name="oua_auth_blacklistedtoken_clean_expired",
            ),
        ]
        return custom_urls + urls

    def clean_expired_view(self, request):
        """View for cleaning expired tokens."""
        if request.method == "POST":
            count = BlacklistedToken.clean_expired_tokens()
            self.message_user(
                request, f"{count} expired tokens were removed.", messages.SUCCESS
            )
            return redirect("..")

        return render(
            request,
            "admin/clean_expired_confirm.html",
            {
                "title": "Clean Expired Tokens",
            },
        )

    def delete_expired_tokens(self, request, queryset):
        """Action to delete expired tokens."""
        count = BlacklistedToken.clean_expired_tokens()
        self.message_user(
            request, f"{count} expired tokens were removed.", messages.SUCCESS
        )

    delete_expired_tokens.short_description = "Delete all expired tokens"

    def extend_expiration(self, request, queryset):
        """Extend the expiration of selected tokens by 24 hours."""
        count = 0
        for token in queryset:
            token.expires_at = token.expires_at + timezone.timedelta(days=1)
            token.save()
            count += 1
        self.message_user(
            request,
            f"Extended expiration for {count} tokens by 24 hours.",
            messages.SUCCESS,
        )

    extend_expiration.short_description = "Extend expiration by 24 hours"

    def has_add_permission(self, request):
        """
        Disable direct token creation through admin as tokens should only
        be blacklisted through the API.
        """
        return False


class SuspiciousActivityAdmin(admin.ModelAdmin):
    """Admin configuration for SuspiciousActivity model."""

    list_display = (
        "user_identifier",
        "activity_type",
        "ip_address",
        "timestamp",
        "details_truncated",
    )
    list_filter = ("activity_type", "timestamp")
    search_fields = ("user_identifier", "ip_address", "activity_type", "details")
    readonly_fields = ("timestamp",)
    actions = ["cleanup_old_activities"]

    def details_truncated(self, obj):
        """Display truncated details for better readability."""
        if not obj.details:
            return "—"
        details = obj.details
        if len(details) > 50:
            return details[:47] + "..."
        return details

    details_truncated.short_description = "Details"

    def cleanup_old_activities(self, request, queryset):
        """Action to clean up old activities."""
        count = SuspiciousActivity.cleanup_old_activities(days=30)
        self.message_user(
            request,
            f"{count} old activities were removed (older than 30 days).",
            messages.SUCCESS,
        )

    cleanup_old_activities.short_description = "Delete activities older than 30 days"


class UserSecurityProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserSecurityProfile model."""

    list_display = (
        "user_email",
        "is_locked",
        "locked_until",
        "failed_login_attempts",
        "last_failed_login",
    )
    list_filter = ("is_locked", "last_failed_login")
    search_fields = ("user__email", "user__username", "lock_reason")
    actions = ["unlock_accounts", "reset_failed_attempts"]
    readonly_fields = ("last_failed_login", "last_login_ip")

    def user_email(self, obj):
        """Display user email for better identification."""
        return obj.user.email

    user_email.short_description = "User"

    def unlock_accounts(self, request, queryset):
        """Action to unlock selected accounts."""
        count = 0
        for profile in queryset:
            if profile.is_locked:
                profile.unlock_account()
                count += 1
        self.message_user(request, f"Unlocked {count} accounts.", messages.SUCCESS)

    unlock_accounts.short_description = "Unlock selected accounts"

    def reset_failed_attempts(self, request, queryset):
        """Action to reset failed login attempts."""
        count = 0
        for profile in queryset:
            if profile.failed_login_attempts > 0:
                profile.failed_login_attempts = 0
                profile.save(update_fields=["failed_login_attempts"])
                count += 1
        self.message_user(
            request, f"Reset failed attempts for {count} accounts.", messages.SUCCESS
        )

    reset_failed_attempts.short_description = "Reset failed login attempts"

    def get_urls(self):
        """Add custom URLs for admin actions."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "create_missing_profiles/",
                self.admin_site.admin_view(self.create_profiles_view),
                name="oua_auth_usersecurityprofile_create_missing",
            ),
        ]
        return custom_urls + urls

    def create_profiles_view(self, request):
        """View for creating missing security profiles."""
        if request.method == "POST":
            count = UserSecurityProfile.auto_create_profiles()
            self.message_user(
                request, f"Created {count} new security profiles.", messages.SUCCESS
            )
            return redirect("..")

        return render(
            request,
            "admin/create_profiles_confirm.html",
            {
                "title": "Create Missing Security Profiles",
            },
        )


# Register models with custom admin interfaces
admin.site.register(SuspiciousActivity, SuspiciousActivityAdmin)

# Only register UserSecurityProfile if it's defined (it may not be defined during migrations)
try:
    from .models import UserSecurityProfile

    admin.site.register(UserSecurityProfile, UserSecurityProfileAdmin)
except (ImportError, admin.sites.AlreadyRegistered):
    pass
