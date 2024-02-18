from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    groups = models.ManyToManyField(
        Group, related_name="custom_user_groups", blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_user_permissions"
    )

    class Meta:
        db_table = "user_balance"

    def __str__(self):
        return self.get_full_name()


class Account(models.Model):
    currency = models.CharField(max_length=50, verbose_name="Валюта")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


class Transaction(models.Model):

    DEPOSIT = "D"
    WITHDRAWAL = "W"
    SEND = "S"
    TRANSACTION_TYPE_CHOICES = [
        (DEPOSIT, "Зачисление"),
        (WITHDRAWAL, "Списание"),
        (SEND, "Перевод"),
    ]

    transaction_type = models.CharField(
        max_length=1, choices=TRANSACTION_TYPE_CHOICES, null=True, blank=True
    )
    currency = models.CharField(max_length=50, verbose_name="Валюта")
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_transactions",
        null=True,
        blank=True,
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_transactions",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
