import re
import unittest

from src.router import APIRouter


class Router(unittest.TestCase):

    def test_router_paths(self) -> None:
        app = APIRouter()
        self.assertEqual(app.clear_path('/api////v1'), '/api/v1/')
        self.assertEqual(app.path_to_regex(
            '/api/{id}/'), re.compile(r"^\/api\/([^\/]+)\/$"))

    def test_router_duplicate_endpoints(self) -> None:
        app = APIRouter()
        try:
            @app.get('/real-estates')
            def func_a():
                pass

            @app.get('/real-estates/')
            def func_b():
                pass
        except Exception:
            pass
        except:
            self.fail("Router generated an unexpected error")
        else:
            self.fail("Router allows to create duplicate paths")
