import unittest
import os
import sys
import time
import requests
import json
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://localhost:8000"

def parse_sse(response_text: str) -> str:
    content = ""
    for line in response_text.splitlines():
        line = line.strip()
        if line.startswith("data: ") and not line.startswith("data: [DONE]"):
            try:
                data = json.loads(line[6:])
                content += data.get("content", "")
            except Exception:
                pass
    return content

class FullPlatformVerification(unittest.TestCase):
    """
    Comprehensive functional, security, and multi-tenant test suite.
    """

    def setUp(self):
        self.admin_user = "admin"
        self.admin_pass = "ChangeMe!123"
        self.token = None

    def get_admin_token(self):
        if self.token:
            return self.token
        res = requests.post(f"{BASE_URL}/admin/auth/login", json={"username": self.admin_user, "password": self.admin_pass})
        self.assertEqual(res.status_code, 200, f"Login failed: {res.text}")
        data = res.json()
        self.assertIn("token", data)
        self.token = data["token"]
        return self.token

    # ---------------- 1. Health & Server Status ----------------
    def test_01_health_check(self):
        res = requests.get(f"{BASE_URL}/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "ok")

    # ---------------- 2. Security: Authentication & Access Control ----------------
    def test_02_auth_protection(self):
        # Protected endpoint without token must return 401
        res = requests.get(f"{BASE_URL}/admin/projects")
        self.assertEqual(res.status_code, 401, "Protected endpoint allowed access without token!")

        # Invalid password must fail
        bad_res = requests.post(f"{BASE_URL}/admin/auth/login", json={"username": self.admin_user, "password": "WrongPassword999!"})
        self.assertIn(bad_res.status_code, [400, 401])

        # Valid token grants access
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        valid_res = requests.get(f"{BASE_URL}/admin/projects", headers=headers)
        self.assertEqual(valid_res.status_code, 200)
        projects = valid_res.json()
        self.assertTrue(isinstance(projects, list))

    # ---------------- 3. Security: Path Traversal Tests ----------------
    def test_03_path_traversal_resistance(self):
        bad_paths = [
            "/static/../../core/config.py",
            "/static/..%2f..%2fcore%2fconfig.py",
            "/static/..\\..\\core\\config.py",
            "/static/../../.env",
        ]
        for path in bad_paths:
            res = requests.get(f"{BASE_URL}{path}")
            self.assertIn(res.status_code, [400, 404, 403], f"Possible path traversal vulnerability on {path}: {res.status_code}")

    # ---------------- 4. Security: SQL Injection Resistance ----------------
    def test_04_sql_injection_resistance(self):
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        sql_payloads = [
            "' OR '1'='1",
            "general-policy'; DROP TABLE projects; --",
            "1 UNION SELECT null, username, password_hash FROM admin_users --"
        ]
        for payload in sql_payloads:
            res = requests.get(f"{BASE_URL}/admin/projects/{payload}/documents", headers=headers)
            self.assertIn(res.status_code, [404, 422, 200])
            if res.status_code == 200:
                self.assertEqual(len(res.json()), 0, "SQL injection returned data unexpectedly!")

    # ---------------- 5. Multi-Tenant Project Creation & Project Control ----------------
    def test_05_project_management(self):
        token = self.get_admin_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test creating a new project
        proj_name = f"Test Project {int(time.time())}"
        create_res = requests.post(f"{BASE_URL}/admin/projects", headers=headers, json={
            "name": proj_name,
            "description": "Verification project for multi-tenancy"
        })
        self.assertEqual(create_res.status_code, 200)
        slug = create_res.json()["slug"]

        # Verify project is listed
        list_res = requests.get(f"{BASE_URL}/admin/projects", headers=headers)
        self.assertEqual(list_res.status_code, 200)
        slugs = [p["slug"] for p in list_res.json()]
        self.assertIn(slug, slugs)

        # Test project enable/disable switch
        patch_res = requests.patch(f"{BASE_URL}/admin/projects/{slug}", headers=headers, json={"status": "disabled"})
        self.assertEqual(patch_res.status_code, 200)

        # Disabled project must return 403 on chat
        chat_res = requests.post(
            f"{BASE_URL}/api/{slug}/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Hello"}]}
        )
        self.assertEqual(chat_res.status_code, 403)

        # Re-enable project
        patch_res2 = requests.patch(f"{BASE_URL}/admin/projects/{slug}", headers=headers, json={"status": "active"})
        self.assertEqual(patch_res2.status_code, 200)

    # ---------------- 6. Grounded RAG Accuracy & Refusal on general-policy ----------------
    def test_06_grounded_rag_accuracy_and_refusal(self):
        # 6a. Factual query grounded in sample_acme_policy.pdf (Broadband reimbursement)
        res_fact = requests.post(
            f"{BASE_URL}/api/general-policy/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": "How much is the monthly broadband stipend and how is it reimbursed?"}],
                "stream": True
            }
        )
        self.assertEqual(res_fact.status_code, 200)
        reply_fact = parse_sse(res_fact.text)
        print(f"\n[RAG Test Fact Response]: {reply_fact}")
        self.assertTrue("payroll" in reply_fact.lower() or "broadband" in reply_fact.lower() or "stipend" in reply_fact.lower(), f"Expected factual policy terms in answer, got: {reply_fact}")

        # 6b. Out-of-scope query that must trigger grounded refusal
        res_refuse = requests.post(
            f"{BASE_URL}/api/general-policy/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": "What is the secret recipe for grandmother's apple pie?"}],
                "stream": True
            }
        )
        self.assertEqual(res_refuse.status_code, 200)
        reply_refuse = parse_sse(res_refuse.text)
        print(f"\n[RAG Test Refusal Response]: {reply_refuse}")
        self.assertTrue(
            "don't have information" in reply_refuse.lower() or "support@example.com" in reply_refuse.lower(),
            f"Expected refusal for out-of-scope question, but got: {reply_refuse}"
        )

if __name__ == "__main__":
    unittest.main()
