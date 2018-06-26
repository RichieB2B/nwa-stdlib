import unittest
from unittest.mock import patch, MagicMock

from nwastdlib.oauth.oauth_filter import OAuthFilter


class TestOauthFilterWithoutApp(unittest.TestCase):
    @patch('nwastdlib.oauth.oauth_filter.flask.current_app')
    def test_get_current_user(self, current_app):
        current_app.cache = MagicMock()
        res = OAuthFilter.current_user()
        self.assertEqual(None, res)
