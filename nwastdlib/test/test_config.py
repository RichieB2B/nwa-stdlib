import os
import unittest

from nwastdlib import Either, get_config


class TestConfig(unittest.TestCase):
    def setUp(self):
        os.environ.clear()

    def test_get_config_with_env(self):
        os.environ.setdefault("test", "test_value")
        config = get_config("test", secret="ignored_because_of_env_setting")
        self.assertEqual(config, Either.Right("test_value"))

    def test_get_config_with_default(self):
        config = get_config("test", default=1, secret="ignored_because_of_env_setting")
        self.assertEqual(config, Either.Right(1))

    def test_get_config_with_parse(self):
        os.environ.setdefault("test", "1")
        config = get_config("test", parse=int, secret="ignored_because_of_env_setting")
        self.assertEqual(config, Either.Right(1))

    def test_get_config_with_secret(self):
        loc = "/tmp/secret"
        if not os.path.isfile(loc):
            new_file = open(loc, "w")
            new_file.write("test_value")
            new_file.close()

        config = get_config("test", secret="secret", secret_base_location="/tmp")
        self.assertEqual(config, Either.Right("test_value"))
