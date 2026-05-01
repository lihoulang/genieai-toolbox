import os
import socket
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
PYTHON_BIN = BACKEND_DIR / "venv" / "bin" / "python"


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class BackendSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.port = get_free_port()
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        env = os.environ.copy()
        env["DB_PATH"] = str(Path(cls.temp_dir.name) / "smoke.db")
        cls.server = subprocess.Popen(
            [str(PYTHON_BIN), "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(cls.port)],
            cwd=str(BACKEND_DIR),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        cls._wait_until_ready()

    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        try:
            cls.server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cls.server.kill()
        cls.temp_dir.cleanup()

    @classmethod
    def _wait_until_ready(cls):
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                response = requests.get(f"{cls.base_url}/docs", timeout=1)
                if response.status_code == 200:
                    return
            except requests.RequestException:
                time.sleep(0.2)
        raise RuntimeError("Server did not become ready in time")

    def test_auth_conversation_and_account_deletion_flow(self):
        username = "smoke_user"
        password = "secret123"

        register = requests.post(
            f"{self.base_url}/register",
            json={"username": username, "password": password},
            timeout=5,
        )
        self.assertEqual(register.status_code, 200)
        self.assertEqual(register.json()["code"], 200)

        login = requests.post(
            f"{self.base_url}/login",
            json={"username": username, "password": password},
            timeout=5,
        )
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.json()["code"], 200)

        user_id = login.json()["user_id"]
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        unauthorized = requests.get(f"{self.base_url}/user/info/{user_id}", timeout=5)
        self.assertEqual(unauthorized.status_code, 401)

        profile = requests.get(f"{self.base_url}/user/info/{user_id}", headers=headers, timeout=5)
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.json()["code"], 200)

        create_conv = requests.post(f"{self.base_url}/conversation/create/{user_id}", headers=headers, timeout=5)
        self.assertEqual(create_conv.status_code, 200)
        conv_id = create_conv.json()["conversation_id"]

        conversations = requests.get(f"{self.base_url}/conversations/{user_id}", headers=headers, timeout=5)
        self.assertEqual(conversations.status_code, 200)
        self.assertEqual(len(conversations.json()["data"]), 1)
        self.assertEqual(conversations.json()["data"][0]["id"], conv_id)

        report = requests.post(
            f"{self.base_url}/ai/report",
            headers=headers,
            json={
                "user_id": user_id,
                "conversation_id": conv_id,
                "reason": "事实错误/误导",
                "message_content": "测试举报内容",
            },
            timeout=5,
        )
        self.assertEqual(report.status_code, 200)
        self.assertEqual(report.json()["code"], 200)

        delete_account = requests.delete(
            f"{self.base_url}/user/account/{user_id}",
            headers=headers,
            timeout=5,
        )
        self.assertEqual(delete_account.status_code, 200)
        self.assertEqual(delete_account.json()["code"], 200)

        relogin = requests.post(
            f"{self.base_url}/login",
            json={"username": username, "password": password},
            timeout=5,
        )
        self.assertEqual(relogin.status_code, 200)
        self.assertEqual(relogin.json()["code"], 401)


if __name__ == "__main__":
    unittest.main()
