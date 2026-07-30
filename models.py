from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

# ================= USER & AUTH MODEL =================

def create_user(username, email, password, name, role="Admin", reset_question="What is your store name?", reset_answer="Bizflow Store"):
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    reset_answer_clean = reset_answer.strip().lower()
    
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, name, role, reset_question, reset_answer)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (username, email, password_hash, name, role, reset_question, reset_answer_clean))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_by_username_or_email(identifier):
    conn = get_db_connection()
    user = conn.execute('''
        SELECT * FROM users 
        WHERE username = ? OR email = ?
    ''', (identifier, identifier)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def verify_user_login(identifier, password):
    user = get_user_by_username_or_email(identifier)
    if not user:
        return None
    if check_password_hash(user['password_hash'], password):
        return user
    return None

def reset_user_password(identifier, reset_answer, new_password):
    user = get_user_by_username_or_email(identifier)
    if not user:
        raise ValueError("No account found with provided username/email.")
    
    if user['reset_answer'].strip().lower() != reset_answer.strip().lower():
        raise ValueError("Security question answer does not match.")
    
    new_hash = generate_password_hash(new_password)
    conn = get_db_connection()
    conn.execute('''
        UPDATE users
        SET password_hash = ?
        WHERE user_id = ?
    ''', (new_hash, user['user_id']))
    conn.commit()
    conn.close()
    return True

# ================= CUSTOMER MODEL (Per-User Isolated) =================

def get_all_customers(user_id):
    conn = get_db_connection()
    customers = conn.execute('''
        SELECT c.*, 
               COALESCE(COUNT(s.sale_id), 0) as total_orders,
               COALESCE(SUM(s.total_amount), 0.0) as total_spent,
               MAX(s.date) as last_purchase_date
        FROM customers c
        LEFT JOIN sales s ON c.customer_id = s.customer_id AND s.user_id = c.user_id
        WHERE c.user_id = ?
        GROUP BY c.customer_id
        ORDER BY c.created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(c) for c in customers]

def get_customer_by_id(customer_id, user_id):
    conn = get_db_connection()
    customer = conn.execute('''
        SELECT c.*, 
               COALESCE(COUNT(s.sale_id), 0) as total_orders,
               COALESCE(SUM(s.total_amount), 0.0) as total_spent,
               MAX(s.date) as last_purchase_date
        FROM customers c
        LEFT JOIN sales s ON c.customer_id = s.customer_id AND s.user_id = c.user_id
        WHERE c.customer_id = ? AND c.user_id = ?
        GROUP BY c.customer_id
    ''', (customer_id, user_id)).fetchone()
    conn.close()
    return dict(customer) if customer else None

def add_customer(user_id, name, phone, email, address):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO customers (user_id, name, phone, email, address)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, name, phone, email, address))
    customer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return customer_id

def update_customer(customer_id, user_id, name, phone, email, address):
    conn = get_db_connection()
    conn.execute('''
        UPDATE customers
        SET name = ?, phone = ?, email = ?, address = ?
        WHERE customer_id = ? AND user_id = ?
    ''', (name, phone, email, address, customer_id, user_id))
    conn.commit()
    conn.close()

def delete_customer(customer_id, user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM customers WHERE customer_id = ? AND user_id = ?', (customer_id, user_id))
    conn.commit()
    conn.close()

def search_customers(user_id, query):
    conn = get_db_connection()
    search = f"%{query}%"
    customers = conn.execute('''
        SELECT c.*, 
               COALESCE(COUNT(s.sale_id), 0) as total_orders,
               COALESCE(SUM(s.total_amount), 0.0) as total_spent,
               MAX(s.date) as last_purchase_date
        FROM customers c
        LEFT JOIN sales s ON c.customer_id = s.customer_id AND s.user_id = c.user_id
        WHERE c.user_id = ? AND (c.name LIKE ? OR c.phone LIKE ? OR c.email LIKE ?)
        GROUP BY c.customer_id
        ORDER BY c.name ASC
    ''', (user_id, search, search, search)).fetchall()
    conn.close()
    return [dict(c) for c in customers]

# ================= PRODUCT MODEL (Per-User Isolated) =================

def get_all_products(user_id):
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products WHERE user_id = ? ORDER BY product_name ASC', (user_id,)).fetchall()
    conn.close()
    return [dict(p) for p in products]

def get_product_by_id(product_id, user_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE product_id = ? AND user_id = ?', (product_id, user_id)).fetchone()
    conn.close()
    return dict(product) if product else None

def add_product(user_id, name, price, quantity, category="General", description=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (user_id, product_name, price, quantity, category, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, name, price, quantity, category, description))
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return product_id

def update_product(product_id, user_id, name, price, quantity, category, description):
    conn = get_db_connection()
    conn.execute('''
        UPDATE products
        SET product_name = ?, price = ?, quantity = ?, category = ?, description = ?
        WHERE product_id = ? AND user_id = ?
    ''', (name, price, quantity, category, description, product_id, user_id))
    conn.commit()
    conn.close()

def delete_product(product_id, user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE product_id = ? AND user_id = ?', (product_id, user_id))
    conn.commit()
    conn.close()

def get_low_stock_products(user_id, threshold=5):
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products WHERE user_id = ? AND quantity <= ? ORDER BY quantity ASC', (user_id, threshold)).fetchall()
    conn.close()
    return [dict(p) for p in products]

# ================= SALES MODEL (Per-User Isolated) =================

def create_sale(user_id, customer_id, items, discount=0.0, payment_method="Cash"):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    total_amount = 0.0
    processed_items = []
    
    for item in items:
        prod = cursor.execute('SELECT * FROM products WHERE product_id = ? AND user_id = ?', (item['product_id'], user_id)).fetchone()
        if not prod:
            raise ValueError(f"Product ID {item['product_id']} not found or does not belong to your account.")
        if prod['quantity'] < item['quantity']:
            raise ValueError(f"Insufficient stock for {prod['product_name']}. Available: {prod['quantity']}")
        
        unit_price = prod['price']
        subtotal = unit_price * item['quantity']
        total_amount += subtotal
        processed_items.append({
            'product_id': item['product_id'],
            'product_name': prod['product_name'],
            'quantity': item['quantity'],
            'unit_price': unit_price,
            'subtotal': subtotal
        })
    
    final_amount = max(0.0, total_amount - discount)
    if not payment_method:
        payment_method = "Cash"
    
    cursor.execute('''
        INSERT INTO sales (user_id, customer_id, total_amount, discount, payment_method)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, customer_id, final_amount, discount, payment_method))
    sale_id = cursor.lastrowid
    
    for p in processed_items:
        cursor.execute('''
            INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, subtotal)
            VALUES (?, ?, ?, ?, ?)
        ''', (sale_id, p['product_id'], p['quantity'], p['unit_price'], p['subtotal']))
        
        cursor.execute('''
            UPDATE products
            SET quantity = quantity - ?
            WHERE product_id = ? AND user_id = ?
        ''', (p['quantity'], p['product_id'], user_id))
        
    conn.commit()
    conn.close()
    return sale_id

