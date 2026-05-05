import importlib
import os
import socket
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

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

    def test_membership_redeem_export_and_pin_limit(self):
        username = "member_user"
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

        profile = requests.get(f"{self.base_url}/user/info/{user_id}", headers=headers, timeout=5)
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.json()["vip_active"], False)
        self.assertEqual(profile.json()["pin_limit"], 3)

        conv_ids = []
        for _ in range(4):
            create_conv = requests.post(f"{self.base_url}/conversation/create/{user_id}", headers=headers, timeout=5)
            self.assertEqual(create_conv.status_code, 200)
            conv_ids.append(create_conv.json()["conversation_id"])

        for conv_id in conv_ids[:3]:
            pin_resp = requests.put(f"{self.base_url}/conversation/pin/{conv_id}", headers=headers, timeout=5)
            self.assertEqual(pin_resp.status_code, 200)
            self.assertEqual(pin_resp.json()["code"], 200)

        fourth_pin = requests.put(f"{self.base_url}/conversation/pin/{conv_ids[3]}", headers=headers, timeout=5)
        self.assertEqual(fourth_pin.status_code, 200)
        self.assertEqual(fourth_pin.json()["code"], 400)

        free_export = requests.get(f"{self.base_url}/history/export/{user_id}", headers=headers, timeout=5)
        self.assertEqual(free_export.status_code, 200)
        self.assertEqual(free_export.json()["code"], 403)

        redeem = requests.post(
            f"{self.base_url}/membership/redeem/{user_id}",
            headers=headers,
            json={"code": "DEMO30"},
            timeout=5,
        )
        self.assertEqual(redeem.status_code, 200)
        self.assertEqual(redeem.json()["code"], 200)
        self.assertEqual(redeem.json()["vip_active"], True)

        used_code = requests.post(
            f"{self.base_url}/membership/redeem/{user_id}",
            headers=headers,
            json={"code": "DEMO30"},
            timeout=5,
        )
        self.assertEqual(used_code.status_code, 200)
        self.assertEqual(used_code.json()["code"], 400)

        fourth_pin_after_vip = requests.put(f"{self.base_url}/conversation/pin/{conv_ids[3]}", headers=headers, timeout=5)
        self.assertEqual(fourth_pin_after_vip.status_code, 200)
        self.assertEqual(fourth_pin_after_vip.json()["code"], 200)

        vip_export = requests.get(f"{self.base_url}/history/export/{user_id}", headers=headers, timeout=5)
        self.assertEqual(vip_export.status_code, 200)
        self.assertEqual(vip_export.json()["code"], 200)
        self.assertEqual(vip_export.json()["conversation_count"], 4)


class GooglePlayUnitTest(unittest.TestCase):
    def test_google_play_subscription_sync_updates_membership(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = str(Path(temp_dir) / "google-play.db")
            env_overrides = {
                "DB_PATH": db_path,
                "GOOGLE_PLAY_PACKAGE_NAME": "com.example.genie",
                "GOOGLE_PLAY_SERVICE_ACCOUNT_FILE": "/tmp/fake-google-play.json",
                "GOOGLE_PLAY_SUBSCRIPTION_MAP": '{"genie.monthly":{"level":1,"label":"Google Play 月度会员"}}',
            }
            with mock.patch.dict(os.environ, env_overrides, clear=False):
                import backend.main as backend_main

                backend_main = importlib.reload(backend_main)
                conn = backend_main.get_db()
                conn.execute(
                    "INSERT INTO users (username, password, balance, invite_code, created_at) VALUES (?, ?, ?, ?, ?)",
                    ("gp_user", backend_main.hash_password("secret123"), 150, "GPTEST", backend_main.now_str()),
                )
                user_id = int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])
                conn.commit()
                conn.close()

                active_payload = {
                    "subscriptionState": "SUBSCRIPTION_STATE_ACTIVE",
                    "acknowledgementState": "ACKNOWLEDGEMENT_STATE_PENDING",
                    "latestOrderId": "GPA.1234-5678-9012-34567",
                    "startTime": "2026-05-04T12:00:00Z",
                    "lineItems": [
                        {
                            "productId": "genie.monthly",
                            "expiryTime": "2099-06-04T12:00:00Z",
                            "offerDetails": {"basePlanId": "monthly001"},
                            "autoRenewingPlan": {"autoRenewEnabled": True},
                        }
                    ],
                }

                with mock.patch.object(backend_main, "google_play_fetch_subscription_purchase", return_value=active_payload), \
                     mock.patch.object(backend_main, "google_play_acknowledge_subscription") as ack_mock:
                    result = backend_main.sync_google_subscription_purchase(
                        user_id=user_id,
                        purchase_token="token-123",
                        product_id_hint="genie.monthly",
                        source="google_play_verify",
                    )

                self.assertEqual(result["product_id"], "genie.monthly")
                self.assertTrue(result["membership"]["vip_active"])
                ack_mock.assert_called_once()

                conn = backend_main.get_db()
                stored = conn.execute(
                    "SELECT product_id, subscription_state, acknowledgement_state FROM google_play_subscriptions WHERE purchase_token = ?",
                    ("token-123",),
                ).fetchone()
                conn.close()
                self.assertIsNotNone(stored)
                self.assertEqual(stored["product_id"], "genie.monthly")
                self.assertEqual(stored["subscription_state"], "SUBSCRIPTION_STATE_ACTIVE")
                self.assertEqual(stored["acknowledgement_state"], "ACKNOWLEDGEMENT_STATE_ACKNOWLEDGED")

                expired_payload = {
                    "subscriptionState": "SUBSCRIPTION_STATE_EXPIRED",
                    "acknowledgementState": "ACKNOWLEDGEMENT_STATE_ACKNOWLEDGED",
                    "latestOrderId": "GPA.1234-5678-9012-34567",
                    "startTime": "2026-05-04T12:00:00Z",
                    "lineItems": [
                        {
                            "productId": "genie.monthly",
                            "expiryTime": "2026-05-05T12:00:00Z",
                            "offerDetails": {"basePlanId": "monthly001"},
                            "autoRenewingPlan": {"autoRenewEnabled": False},
                        }
                    ],
                }

                with mock.patch.object(backend_main, "google_play_fetch_subscription_purchase", return_value=expired_payload), \
                     mock.patch.object(backend_main, "google_play_acknowledge_subscription"):
                    result = backend_main.sync_google_subscription_purchase(
                        user_id=user_id,
                        purchase_token="token-123",
                        product_id_hint="genie.monthly",
                        source="google_play_sync",
                    )

                self.assertFalse(result["membership"]["vip_active"])


if __name__ == "__main__":
    unittest.main()
