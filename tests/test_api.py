from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import ItemCategory
from items.models import EWasteItem
from suppliers.models import Supplier
from transactions.models import Transaction


class EWasteAPITestCase(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        self.admin = self.User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            role="admin",
            is_staff=True,
        )
        self.collector = self.User.objects.create_user(
            username="collector",
            email="collector@example.com",
            password="collectorpass123",
            role="collector",
        )
        self.category = ItemCategory.objects.create(name="Circuits", base_price_per_kg=5000)
        self.supplier = Supplier.objects.create(supplier_name="Supplier One")

    def authenticate(self, username, password):
        response = self.client.post(
            reverse("login"), {"username": username, "password": password}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data.get("access")
        self.assertIsNotNone(token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_register_and_login_flow(self):
        register_payload = {
            "username": "newcollector",
            "email": "newcollector@example.com",
            "password": "testpass123",
        }
        register_response = self.client.post(reverse("register"), register_payload, format="json")
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(register_response.data["username"], register_payload["username"])
        login_response = self.client.post(
            reverse("login"),
            {"username": register_payload["username"], "password": register_payload["password"]},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)

    def test_category_creation_requires_admin(self):
        self.authenticate("admin", "adminpass123")
        response = self.client.post(
            "/categories/",
            {"name": "Boards", "base_price_per_kg": "6000.00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_price_computation_for_conditions(self):
        weight_value = Decimal("2.5")
        item_poor = EWasteItem.objects.create(
            category=self.category,
            weight_kg=weight_value,
            condition=EWasteItem.ConditionChoices.POOR,
            date_collected=date.today(),
            created_by=self.collector,
        )
        item_fair = EWasteItem.objects.create(
            category=self.category,
            weight_kg=weight_value,
            condition=EWasteItem.ConditionChoices.FAIR,
            date_collected=date.today(),
            created_by=self.collector,
        )
        item_good = EWasteItem.objects.create(
            category=self.category,
            weight_kg=weight_value,
            condition=EWasteItem.ConditionChoices.GOOD,
            date_collected=date.today(),
            created_by=self.collector,
        )
        base_price = self.category.base_price_per_kg
        self.assertGreater(item_good.estimated_value, item_poor.estimated_value)
        self.assertEqual(
            float(item_poor.estimated_value),
            float(base_price * weight_value * EWasteItem.CONDITION_MULTIPLIERS[EWasteItem.ConditionChoices.POOR]),
        )
        self.assertEqual(
            float(item_fair.estimated_value),
            float(base_price * weight_value * EWasteItem.CONDITION_MULTIPLIERS[EWasteItem.ConditionChoices.FAIR]),
        )
        self.assertEqual(
            float(item_good.estimated_value),
            float(base_price * weight_value * EWasteItem.CONDITION_MULTIPLIERS[EWasteItem.ConditionChoices.GOOD]),
        )

    def test_item_permissions_for_collector(self):
        self.authenticate("collector", "collectorpass123")
        EWasteItem.objects.create(
            category=self.category,
            weight_kg="5",
            condition=EWasteItem.ConditionChoices.GOOD,
            date_collected=date.today(),
            created_by=self.admin,
        )
        EWasteItem.objects.create(
            category=self.category,
            weight_kg="3",
            condition=EWasteItem.ConditionChoices.FAIR,
            date_collected=date.today(),
            created_by=self.collector,
        )
        response = self.client.get("/items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_view_all_items(self):
        EWasteItem.objects.create(
            category=self.category,
            weight_kg="5",
            condition=EWasteItem.ConditionChoices.GOOD,
            date_collected=date.today(),
            created_by=self.admin,
        )
        EWasteItem.objects.create(
            category=self.category,
            weight_kg="3",
            condition=EWasteItem.ConditionChoices.FAIR,
            date_collected=date.today(),
            created_by=self.collector,
        )
        self.authenticate("admin", "adminpass123")
        response = self.client.get("/items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_supplier_item_transaction_flow(self):
        self.authenticate("collector", "collectorpass123")
        supplier_response = self.client.post(
            "/suppliers/",
            {"supplier_name": "Local Supplier", "contact": "0700-111-222", "location": "Nairobi"},
            format="json",
        )
        self.assertEqual(supplier_response.status_code, status.HTTP_201_CREATED)
        supplier_id = supplier_response.data["id"]
        item_response = self.client.post(
            "/items/",
            {
                "category": self.category.id,
                "weight_kg": "4.5",
                "condition": "good",
                "source_supplier": supplier_id,
                "date_collected": date.today().isoformat(),
            },
            format="json",
        )
        self.assertEqual(item_response.status_code, status.HTTP_201_CREATED)
        self.assertIn("estimated_value", item_response.data)
        item_id = item_response.data["id"]
        transaction_response = self.client.post(
            "/transactions/",
            {
                "ewaste_item": item_id,
                "sale_price": "20000",
                "buyer_name": "Buyer A",
                "status": "stocked",
            },
            format="json",
        )
        self.assertEqual(transaction_response.status_code, status.HTTP_201_CREATED)
        transaction_id = transaction_response.data["id"]
        update_response = self.client.patch(
            f"/transactions/{transaction_id}/",
            {"status": "sold", "date_sold": date.today().isoformat()},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["status"], "sold")

    def test_analytics_endpoints(self):
        EWasteItem.objects.create(
            category=self.category,
            weight_kg="5",
            condition=EWasteItem.ConditionChoices.GOOD,
            date_collected=date.today(),
            created_by=self.collector,
        )
        self.authenticate("admin", "adminpass123")
        today_response = self.client.get(reverse("analytics-today"))
        self.assertEqual(today_response.status_code, status.HTTP_200_OK)
        self.assertIn("total_estimated_value", today_response.data)
        monthly_response = self.client.get(reverse("analytics-monthly"))
        self.assertEqual(monthly_response.status_code, status.HTTP_200_OK)
        self.assertIn("monthly", monthly_response.data)
        supplier_response = self.client.get(reverse("analytics-suppliers"))
        self.assertEqual(supplier_response.status_code, status.HTTP_200_OK)
        self.assertIn("ranking", supplier_response.data)
