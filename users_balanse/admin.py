from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users_balanse import models
from users_balanse.models import Transaction

admin.site.register(models.User, UserAdmin)
admin.site.register(Transaction)


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("currency", "amount", "user")
    list_display_links = ("currency", "amount")
    fields = ["currency", "amount", "user"]

    class Meta:
        verbose_name = "Счёт"
        verbose_name_plural = "Счета"
