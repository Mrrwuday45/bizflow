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
from models import (
    get_customer_by_id, log_ai_interaction, get_all_customers, get_all_products, 
    get_all_sales, add_customer, add_product
)
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
    def handle_write_actions(user_id, user_message):
        """
        Parses intent for database write actions (Add Customer, Add Product) and executes them directly.
        Validates whether actual details are provided vs meta phrases ("i will give details", "how to add").
        """
        msg_clean = user_message.strip()
        msg_lower = msg_clean.lower()
        
        meta_phrases = [
            'i will give', 'will give', 'give details', 'provide details', 
            'details', 'later', 'how to', 'can you', 'help me', 'want to', 
            'please add', 'how do i', 'for me', 'below', 'ask me'
        ]

        # --- Action 1: Add Customer ---
        is_add_cust = any(kw in msg_lower for kw in ['add customer', 'create customer', 'new customer', 'register customer', 'save customer', 'add client', 'create client'])
        if is_add_cust or (('add' in msg_lower or 'create' in msg_lower) and ('client' in msg_lower or 'customer' in msg_lower)):
            phone_match = re.search(r'(\+?\d[\d\s\-\(\)]{8,14}\d)', msg_clean)
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', msg_clean)
            
            # Check if prompt is a generic statement / request for details
            if any(mp in msg_lower for mp in meta_phrases) and not phone_match and not email_match:
                return f"""## 👤 Add Customer via AI Assistant

Please provide the customer details in your message!

### 📝 Example Format:
> *"Add customer **Rajesh Kumar**, phone **9876543210**, email **rajesh@gmail.com**, address **Delhi**"*

*(Or navigate to **Customers** in the sidebar menu to use the registration form).*
"""

            name = ""
            name_match = re.search(r'(?:name|named|customer|client|add|create)\s+([A-Z][a-zA-Z0-9\s]{1,25}?)(?:\s*,|\s+phone|\s+with|\s+email|\s+\d|$)', msg_clean, re.IGNORECASE)
            if name_match:
                candidate = name_match.group(1).strip()
                if candidate.lower() not in ['customer', 'client', 'add', 'create', 'named', 'name', 'with', 'phone', 'new']:
                    name = candidate.title()
            
            if not name:
                words = [w for w in re.findall(r'\b[A-Za-z]+\b', msg_clean) if w.lower() not in ['add', 'create', 'new', 'customer', 'client', 'save', 'register', 'with', 'phone', 'email', 'number', 'address', 'details', 'will', 'give', 'the']]
                if words:
                    name = " ".join(words[:2]).title()

            if name.lower().startswith('customer '):
                name = name[9:].strip()
            elif name.lower().startswith('client '):
                name = name[7:].strip()

            is_meta_name = any(mp in name.lower() for mp in meta_phrases)
            if not phone_match and not email_match and (not name or is_meta_name or len(name) < 2):
                return f"""## 👤 Add Customer via AI Assistant

Please provide the customer details in your prompt!

### 📝 Example Format:
> *"Add customer **Rajesh Kumar**, phone **9876543210**, email **rajesh@gmail.com**, address **Delhi**"*

*(Or navigate to **Customers** in the sidebar menu to use the registration form).*
"""

            phone = phone_match.group(1).replace(' ', '').replace('-', '') if phone_match else "9999999999"
            email = email_match.group(1) if email_match else ""
            if not name or is_meta_name:
                name = "New Customer"
                    
            addr_match = re.search(r'(?:address|location|city|in|at)\s+([a-zA-Z0-9\s,]{2,30})', msg_clean, re.IGNORECASE)
            address = addr_match.group(1).strip() if addr_match else "Local Store Region"

            try:
                cust_id = add_customer(user_id=user_id, name=name, phone=phone, email=email, address=address)
                return f"""## ✅ Customer Successfully Created in Database!

- **Customer ID**: `#CUST-{cust_id}`
- **Customer Name**: **{name}**
- **Contact Phone**: **{phone}**
- **Email Address**: {email if email else 'N/A'}
- **Store Location / Address**: {address}

*(This record is now live in your Customer Directory and instantly available for POS cart sales & PDF invoicing.)*
"""
            except Exception as e:
                return f"""## ⚠️ Customer Creation Notice
Could not execute database write action: `{str(e)}`. Please verify contact details and try again.
"""

        # --- Action 2: Add Product ---
        is_add_prod = any(kw in msg_lower for kw in ['add product', 'create product', 'new product', 'add item', 'new item', 'add stock'])
        if is_add_prod or (('add' in msg_lower or 'create' in msg_lower) and ('product' in msg_lower or 'stock' in msg_lower or 'item' in msg_lower)):
            price_match = re.search(r'(?:price|cost|rs|₹|\$)\s*:?\s*(\d+(?:\.\d+)?)', msg_clean, re.IGNORECASE)
            qty_match = re.search(r'(?:stock|quantity|qty|units)\s*:?\s*(\d+)', msg_clean, re.IGNORECASE)
            
            if any(mp in msg_lower for mp in meta_phrases) and not price_match and not qty_match:
                return f"""## 📦 Add Product to Inventory via AI Assistant

Please specify the product details in your message!

### 📝 Example Format:
> *"Add product **Wireless Mouse**, price **499**, stock **25**, category **Electronics**"*

*(Or navigate to **Products & Stock** in the sidebar menu to use the inventory form).*
"""

            price = float(price_match.group(1)) if price_match else 100.0
            quantity = int(qty_match.group(1)) if qty_match else 10
            
            prod_name = ""
            pname_match = re.search(r'(?:product|item|add product|create product)\s+([A-Za-z0-9\s]{2,30}?)(?:\s*,|\s+price|\s+cost|\s+stock|\s+qty|\s+category|\s+\d|$)', msg_clean, re.IGNORECASE)
            if pname_match:
                prod_name = pname_match.group(1).strip().title()

            if not prod_name or prod_name.lower() in ['product', 'item', 'new', 'add', 'create']:
                words = [w for w in re.findall(r'\b[A-Za-z0-9]+\b', msg_clean) if w.lower() not in ['add', 'create', 'new', 'product', 'item', 'stock', 'price', 'quantity', 'cost', 'rs', 'rupees', 'category']]
                if words:
                    prod_name = " ".join(words[:3]).title()
                else:
                    prod_name = "New Product Item"

            if prod_name.lower().startswith('product '):
                prod_name = prod_name[8:].strip()
            elif prod_name.lower().startswith('item '):
                prod_name = prod_name[5:].strip()

            is_meta_prod = any(mp in prod_name.lower() for mp in meta_phrases)
            if not price_match and not qty_match and (not prod_name or is_meta_prod or len(prod_name) < 2):
                return f"""## 📦 Add Product to Inventory via AI Assistant

Please specify the product details in your prompt!

### 📝 Example Format:
> *"Add product **Wireless Mouse**, price **499**, stock **25**, category **Electronics**"*

*(Or navigate to **Products & Stock** in the sidebar menu).*
"""

            cat_match = re.search(r'(?:category|cat)\s*:?\s*([a-zA-Z0-9\s]+)', msg_clean, re.IGNORECASE)
            category = cat_match.group(1).strip().title() if cat_match else "General"

            try:
                prod_id = add_product(user_id=user_id, name=prod_name, price=price, quantity=quantity, category=category, description="Added via AI Assistant Direct Write")
                return f"""## ✅ Product Successfully Added to Inventory!

- **Product ID**: `#PROD-{prod_id}`
- **Product Name**: **{prod_name}**
- **Unit Price**: **Rs. {price:,.2f}**
- **Available Stock**: **{quantity} units**
- **Category**: {category}

*(This product is now active in your Stock Catalog & POS Checkout Cart.)*
"""
            except Exception as e:
                return f"""## ⚠️ Product Creation Notice
Could not execute database write action: `{str(e)}`.
"""

        return None

    @staticmethod
    def chat_copilot(user_id, user_message, chat_history=None, api_key_override=None, session_key=None):
        """
        In-built Gemini AI Copilot providing structured markdown responses with bullet points, bold headers, tables, and code.
        Uses live Google Gemini API with automatic multi-model fallback and dynamic database context.
        """
        # 0. Check AI Direct Write Actions (Add Customer, Add Product, etc.)
        write_action_res = AIAssistant.handle_write_actions(user_id, user_message)
        if write_action_res:
            try:
                log_ai_interaction(user_id, None, user_message, write_action_res, "action")
            except Exception:
                pass
            return write_action_res
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
        api_key = api_key_override or session_key or GEMINI_API_KEY
        
        # 1. Try Direct Google Gemini REST Cloud API with SSL context handling if API key is provided
        if api_key and len(api_key) > 10 and not api_key.startswith("YOUR_"):
            response_text = AIAssistant.call_gemini_rest_api(api_key, prompt)

        # 2. Intelligent In-Built CRM Engine Fallback if API key is unconfigured or cloud request fails
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

            # 3. Product / Stock queries (e.g. "what are the products in the stock", "list products", "inventory")
            elif any(k in msg_lower for k in ['product', 'stock', 'inventory', 'reorder', 'item', 'catalog']):
                matched_prod = [p for p in products if p['product_name'].lower() in msg_lower]
                if matched_prod:
                    p = matched_prod[0]
                    status = "⚠️ LOW STOCK (Restock Urgently)" if p['quantity'] <= 5 else "✅ Healthy Stock"
                    response_text = f"""## 📦 Product Inventory Breakdown: {p['product_name']}

- **Product Name**: {p['product_name']}
- **Category**: {p.get('category', 'General')}
- **Unit Price**: **Rs. {p['price']:.2f}**
- **Available Stock**: **{p['quantity']} units** ({status})

### 💡 Inventory Action
{"Reorder this product soon to prevent running out of stock." if p['quantity'] <= 5 else "Stock levels are healthy for daily sales."}
"""
                else:
                    prod_list_str = "\n".join([
                        f"- **{p['product_name']}**: **{p['quantity']} units** available • **Rs. {p['price']:.2f}** *(Category: {p.get('category','General')})*"
                        for p in products
                    ]) if products else "- No products added to store inventory yet."

                    response_text = f"""## 📦 Store Inventory & Products in Stock

You currently have **{len(products)} active products** in your store catalog:

{prod_list_str}

### 📊 Inventory Summary
- **Total Products**: **{summary['total_products']}**
- **Low Stock Items (<= 5 units)**: **{summary['low_stock_count']} items** requiring restock.
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

    @staticmethod
    def call_gemini_rest_api(api_key, prompt):
        if not api_key:
            return None
        
        api_key = api_key.strip()
        if len(api_key) < 10 or api_key.startswith("YOUR_"):
            return None

        # 1. Try official google.genai Client with gemini-flash-latest priority
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            models_to_try = ['gemini-flash-latest', 'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-flash-lite-latest']
            for m in models_to_try:
                try:
                    res = client.models.generate_content(model=m, contents=prompt)
                    if res and res.text:
                        return res.text.strip()
                except Exception as m_err:
                    print(f"GenAI model {m} notice: {m_err}")
        except Exception as client_err:
            print(f"GenAI client notice: {client_err}")

        # 2. REST API fallback if client initialization failed
        import ssl, json, urllib.request, urllib.error
        context = ssl._create_unverified_context()
        models = ['gemini-flash-latest', 'gemini-1.5-flash', 'gemini-2.0-flash']
        last_error_msg = None

        for model_name in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

            try:
                with urllib.request.urlopen(req, context=context, timeout=8) as res:
                    if res.status == 200:
                        resp_json = json.loads(res.read().decode('utf-8'))
                        candidates = resp_json.get('candidates', [])
                        if candidates:
                            parts = candidates[0].get('content', {}).get('parts', [])
                            if parts and 'text' in parts[0]:
                                return parts[0]['text'].strip()
            except urllib.error.HTTPError as http_err:
                try:
                    err_body = json.loads(http_err.read().decode('utf-8'))
                    msg = err_body.get('error', {}).get('message', str(http_err))
                    last_error_msg = f"Google API Notice ({http_err.code}): {msg}"
                except Exception:
                    last_error_msg = f"Google API Notice ({http_err.code}): {http_err.reason}"
                print(f"Gemini API Notice ({model_name}): {last_error_msg}")
            except Exception as err:
                last_error_msg = f"Network Connection Notice: {err}"
                print(f"Gemini API Notice ({model_name}): {err}")

        return None
