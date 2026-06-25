import bcrypt
import unittest
from unittest.mock import MagicMock, patch
from bson import ObjectId

from app import create_app


class TestAuthRoutes(unittest.TestCase):
    def setUp(self):
        self.users = MagicMock()
        self.db = MagicMock()
        self.db.users = self.users

        self.init_db_patcher = patch('app.init_db', return_value=self.db)
        self.get_db_patcher = patch('routes.auth.get_db', return_value=self.db)

        self.init_db_patcher.start()
        self.get_db_patcher.start()

        self.app = create_app('testing')
        self.client = self.app.test_client()

    def tearDown(self):
        patch.stopall()

    def test_signup_route_hashes_password(self):
        self.users.find_one.return_value = None
        self.users.insert_one.return_value = MagicMock(inserted_id=ObjectId())

        payload = {
            'email': 'user@example.com',
            'password': 'Password123',
            'name': 'Test User'
        }

        response = self.client.post('/api/auth/signup', json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertIn('token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], payload['email'])
        self.assertEqual(data['user']['name'], payload['name'])
        self.users.insert_one.assert_called_once()

    def test_login_route_verifies_password(self):
        password = 'Password123'
        stored_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_doc = {
            'email': 'user@example.com',
            'password': stored_hash,
            '_id': str(ObjectId()),
            'name': 'Test User'
        }

        self.users.find_one.return_value = user_doc

        payload = {
            'email': user_doc['email'],
            'password': password
        }

        response = self.client.post('/api/auth/login', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], payload['email'])

    def test_health_endpoint(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get('status'), 'ok')
        self.assertIn('message', data)
