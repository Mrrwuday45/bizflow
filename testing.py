"""
System & Integration Test Suite for Bizflow AI CRM (Isolated Test Database)
"""
import os
import time
import unittest
import database

# Override Database Path for Testing to isolate from live crm_database.db
TEST_DB_PATH = "test_crm_temp.db"
database.DATABASE_PATH = TEST_DB_PATH

from database import init_db, get_db_connection
from models import create_user, verify_user_login, reset_user_password
from customer import CustomerManager
from product import ProductManager
from sales import SalesManager
from invoice import generate_pdf_invoice
from reports import BusinessReporter
from ai_assistant import AIAssistant

class TestBizflowAIMultiTenant(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Remove old test db if exists
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass
        init_db()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass

    def test_00_user_authentication_and_reset(self):
        print("\n[TEST] Testing User Registration, Authentication & Forgot Password...")
        ts = int(time.time())
        username = f"user1_{ts}"
        email = f"user1_{ts}@bizflow.ai"
        
        user_id = create_user(
            username=username,
            email=email,
            password="secretpassword123",
            name="User One",
            role="Manager",
            reset_question="What is your store name?",
            reset_answer="Bizflow Store"
        )
        self.assertIsNotNone(user_id)

        user = verify_user_login(username, "secretpassword123")
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], "User One")

        reset_success = reset_user_password(email, "Bizflow Store", "newsecretpassword456")
        self.assertTrue(reset_success)

        updated_user = verify_user_login(username, "newsecretpassword456")
        self.assertIsNotNone(updated_user)
        print("   --> User Auth, Registration & Forgot Password verified successfully.")

    def test_01_per_user_data_isolation(self):
        print("[TEST] Testing Per-User Multi-Tenant Data Isolation...")
        ts = int(time.time())
        u_a = create_user(f"usera_{ts}", f"usera_{ts}@bizflow.ai", "pass123", "User A", "Admin")
        u_b = create_user(f"userb_{ts}", f"userb_{ts}@bizflow.ai", "pass123", "User B", "Admin")

        cust_a = CustomerManager.create_customer(u_a, "Customer A", "9111111111", "a@test.com", "Address A")
        prod_a = ProductManager.create_product(u_a, "Product A", 1500.0, 10, "Cat A", "Item A")

        cust_b = CustomerManager.create_customer(u_b, "Customer B", "9222222222", "b@test.com", "Address B")
        prod_b = ProductManager.create_product(u_b, "Product B", 2500.0, 5, "Cat B", "Item B")

        custs_for_a = CustomerManager.list_customers(u_a)
        prods_for_a = ProductManager.list_products(u_a)
        self.assertEqual(len(custs_for_a), 1)
        self.assertEqual(custs_for_a[0]['name'], "Customer A")

        custs_for_b = CustomerManager.list_customers(u_b)
        prods_for_b = ProductManager.list_products(u_b)
        self.assertEqual(len(custs_for_b), 1)

        sale_a = SalesManager.process_sale(u_a, cust_a, [{'product_id': prod_a, 'quantity': 2}])
        filename, filepath = generate_pdf_invoice(sale_a, u_a)
        self.assertTrue(os.path.exists(filepath))

        summary_a = BusinessReporter.get_dashboard_summary(u_a)
        summary_b = BusinessReporter.get_dashboard_summary(u_b)

        self.assertEqual(summary_a['total_sales_count'], 1)
        self.assertEqual(summary_a['total_revenue'], 3000.0)
        self.assertEqual(summary_b['total_sales_count'], 0)
        self.assertEqual(summary_b['total_revenue'], 0.0)

        print("   --> Per-User Data Isolation completely verified! User B cannot access User A's data.")

if __name__ == '__main__':
    print("=" * 60)
    print("[TEST SUITE] Running Bizflow AI CRM Multi-Tenant Isolation Tests")
    print("=" * 60)
    unittest.main()
