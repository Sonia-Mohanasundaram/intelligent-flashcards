import unittest
from unittest.mock import MagicMock

import bcrypt

from models.user import User


class TestAuthHashing(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.db.users = MagicMock()

    def test_password_hashing_and_verification(self):
        email = "test@example.com"
        password = "securePassword123"
        name = "Test User"

        # Mock find_one to return None when checking existing user
        self.db.users.find_one.return_value = None
        self.db.users.insert_one.return_value.inserted_id = "mocked_id"

        user_doc = User.create(self.db, email, password, name)

        self.assertEqual(user_doc["email"], email)
        self.assertEqual(user_doc["name"], name)
        self.assertIn("password", user_doc)
        self.assertNotEqual(user_doc["password"], password)
        self.assertIsInstance(user_doc["password"], str)

        # Ensure the stored hash verifies correctly
        self.db.users.find_one.return_value = {
            "email": email,
            "password": user_doc["password"],
            "_id": "mocked_id"
        }
        self.assertTrue(User.verify_password(self.db, email, password))
        self.assertFalse(User.verify_password(self.db, email, "wrongPassword"))

    def test_change_password(self):
        user_id = "64c9f5a6f7b4d3e7bc123456"
        old_password = "securePassword123"
        new_password = "newSecurePassword456"

        stored_hash = bcrypt.hashpw(old_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        self.db.users.find_one.return_value = {
            "_id": user_id,
            "password": stored_hash
        }

        User.change_password(self.db, user_id, old_password, new_password)

        self.db.users.update_one.assert_called_once()
        updated_password = self.db.users.update_one.call_args[0][1]["$set"]["password"]
        self.assertNotEqual(updated_password, old_password)
        self.assertIsInstance(updated_password, str)
        self.assertTrue(bcrypt.checkpw(new_password.encode("utf-8"), updated_password.encode("utf-8")))


if __name__ == "__main__":
    unittest.main()
