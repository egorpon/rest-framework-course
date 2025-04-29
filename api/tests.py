from django.urls import reverse
from api.models import User, Product
from rest_framework.test import APITestCase
from rest_framework import status


class ProductAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", password="admin"
        )
        self.normal_user = User.objects.create_user(username="user", password="user")
        self.product = Product.objects.create(
            name="Guitar", description="TEST description", price=12.99, stock=10
        )
        self.url = reverse("product-detail", kwargs={"product_id": self.product.pk})

    def test_get_product(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.product.name)

    def test_unauthorized_update_product(self):
        data = {"name": "Updated Product"}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_delete_product(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_admins_can_delete_product(self):
        # normal user cannot delete
        self.client.login(username="user", password="user")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())
        # admin can delete
        self.client.login(username="admin", password="admin")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())
