import unittest
from app import create_app
from unittest.mock import patch

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'DEBUG': True
        })
        self.client = self.app.test_client()

    @patch('vocab.translate_and_define')
    def test_add_word(self, mocked_translate_and_define):
        mocked_translate_and_define.return_value = '{"translation": "apple", "definition": "a fruit", "example": "I like apple"}'
        response = self.client.post('/en/add_word', json={"word": "apple"})
        self.assertEqual(response.status_code, 200)

    # def test_get_all_words(self):
    #     response = self.client.get('words')
    #     self.assertEqual(response.status_code, 200)
    #     print(response.data)

if __name__ == '__main__':
    unittest.main()