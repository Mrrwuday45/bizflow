"""
Product / Inventory Management Module for Bizflow AI CRM (Per-User Isolated)
"""
from models import (
    get_all_products, get_product_by_id, add_product,
    update_product, delete_product, get_low_stock_products
)

class ProductManager:
    @staticmethod
    def list_products(user_id):
        return get_all_products(user_id)

    @staticmethod
    def get_product(product_id, user_id):
        return get_product_by_id(product_id, user_id)

    @staticmethod
    def create_product(user_id, name, price, quantity, category="General", description=""):
        if not name:
            raise ValueError("Product name is required.")
        if price < 0 or quantity < 0:
            raise ValueError("Price and quantity must be non-negative.")
        return add_product(user_id, name, float(price), int(quantity), category, description)

    @staticmethod
    def edit_product(product_id, user_id, name, price, quantity, category="General", description=""):
        if not name:
            raise ValueError("Product name is required.")
        if price < 0 or quantity < 0:
            raise ValueError("Price and quantity must be non-negative.")
        update_product(product_id, user_id, name, float(price), int(quantity), category, description)

    @staticmethod
    def remove_product(product_id, user_id):
        delete_product(product_id, user_id)

    @staticmethod
    def low_stock_alerts(user_id, threshold=5):
        return get_low_stock_products(user_id, threshold)
