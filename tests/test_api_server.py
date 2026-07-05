from unittest import TestCase

from app.api import server


class ApiServerTest(TestCase):
    def test_public_directory_is_available(self) -> None:
        self.assertTrue((server._public_dir() / "index.html").exists())

    def test_public_mount_keeps_api_routes_available(self) -> None:
        if server.FastAPI is None:
            self.skipTest("FastAPI is not installed")

        app = server.create_app()
        paths = [getattr(route, "path", None) for route in app.routes]

        self.assertIn("/api/health", paths)
        self.assertIn("", paths)
