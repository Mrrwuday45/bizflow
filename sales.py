"""
Sales & POS Module for Bizflow AI CRM (Per-User Isolated)
"""
from models import create_sale, get_all_sales, get_sale_details

class SalesManager:
    @staticmethod
    def process_sale(user_id, customer_id, items, discount=0.0):
        """
        Processes a transaction for the logged in user and returns sale_id.
        """
        if not customer_id:
            raise ValueError("A customer must be selected for the sale.")
        if not items or len(items) == 0:
            raise ValueError("At least one product item is required for a sale.")
            
        sale_id = create_sale(user_id, customer_id, items, discount)
        return sale_id

    @staticmethod
    def list_sales(user_id):
        return get_all_sales(user_id)

    @staticmethod
    def get_sale_info(sale_id, user_id):
        return get_sale_details(sale_id, user_id)
