"""Test for auth API"""
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

TOKEN_URL = reverse("auth:token")


def create_user(**params):
    """Create and return a new user"""
    user = get_user_model().objects.create_user(**params)
    return user


class PublicUserApiTest(TestCase):
    """Test the public features of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_token_for_users(self):
        """Test generates token for valid credentials."""
        user_details = {
            "email": "test@example.com",
            "password": "test-user-password123",
            "name": "Test",
        }
        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        user_details = {
            "email": "test@example.com",
            "password": "goodpass",
            "name": "Test",
        }
        create_user(**user_details)

        payload = {
            "email": "test@example.com",
            "password": "badpass",
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", res.data)
        self.assertNotIn("refresh", res.data)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        payload = {"email": "test@example.com", "password": ""}
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("access", res.data)
        self.assertNotIn("refresh", res.data)
