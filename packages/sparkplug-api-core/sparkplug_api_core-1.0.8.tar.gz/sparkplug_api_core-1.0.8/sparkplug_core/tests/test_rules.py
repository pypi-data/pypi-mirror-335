# python
from unittest.mock import Mock

# django
from django.test import TestCase
from django.contrib.auth import get_user_model

# app
from ..rules import is_authenticated

User = get_user_model()


class TestRules(TestCase):

    def setUp(self):
        self.user = Mock(spec=User)
        self.community_uuid = "some-uuid"

    def test_is_authenticated_true(self):
        self.user.is_authenticated = True
        self.user.is_active = True
        assert is_authenticated(self.user)

    def test_is_authenticated_false_not_authenticated(self):
        self.user.is_authenticated = False
        self.user.is_active = True
        assert not is_authenticated(self.user)

    def test_is_authenticated_false_not_active(self):
        self.user.is_authenticated = True
        self.user.is_active = False
        assert not is_authenticated(self.user)
