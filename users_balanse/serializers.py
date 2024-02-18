from users_balanse.models import Account, Transaction
from rest_framework import serializers


class AccountSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()
    # current_currency = serializers.SerializerMethodField()

    class Meta:
        model = Account
        exclude = ("user",)

    def get_user_full_name(self, obj):
        if not isinstance(obj, Transaction):
            return obj.user.get_full_name()

    # def get_current_currency(self, obj):
    #     return obj.currency


class TransactionSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="get_transaction_type_display")
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()
    sender_balance = serializers.SerializerMethodField()
    receiver_balance = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        exclude = ("sender", "receiver", "transaction_type")

    def get_sender_name(self, obj):
        return obj.sender.get_full_name()

    def get_receiver_name(self, obj):
        if obj.receiver:
            return obj.receiver.get_full_name()

    def get_sender_balance(self, obj):
        return obj.sender.account.amount

    def get_receiver_balance(self, obj):
        if obj.receiver:
            return obj.receiver.account.amount


class ConvertedBalanceSerializer(serializers.Serializer):
    user = serializers.CharField()
    currency = serializers.CharField()
    converted_balance = serializers.DecimalField(max_digits=32, decimal_places=20)
