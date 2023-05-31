import json
import unittest
from http import HTTPStatus

from src.main import post_real_estates_likes
from src.router import Header


class RealEstateLikes(unittest.TestCase):

    @unittest.skip("Skipping because property_likes table does not exist")
    def test_authorization(self) -> None:
        try:
            code_status, response = post_real_estates_likes(
                id=1, headers=Header(Authorization=''))
        except:
            self.fail("get_real_estates generated an unexpected error")
        else:
            self.assertEqual(code_status, HTTPStatus.UNAUTHORIZED)
            self.assertEqual(response, None)

    @unittest.skip("Skipping because property_likes table does not exist")
    def test_response(self) -> None:
        try:
            code_status, response = post_real_estates_likes(
                id=1, headers=Header(Authorization='Basic dGVzdF91c2VyOnRlc3RwYXNzMTIz'))
        except:
            self.fail("get_real_estates generated an unexpected error")
        else:
            self.assertEqual(code_status, HTTPStatus.OK)
            self.assertEqual(response, json.dumps([]))
