import decimal
from decimal import ROUND_HALF_UP

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework import status
from .models import User, Account, Transaction
from .parser import get_exchange_rates
from .serializers import (
    AccountSerializer,
    TransactionSerializer,
    ConvertedBalanceSerializer,
)


class InsufficientFundsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Недостаточно средств"
    default_code = "insufficient_funds"


class UserBalanceViewSet(viewsets.ModelViewSet):
    # queryset = User.objects.all()
    serializer_class = AccountSerializer

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        if not pk:
            return Account.objects.all()

        return Account.objects.filter(pk=pk)

    def _get_user(self, user_id):
        """
        Private method to retrieve a user by their primary key.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    @action(methods=["get"], detail=True)
    def get_user_blnc(self, request, pk=None):
        user_id = int(pk)
        user = self._get_user(user_id)

        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        currency_param = request.query_params.get("currency", "RUB")
        allowed_currencies = ["RUB", "USD"]

        if currency_param not in allowed_currencies:
            return Response(
                {"error": "Invalid currency"}, status=status.HTTP_400_BAD_REQUEST
            )

        usd_resp, _ = get_exchange_rates()

        if currency_param == "RUB":
            serializer = AccountSerializer(user.account)
        elif currency_param == "USD":
            try:
                converted_balance = decimal.Decimal(
                    user.account.amount
                    / decimal.Decimal(usd_resp["curs"]).quantize(
                        decimal.Decimal(".0001"), rounding=ROUND_HALF_UP
                    )
                )
            except (KeyError, ValueError):
                return Response(
                    {"error": "Error converting currency"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            converted_data = {
                "user": user.get_full_name(),
                "currency": currency_param,
                "converted_balance": converted_balance,
            }
            serializer = ConvertedBalanceSerializer(data=converted_data)

            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def _check_balance_and_increase_or_decrease(
        self, amount=None, user_1=None, user_2=None
    ):

        if user_1 and user_2:
            if user_1.account.amount >= decimal.Decimal(amount):
                user_1.account.amount -= decimal.Decimal(amount)
                user_2.account.amount += decimal.Decimal(amount)
                user_1.account.save()
                user_2.account.save()
            else:
                raise InsufficientFundsException(
                    detail=f"Недостаточно средств у {user_1.get_full_name()}"
                )

        elif user_1:
            if user_1.account.amount >= decimal.Decimal(amount):
                user_1.account.amount -= decimal.Decimal(amount)
                user_1.account.save()
                return user_1
            else:
                raise InsufficientFundsException(
                    detail=f"Недостаточно средств у {user_1.get_full_name()}"
                )

    # top up method
    @action(methods=["put"], detail=True)
    def increase(self, request, pk=None):
        user_id = int(pk)
        amount = request.data.get("amount")

        user = self._get_user(user_id)
        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        balance = user.account
        balance.amount += decimal.Decimal(amount)
        balance.save()

        transaction = Transaction.objects.create(
            currency="RUB",
            sender=user,
            amount=amount,
            transaction_type=Transaction.DEPOSIT,
        )
        serializer = TransactionSerializer(transaction)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # expense method
    @action(methods=["put"], detail=True)
    def decrease(self, request, pk=None):
        user_id = int(pk)
        amount = request.data.get("amount")

        user = self._get_user(user_id)

        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        self._check_balance_and_increase_or_decrease(user_1=user, amount=amount)

        transaction = Transaction.objects.create(
            currency="RUB",
            sender=user,
            amount=amount,
            transaction_type=Transaction.WITHDRAWAL,
        )
        serializer = TransactionSerializer(transaction)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False)
    def p2p(self, request):
        sender_id = request.data.get("sender_id")
        receiver_id = request.data.get("receiver_id")
        amount = request.data.get("amount")

        sender = self._get_user(sender_id)
        receiver = self._get_user(receiver_id)

        if not sender or not receiver:
            if not sender:
                return Response(
                    {"error": "sender not found"}, status=status.HTTP_404_NOT_FOUND
                )
            return Response(
                {"error": "receiver not found"}, status=status.HTTP_404_NOT_FOUND
            )

        self._check_balance_and_increase_or_decrease(
            user_1=sender, user_2=receiver, amount=amount
        )

        transaction = Transaction.objects.create(
            currency="RUB",
            sender=sender,
            receiver=receiver,
            amount=amount,
            transaction_type=Transaction.SEND,
        )
        serializer = TransactionSerializer(transaction)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def list_user_transactions(self, request, pk):
        user = self._get_user(int(pk))
        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        user_transactions = Transaction.objects.filter(sender=user)
        filter_param = request.query_params.get(
            "param"
        )  # Получение параметра из query parameters

        if filter_param:
            user_transactions = user_transactions.order_by(str(filter_param))
            page = self.paginate_queryset(user_transactions)  # Пагинация результатов
            if page is not None:
                serializer = TransactionSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(user_transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
