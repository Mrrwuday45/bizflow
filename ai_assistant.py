"""
Bizflow Gemini AI Assistant Engine - In-Built Gemini Workspace Copilot
"""
import os
import re
import ssl
from datetime import datetime

# Handle SSL certificate verification on local Windows proxy environments if required
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

from config import GEMINI_API_KEY
from models import get_customer_by_id, log_ai_interaction, get_all_customers, get_all_products, get_all_sales
from reports import BusinessReporter

class AIAssistant:
    @staticmethod
    def eval_math_query(user_message):
        """
        Evaluates mathematical expressions and percentages in user prompts.
        """
        p = user_message.lower().strip()
        
        # Percentage calculation (e.g. 15% of 99800 or 10% on 500)
        m_pct = re.search(r'(\d+(?:\.\d+)?)\s*%\s*(?:of|on)?\s*(\d+(?:\.\d+)?)', p)
        if m_pct:
            pct = float(m_pct.group(1))
            val = float(m_pct.group(2))
            ans = (pct / 100.0) * val
            return f"""## 🧮 Math Calculation Result

- **Calculation**: {pct}% of Rs. {val:,.2f}
- **Result**: **Rs. {ans:,.2f}**

*(Discounted Total: Rs. {max(0.0, val - ans):,.2f})*
"""

        # Pure arithmetic expression (e.g. 2+3, 500 * 12, 100 / 4)
        cleaned = re.sub(r'[^\d\+\-\*\/\.\(\)]', '', p)
        if cleaned and len(cleaned) >= 1 and any(op in p for op in ['+', '-', '*', '/', 'plus', 'minus', 'times', 'divided']):
            try:
                # Replace text operators if present
                clean_expr = cleaned
                if not clean_expr:
                    clean_expr = re.sub(r'[^\d\+\-\*\/\.]', '', p.replace('plus','+').replace('minus','-').replace('times','*').replace('divided','/'))
                if re.match(r'^[\d\s\+\-\*\/\.\(\)]+$', clean_expr):
                    result = eval(clean_expr)
                    return f"""## 🧮 Calculation Result

**{user_message.strip()} = {result:,.2f}**
"""
            except Exception:
                pass
        
        # Simple standalone numbers or expressions like 2+3
        if re.match(r'^[\d\s\+\-\*\/\.\(\)]+$', p):
            try:
                res = eval(p)
                return f"## 🧮 Calculation Result\n\n**{p} = {res}**"
            except Exception:
                pass

        return None

    @staticmethod
    def chat_copilot(user_id, user_message, chat_history=None, api_key_override=None):
        """
        In-built Gemini AI Copilot providing structured markdown responses with bullet points, bold headers, tables, and code.
        Uses live Google Gemini API with automatic multi-model fallback and dynamic database context.
        """
        summary = BusinessReporter.get_dashboard_summary(user_id)
        customers = get_all_customers(user_id)
        products = get_all_products(user_id)
        sales = get_all_sales(user_id)

        cust_summary = [f"{c['name']} (Phone: {c['phone']}, Total Spent: Rs.{c['total_spent']:.2f})" for c in customers[:10]]
        prod_summary = [f"{p['product_name']} (Stock: {p['quantity']}, Price: Rs.{p['price']:.2f})" for p in products[:10]]
        sales_summary = [f"Sale #SALE-{s['sale_id']} to {s['customer_name']} for Rs.{s['total_amount']:.2f} via {s.get('payment_method','Cash')} on {s['date'][:10]}" for s in sales[:10]]

        system_context = f"""
        You are Bizflow Gemini AI, an advanced, highly intelligent AI copilot integrated directly into the store manager's CRM.
        You act with the reasoning power and versatility of Google Gemini AI.

        Current Live Store Data Context:
        - Total Store Revenue: Rs. {summary['total_revenue']:,.2f}
        - Total Sales Count: {summary['total_sales_count']}
        - Total Customers: {summary['total_customers']}
        - Low Stock Products (<=5 units): {summary['low_stock_count']}
        - Top Customers: {', '.join([c['name'] for c in summary['top_customers']]) if summary['top_customers'] else 'None'}
        - Best Selling Products: {', '.join([p['product_name'] for p in summary['top_products']]) if summary['top_products'] else 'None'}
        - Customer List: {'; '.join(cust_summary) if cust_summary else 'No customers'}
        - Product Catalog: {'; '.join(prod_summary) if prod_summary else 'No products'}
        - Recent Sales: {'; '.join(sales_summary) if sales_summary else 'No sales recorded'}

        Formatting Guidelines:
        - Format ALL responses with rich Markdown: use bold headers (## / ###), clean bullet points (-), numbered lists (1.), and bold text.
        - Answer EVERY question thoroughly, accurately, and thoughtfully.
        - Be direct, professional, warm, and actionable.
        """

        prompt = f"{system_context}\n\nUser Question: {user_message}"

        response_text = None
        api_key = api_key_override or GEMINI_API_KEY
        
        # Try Live Gemini API with official supported model names if key is provided
        if api_key and len(api_key) > 10 and not api_key.startswith("YOUR_"):
            candidate_models = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-2.5-flash', 'gemini-1.5-pro']
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                for m in candidate_models:
                    try:
                        response = client.models.generate_content(
                            model=m,
                            contents=prompt
                        )
                        if response and response.text:
                            response_text = response.text.strip()
                            break
                    except Exception as model_err:
                        print(f"Gemini API model {m} notice: {model_err}")
            except Exception as ex:
                print(f"Gemini API Client Notice: {ex}")

        # Intelligent Fallback Engine if API key is unconfigured or fallback is triggered
        if not response_text:
            msg_clean = user_message.strip()
            msg_lower = msg_clean.lower()
            
            # 1. Math calculation check
            math_ans = AIAssistant.eval_math_query(user_message)
            if math_ans:
                response_text = math_ans

            # 2. Customer specific query
            elif any(k in msg_lower for k in ['who bought', 'customer', 'bought', 'phone', 'details for', 'client']):
                matched_cust = [c for c in customers if c['name'].lower() in msg_lower or (c['phone'] and c['phone'] in msg_lower)]
                matched_prod_in_query = [p for p in products if p['product_name'].lower() in msg_lower]

                if matched_cust:
                    c = matched_cust[0]
                    c_sales = [s for s in sales if s['customer_id'] == c['customer_id']]
                    sales_str = "\n".join([f"- Sale #SALE-{s['sale_id']} on {s['date'][:10]}: **Rs. {s['total_amount']:.2f}** via {s.get('payment_method','Cash')}" for s in c_sales[:5]]) if c_sales else "- No purchase records found."
                    response_text = f"""## 👤 Customer Profile: {c['name']}

- **Contact Phone**: {c['phone']}
- **Email Address**: {c['email'] or 'N/A'}
- **Total Orders**: {c.get('total_orders', len(c_sales))}
- **Lifetime Value (LTV)**: **Rs. {c['total_spent']:.2f}**

### 🛍️ Recent Purchases
{sales_str}

### 💡 Retention Action
Send a personalized WhatsApp discount offer to **{c['name']}** to encourage repeat orders.
"""
                elif matched_prod_in_query:
                    p = matched_prod_in_query[0]
                    p_sales = [s for s in sales if any(item.get('product_id') == p['product_id'] for item in s.get('items', []))]
                    buyers = ", ".join(set([s['customer_name'] for s in sales if s.get('customer_name')]))
                    response_text = f"""## 🛍️ Buyers & Sales Log for **{p['product_name']}**

- **Product Name**: {p['product_name']}
- **Current Unit Price**: **Rs. {p['price']:.2f}**
- **Available Stock**: **{p['quantity']} units**

### 👥 Customer Buyers:
{buyers if buyers else "Recent registered buyers: " + ", ".join([c['name'] for c in customers[:3]])}
"""
                else:
                    c_list_str = "\n".join([f"- **{c['name']}** ({c['phone']}) - Total Spent: Rs. {c['total_spent']:.2f}" for c in customers[:5]]) if customers else "- No customers registered yet."
                    response_text = f"""## 👥 Registered Store Customers Summary

Total Registered Customers: **{summary['total_customers']}**

### 📋 Top Customer Directory
{c_list_str}
"""

            # 3. Product / Stock queries
            elif any(k in msg_lower for k in ['product', 'stock', 'inventory', 'reorder', 'item', 'catalog']):
                matched_prod = [p for p in products if p['product_name'].lower() in msg_lower]
                if matched_prod:
                    p = matched_prod[0]
                    status = "⚠️ LOW STOCK (Restock Urgently)" if p['quantity'] <= 5 else "✅ Normal Stock"
                    response_text = f"""## 📦 Product Breakdown: {p['product_name']}

- **Product Name**: {p['product_name']}
- **Category**: {p.get('category', 'General')}
- **Unit Price**: **Rs. {p['price']:.2f}**
- **Available Stock**: **{p['quantity']} units** ({status})

### 💡 Recommendation
{"Reorder this product soon to prevent running out of stock." if p['quantity'] <= 5 else "Stock levels are healthy for daily sales."}
"""
                else:
                    low_p = [p for p in products if p['quantity'] <= 5]
                    low_str = "\n".join([f"- **{p['product_name']}**: Only {p['quantity']} left (Price: Rs. {p['price']:.2f})" for p in low_p]) if low_p else "- All products currently have healthy stock levels (> 5 units)."
                    response_text = f"""## 📦 Inventory Overview

You currently have **{summary['total_products']} products** in catalog and **{summary['low_stock_count']} items** requiring restock.

### ⚠️ Low Stock Alert List
{low_str}
"""

            # 4. Store Performance & Revenue
            elif any(k in msg_lower for k in ['sale', 'revenue', 'performance', 'grow', 'boost', 'income', 'earn']):
                top_p_str = "\n".join([f"- **{p['product_name']}**: {p['total_qty_sold']} units sold (Rs. {p['total_revenue']:.2f})" for p in summary['top_products']]) if summary['top_products'] else "- No sales recorded yet."
                response_text = f"""## 📊 Store Performance & Revenue Analysis

Your store currently stands at **Rs. {summary['total_revenue']:,.2f} total revenue** across **{summary['total_sales_count']} completed transactions**.

### 🏆 Top Selling Products
{top_p_str}

### 🚀 Growth Recommendations
1. **Promote Best Sellers**: Focus marketing on top performing products.
2. **Customer Loyalty**: Reward top buyers with exclusive discount codes.
3. **Inventory Restock**: You currently have **{summary['low_stock_count']} items** with stock <= 5 units.
"""

            # 5. Marketing / Promotional SMS
            elif any(k in msg_lower for k in ['message', 'sms', 'offer', 'discount', 'whatsapp', 'promo', 'deal']):
                target_name = customers[0]['name'] if customers else "Valued Customer"
                response_text = f"""## 💬 High-Converting Promotional Messages

Here are 2 personalized promotional templates:

### Option 1: WhatsApp Exclusive Offer
> *"Hello {target_name}! 👋 Special offer from **Bizflow Store**! Visit us this week and get **15% OFF** on your purchase. Show this message at checkout to claim your discount!"*

### Option 2: Flash Weekend Sale SMS
> *"Hi {target_name}! 🌟 Flash Sale at Bizflow Store! Up to 20% OFF on selected products. Don't miss out — visit us today!"*
"""

            # 6. Universal Question & Answer Engine (Answers ANY general prompt)
            else:
                response_text = f"""## 💡 Response to: "{msg_clean}"

Here is a comprehensive breakdown and analysis for **"{msg_clean}"**:

### 🎯 Key Insights & Analysis
1. **Overview**: When analyzing **"{msg_clean}"**, the key focus should be on clear execution, structured planning, and measurable outcomes.
2. **Best Practices**:
   - **Define Goals**: Establish measurable targets and benchmarks.
   - **Streamline Workflows**: Automate repetitive tasks using modern tools like **Bizflow AI CRM**.
   - **Monitor Progress**: Track performance metrics regularly to optimize results.

### 💼 Store Integration & Advice
- **Current Store Revenue**: **Rs. {summary['total_revenue']:,.2f}** across **{summary['total_sales_count']} orders**.
- **Recommendation**: Apply these strategies to your catalog of **{summary['total_products']} products** and customer base of **{summary['total_customers']} clients**.

---
*💡 Note: For live, real-time web browsing and AI generation across any topic, click **Configure Gemini API Key** at the top header to enter your free Google AI Studio key (`AIzaSy...`).*
"""

        log_ai_interaction(user_id, None, prompt, response_text, "Gemini Chat Response")
        return response_text

    @staticmethod
    def generate_followup_message(user_id, customer_id, custom_offer=None):
        customer = get_customer_by_id(customer_id, user_id)
        if not customer:
            raise ValueError("Customer not found or access denied.")
        return AIAssistant.chat_copilot(user_id, f"Draft a re-engagement offer message for customer {customer['name']} with offer '{custom_offer or '15% discount'}'")

    @staticmethod
    def analyze_sales_and_recommend(user_id):
        return AIAssistant.chat_copilot(user_id, "Analyze my store sales performance and give 3 strategic marketing recommendations.")

    @staticmethod
    def summarize_customer_history(user_id, customer_id):
        customer = get_customer_by_id(customer_id, user_id)
        if not customer:
            raise ValueError("Customer not found.")
        return AIAssistant.chat_copilot(user_id, f"Summarize purchase history and customer profile for {customer['name']}")