def get_all_sales(user_id):
    conn = get_db_connection()
    sales = conn.execute('''
        SELECT s.*, c.name as customer_name, c.phone as customer_phone
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
        WHERE s.user_id = ?
        ORDER BY s.date DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(s) for s in sales]

def get_sale_details(sale_id, user_id):
    conn = get_db_connection()
    sale = conn.execute('''
        SELECT s.*, c.name as customer_name, c.phone as customer_phone, c.email as customer_email, c.address as customer_address
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
        WHERE s.sale_id = ? AND s.user_id = ?
    ''', (sale_id, user_id)).fetchone()
    
    if not sale:
        conn.close()
        return None
        
    items = conn.execute('''
        SELECT si.*, p.product_name
        FROM sale_items si
        JOIN products p ON si.product_id = p.product_id
        WHERE si.sale_id = ?
    ''', (sale_id,)).fetchall()
    
    conn.close()
    res = dict(sale)
    res['items'] = [dict(i) for i in items]
    return res

# ================= INVOICE MODEL (Per-User Isolated) =================

def add_invoice_record(user_id, sale_id, customer_id, file_path, amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO invoices (user_id, sale_id, customer_id, file_path, amount)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, sale_id, customer_id, file_path, amount))
    invoice_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return invoice_id

def get_all_invoices(user_id):
    conn = get_db_connection()
    invoices = conn.execute('''
        SELECT i.*, c.name as customer_name, s.date as sale_date, s.payment_method
        FROM invoices i
        JOIN customers c ON i.customer_id = c.customer_id
        JOIN sales s ON i.sale_id = s.sale_id
        WHERE i.user_id = ?
        ORDER BY i.date DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(inv) for inv in invoices]

# ================= AI LOGS (Per-User Isolated) =================

def log_ai_interaction(user_id, customer_id, prompt, response, req_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ai_logs (user_id, customer_id, prompt, response, type)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, customer_id, prompt, response, req_type))
    conn.commit()
    conn.close()
