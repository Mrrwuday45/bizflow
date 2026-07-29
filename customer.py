"""
Customer Management Module for Bizflow AI CRM (Per-User Isolated)
"""
from models import (
    get_all_customers, get_customer_by_id, add_customer, 
    update_customer, delete_customer, search_customers
)

class CustomerManager:
    @staticmethod
    def list_customers(user_id):
        return get_all_customers(user_id)

    @staticmethod
    def get_customer(customer_id, user_id):
        return get_customer_by_id(customer_id, user_id)

    @staticmethod
    def create_customer(user_id, name, phone, email="", address=""):
        if not name or not phone:
            raise ValueError("Customer Name and Phone number are required.")
        return add_customer(user_id, name, phone, email, address)

    @staticmethod
    def edit_customer(customer_id, user_id, name, phone, email="", address=""):
        if not name or not phone:
            raise ValueError("Customer Name and Phone number are required.")
        update_customer(customer_id, user_id, name, phone, email, address)

    @staticmethod
    def remove_customer(customer_id, user_id):
        delete_customer(customer_id, user_id)

    @staticmethod
    def find_customers(user_id, query):
        return search_customers(user_id, query)
