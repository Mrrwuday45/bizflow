"""
Business Reporting and Analytics Module for Bizflow AI CRM (With Chart.js Datasets)
"""
from database import get_db_connection
from datetime import datetime, timedelta

class BusinessReporter:
    @staticmethod
    def get_dashboard_summary(user_id):
        conn = get_db_connection()
        
        total_customers = conn.execute("SELECT COUNT(*) FROM customers WHERE user_id = ?", (user_id,)).fetchone()[0]
        total_products = conn.execute("SELECT COUNT(*) FROM products WHERE user_id = ?", (user_id,)).fetchone()[0]
        low_stock_count = conn.execute("SELECT COUNT(*) FROM products WHERE user_id = ? AND quantity <= 5", (user_id,)).fetchone()[0]
        
        sales_stats = conn.execute("""
            SELECT COUNT(*), COALESCE(SUM(total_amount), 0.0) 
            FROM sales
            WHERE user_id = ?
        """, (user_id,)).fetchone()
        
        total_sales_count = sales_stats[0]
        total_revenue = sales_stats[1]

        # Recent 5 Sales for user
        recent_sales = conn.execute("""
            SELECT s.*, c.name as customer_name
            FROM sales s
            JOIN customers c ON s.customer_id = c.customer_id
            WHERE s.user_id = ?
            ORDER BY s.date DESC
            LIMIT 5
        """, (user_id,)).fetchall()

        # Top 5 Customers by spend for user
        top_customers = conn.execute("""
            SELECT c.customer_id, c.name, c.phone, COUNT(s.sale_id) as total_orders, COALESCE(SUM(s.total_amount), 0.0) as total_spent
            FROM customers c
            JOIN sales s ON c.customer_id = s.customer_id
            WHERE c.user_id = ? AND s.user_id = ?
            GROUP BY c.customer_id
            ORDER BY total_spent DESC
            LIMIT 5
        """, (user_id, user_id)).fetchall()

        # Top 5 Best Selling Products for user
        top_products = conn.execute("""
            SELECT p.product_name, SUM(si.quantity) as total_qty_sold, SUM(si.subtotal) as total_revenue
            FROM sale_items si
            JOIN products p ON si.product_id = p.product_id
            JOIN sales s ON si.sale_id = s.sale_id
            WHERE p.user_id = ? AND s.user_id = ?
            GROUP BY p.product_id
            ORDER BY total_qty_sold DESC
            LIMIT 5
        """, (user_id, user_id)).fetchall()

        # --- Chart.js Dataset 1: Daily Revenue Trend (Last 7 Days) ---
        chart_days = []
        chart_revenue = []
        for i in range(6, -1, -1):
            date_str = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            display_day = (datetime.now() - timedelta(days=i)).strftime('%b %d')
            day_total = conn.execute("""
                SELECT COALESCE(SUM(total_amount), 0.0)
                FROM sales
                WHERE user_id = ? AND DATE(date) = ?
            """, (user_id, date_str)).fetchone()[0]
            
            chart_days.append(display_day)
            chart_revenue.append(round(day_total, 2))

        # --- Chart.js Dataset 2: Product Sales Breakdown ---
        chart_prod_labels = [p['product_name'] for p in top_products]
        chart_prod_data = [p['total_qty_sold'] for p in top_products]

        conn.close()

        return {
            'total_customers': total_customers,
            'total_products': total_products,
            'low_stock_count': low_stock_count,
            'total_sales_count': total_sales_count,
            'total_revenue': total_revenue,
            'recent_sales': [dict(s) for s in recent_sales],
            'top_customers': [dict(c) for c in top_customers],
            'top_products': [dict(p) for p in top_products],
            'chart_days': chart_days,
            'chart_revenue': chart_revenue,
            'chart_prod_labels': chart_prod_labels,
            'chart_prod_data': chart_prod_data
        }
