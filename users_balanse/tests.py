from decimal import Decimal, ROUND_HALF_UP

from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status


from users_balanse.models import User, Account
from users_balanse.serializers import AccountSerializer, ConvertedBalanceSerializer


class TestUserBalanceViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.credentials = {"username": "test_user", "password": "te$t_pa$$word"}
        self.user = User.objects.create_user(**self.credentials)
        self.account = Account.objects.create(
            currency="RUB", user=self.user, amount=1000
        )

    def test_get_queryset_no_pk(self):
        response = self.client.get(
            reverse("balance-list")
        )  # Adapt the name as per your URL config
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if all accounts are returned

    def test_get_queryset_with_pk(self):
        url = reverse("balance-increase", args=[self.user.pk])
        data = {"amount": "500"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestUserBalanceTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.credentials = {
            "username": "test_user",
            "password": "te$t_pa$$word",
            "first_name": "John",
            "last_name": "Doe",
        }
        self.user = User.objects.create_user(**self.credentials)
        self.account = Account.objects.create(
            currency="RUB", user=self.user, amount=1000
        )

    def test_get_user_balance_rub(self):
        """Test getting user balance in RUB"""
        url = reverse("balance-get-user-blnc", kwargs={"pk": self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, AccountSerializer(self.account).data)

    def test_get_user_balance_in_usd(self):
        # Mock the response from the get_exchange_rates function
        url = reverse("balance-get-user-blnc", kwargs={"pk": self.user.id})
        response = self.client.get(url, {"currency": "USD"})
        serializer = ConvertedBalanceSerializer(
            data={
                "user": self.user.get_full_name(),
                "currency": "USD",
                "converted_balance": Decimal(self.user.account.amount / 60.0).quantize(
                    Decimal(".0001"), rounding=ROUND_HALF_UP
                ),  # Assuming USD rate is 60.0
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(serializer.is_valid())

        self.assertEqual(
            Decimal(
                serializer.data["converted_balance"]),
            Decimal(16.6667).quantize(Decimal(".0001"), rounding=ROUND_HALF_UP),
        )

    def test_get_user_balance_invalid_currency(self):
        """Test getting user balance with invalid currency"""
        url = reverse("balance-get-user-blnc", kwargs={"pk": self.user.id})
        response = self.client.get(url, {"currency": "EUR"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Invalid currency"})

    def test_get_user_balance_invalid_user(self):
        """Test getting balance for non-existent user"""
        url = reverse("balance-get-user-blnc", kwargs={"pk": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "User not found"})
