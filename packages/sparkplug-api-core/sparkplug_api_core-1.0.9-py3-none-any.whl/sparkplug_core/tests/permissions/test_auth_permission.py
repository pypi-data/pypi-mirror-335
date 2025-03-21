# python
from unittest.mock import Mock, patch

# django
from django.contrib.auth.models import User
from django.test import TestCase

# contrib
from rest_framework.request import Request
from rest_framework.views import APIView

# app
from ...permissions.auth import AuthPermission


class TestAuthPermission(TestCase):

    def setUp(self):
        self.user = Mock(spec=User)
        self.request = Mock(spec=Request)
        self.view = Mock(spec=APIView)
        self.permission = AuthPermission()

    @patch("apps.slack_archive.permissions.list.test_rule")
    def test_has_permission_authenticated(self, mock_test_rule):
        mock_test_rule.return_value = True
        self.request.user = self.user

        result = self.permission.has_permission(self.request, self.view)

        mock_test_rule.assert_called_once_with("is_authenticated", self.user)
        assert result is True

    @patch("apps.slack_archive.permissions.list.test_rule")
    def test_has_permission_not_authenticated(self, mock_test_rule):
        mock_test_rule.return_value = False
        self.request.user = self.user

        result = self.permission.has_permission(self.request, self.view)

        mock_test_rule.assert_called_once_with("is_authenticated", self.user)
        assert result is False
