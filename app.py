import json
import os
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, 
    url_for, flash, send_file, jsonify, session, g
)

from config import SECRET_KEY, INVOICES_DIR, BASE_DIR, GEMINI_API_KEY
from database import init_db, purge_database_and_reset_ids
from models import (
    get_all_customers, get_all_products, get_all_sales, get_all_invoices,
    get_customer_by_id, get_product_by_id, get_sale_details,
    add_customer, update_customer, delete_customer,
    add_product, update_product, delete_product,
    create_sale, create_user, verify_user_login, reset_user_password,
    get_user_by_id, get_user_by_username_or_email,
    get_ai_chat_history, delete_ai_chat_history, delete_single_ai_log
)
from customer import CustomerManager
from product import ProductManager
from sales import SalesManager
from invoice import generate_pdf_invoice
from reports import BusinessReporter
from ai_assistant import AIAssistant
from translations import TRANSLATIONS, SUPPORTED_LANGUAGES, get_translation

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['TEMPLATES_AUTO_RELOAD'] = True
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

def seed_admin_if_empty():
    default_users = [
        ("admin", "admin@store.com", "admin123", "Store Admin", "Admin"),
        ("uday734", "uday734@store.com", "uday734", "Thota Uday kiran", "Admin")
    ]
    for username, email, password, name, role in default_users:
        if not get_user_by_username_or_email(username):
            try:
                create_user(
                    username=username, 
                    email=email, 
                    password=password, 
                    name=name, 
                    role=role,
                    reset_question="What is your store name?",
                    reset_answer="Bizflow Store"
                )
            except Exception:
                pass

seed_admin_if_empty()

# Context Processor for Global User State & Internationalization
@app.context_processor
def inject_global_vars():
    user_id = session.get('user_id')
    user = get_user_by_id(user_id) if user_id else None
    
    current_lang = session.get('lang', 'en')
    if current_lang not in SUPPORTED_LANGUAGES:
        current_lang = 'en'
        
    def t(key):
        return get_translation(key, current_lang)
        
    return dict(
        current_user=user,
        current_lang=current_lang,
        supported_languages=SUPPORTED_LANGUAGES,
        translations=TRANSLATIONS,
        t=t
    )

# Language Switcher Route
@app.route('/set-lang/<lang_code>', methods=['GET', 'POST'])
def set_language_route(lang_code):
    if lang_code in SUPPORTED_LANGUAGES:
        session['lang'] = lang_code
    else:
        session['lang'] = 'en'
    
    if request.method == 'POST' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'lang': session['lang']})
    
    referrer = request.referrer
    if referrer and referrer != request.url:
        return redirect(referrer)
    return redirect(url_for('index'))

@app.route('/api/translations')
def get_translations_api():
    return jsonify(TRANSLATIONS)

# Authentication Protection Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please sign in to access your Bizflow AI workspace.', 'error')
            return redirect(url_for('login_route'))
        return f(*args, **kwargs)
    return decorated_function

# ================= AUTHENTICATION ROUTES =================

@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '').strip()

        user = verify_user_login(identifier, password)
        if user:
            session.permanent = True
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username/email or password. Please try again.", 'error')
            return render_template('auth.html', mode='login')

    return render_template('auth.html', mode='login')

@app.route('/register', methods=['GET', 'POST'])
def register_route():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip() or f"{username}@store.com"
        password = request.form.get('password', '').strip()
        reset_question = request.form.get('reset_question', 'What is your store name?').strip()
        reset_answer = request.form.get('reset_answer', '').strip()

        if not username or not password or not name:
            flash("All required fields must be filled out.", 'error')
            return render_template('auth.html', mode='register')

        if get_user_by_username_or_email(username):
            flash("Username is already registered.", 'error')
            return render_template('auth.html', mode='register')

        try:
            user_id = create_user(username, email, password, name, role="Store Manager", reset_question=reset_question, reset_answer=reset_answer)
            session['user_id'] = user_id
            session['username'] = username
            flash("Account registered successfully! Welcome to Bizflow AI.", 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f"Registration failed: {str(e)}", 'error')
            return render_template('auth.html', mode='register')

    return render_template('auth.html', mode='register')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password_route():
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        reset_answer = request.form.get('reset_answer', '').strip()
        new_password = request.form.get('new_password', '').strip()

        try:
            reset_user_password(identifier, reset_answer, new_password)
            flash("Password updated successfully! You can now sign in with your new password.", 'success')
            return redirect(url_for('login_route'))
        except Exception as e:
            flash(f"Password reset failed: {str(e)}", 'error')
            return render_template('auth.html', mode='forgot')

    return render_template('auth.html', mode='forgot')

@app.route('/logout')
def logout_route():
    session.clear()
    flash("You have been signed out.", 'success')
    return redirect(url_for('login_route'))

# ================= LANDING PAGE & CRM CORE ROUTES =================

@app.route('/')
def index():
    user_id = session.get('user_id')
    user = get_user_by_id(user_id) if user_id else None
    stats = BusinessReporter.get_landing_statistics(user_id)
    return render_template('index.html', current_user=user, stats=stats)

@app.route('/landing-stats')
def landing_stats_route():
    user_id = session.get('user_id')
    stats = BusinessReporter.get_landing_statistics(user_id)
    return jsonify(stats)

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    summary = BusinessReporter.get_dashboard_summary(user_id)
    return render_template('dashboard.html', active_page='dashboard', summary=summary)

# ----- Customers -----
@app.route('/customers')
@login_required
def customers_page():
    user_id = session['user_id']
    customers = CustomerManager.list_customers(user_id)
    return render_template('customers.html', active_page='customers', customers=customers)

@app.route('/customers/add', methods=['POST'])
@login_required
def add_customer_route():
    user_id = session['user_id']
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email', '')
    address = request.form.get('address', '')
    try:
        CustomerManager.create_customer(user_id, name, phone, email, address)
        flash('Customer added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding customer: {str(e)}', 'error')
    return redirect(url_for('customers_page'))

@app.route('/customers/edit/<int:customer_id>', methods=['POST'])
@login_required
def edit_customer_route(customer_id):
    user_id = session['user_id']
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email', '')
    address = request.form.get('address', '')
    try:
        CustomerManager.edit_customer(customer_id, user_id, name, phone, email, address)
        flash('Customer details updated!', 'success')
    except Exception as e:
        flash(f'Error updating customer: {str(e)}', 'error')
    return redirect(url_for('customers_page'))

@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
@login_required
def delete_customer_route(customer_id):
    user_id = session['user_id']
    try:
        CustomerManager.remove_customer(customer_id, user_id)
        flash('Customer deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting customer: {str(e)}', 'error')
    return redirect(url_for('customers_page'))

# ----- Products & Inventory -----
@app.route('/products')
@login_required
def products_page():
    user_id = session['user_id']
    products = ProductManager.list_products(user_id)
    return render_template('products.html', active_page='products', products=products)

@app.route('/products/add', methods=['POST'])
@login_required
def add_product_route():
    user_id = session['user_id']
    name = request.form.get('name')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    category = request.form.get('category', 'General')
    description = request.form.get('description', '')
    try:
        ProductManager.create_product(user_id, name, float(price), int(quantity), category, description)
        flash('Product added to catalog!', 'success')
    except Exception as e:
        flash(f'Error adding product: {str(e)}', 'error')
    return redirect(url_for('products_page'))

@app.route('/products/edit/<int:product_id>', methods=['POST'])
@login_required
def edit_product_route(product_id):
    user_id = session['user_id']
    name = request.form.get('name')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    category = request.form.get('category', 'General')
    description = request.form.get('description', '')
    try:
        ProductManager.edit_product(product_id, user_id, name, float(price), int(quantity), category, description)
        flash('Product updated!', 'success')
    except Exception as e:
        flash(f'Error updating product: {str(e)}', 'error')
    return redirect(url_for('products_page'))

@app.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product_route(product_id):
    user_id = session['user_id']
    try:
        ProductManager.remove_product(product_id, user_id)
        flash('Product removed.', 'success')
    except Exception as e:
        flash(f'Error deleting product: {str(e)}', 'error')
    return redirect(url_for('products_page'))

# ----- Sales & POS -----
@app.route('/sales')
@login_required
def sales_page():
    user_id = session['user_id']
    customers = CustomerManager.list_customers(user_id)
    products = ProductManager.list_products(user_id)
    sales = SalesManager.list_sales(user_id)
    return render_template('sales.html', active_page='sales', customers=customers, products=products, sales=sales)

@app.route('/sales/create', methods=['POST'])
@login_required
def create_sale_route():
    user_id = session['user_id']
    customer_id = request.form.get('customer_id')
    discount = float(request.form.get('discount', 0.0) or 0.0)
    payment_method = request.form.get('payment_method', 'Cash').strip() or 'Cash'
    items_json = request.form.get('items_json', '[]')
    
    try:
        items = json.loads(items_json)
        if not items:
            flash('Please add at least one item to the sale cart.', 'error')
            return redirect(url_for('sales_page'))

        sale_id = SalesManager.process_sale(user_id, int(customer_id), items, discount, payment_method)
        filename, filepath = generate_pdf_invoice(sale_id, user_id)
        
        flash(f'Sale #SALE-{sale_id} completed via {payment_method}! PDF Invoice generated.', 'success')
    except Exception as e:
        flash(f'Sale processing failed: {str(e)}', 'error')

    return redirect(url_for('sales_page'))

# ----- Invoices -----
@app.route('/invoices')
@login_required
def invoices_page():
    user_id = session['user_id']
    invoices = get_all_invoices(user_id)
    return render_template('invoices.html', active_page='invoices', invoices=invoices)

@app.route('/invoices/pdf/<int:sale_id>')
@login_required
def generate_invoice_pdf_route(sale_id):
    user_id = session['user_id']
    try:
        filename, filepath = generate_pdf_invoice(sale_id, user_id)
        return send_file(filepath, mimetype='application/pdf')
    except Exception as e:
        flash(f'Could not generate PDF: {str(e)}', 'error')
        return redirect(url_for('sales_page'))

@app.route('/invoices/download/<int:invoice_id>')
@login_required
def download_invoice_file(invoice_id):
    user_id = session['user_id']
    invoices = get_all_invoices(user_id)
    inv = next((i for i in invoices if i['invoice_id'] == invoice_id), None)
    if not inv or not os.path.exists(inv['file_path']):
        flash('Invoice file not found or access denied.', 'error')
        return redirect(url_for('invoices_page'))
    
    as_attachment = request.args.get('download', '0') == '1'
    return send_file(inv['file_path'], mimetype='application/pdf', as_attachment=as_attachment)

# ----- Conversational AI Chatbot -----
@app.route('/ai-assistant')
@login_required
def ai_assistant_page():
    user_id = session['user_id']
    customers = CustomerManager.list_customers(user_id)
    products = ProductManager.list_products(user_id)
    chat_history = get_ai_chat_history(user_id)
    return render_template(
        'ai_assistant.html', 
        active_page='ai', 
        customers=customers,
        products=products,
        chat_history=chat_history
    )

@app.route('/api/clear-ai-history', methods=['POST', 'DELETE'])
@login_required
def clear_ai_history_route():
    user_id = session['user_id']
    delete_ai_chat_history(user_id)
    return jsonify({'success': True, 'message': 'Chat history cleared successfully.'})

@app.route('/api/delete-ai-log/<int:log_id>', methods=['POST', 'DELETE'])
@login_required
def delete_single_ai_log_route(log_id):
    user_id = session['user_id']
    delete_single_ai_log(user_id, log_id)
    return jsonify({'success': True, 'message': 'Log deleted.'})

@app.route('/api/ai-chat', methods=['GET', 'POST'])
@login_required
def api_ai_chat_route():
    user_id = session['user_id']
    
    data = request.get_json(silent=True) or {}
    message = (data.get('message') or data.get('msg') or request.args.get('message') or request.args.get('msg') or request.args.get('prompt') or request.form.get('message') or request.form.get('msg') or '').strip()
    api_key_override = (data.get('gemini_api_key') or session.get('gemini_api_key') or os.environ.get('GEMINI_API_KEY') or '').strip()
    
    if not message:
        return jsonify({'error': 'Message prompt is required.'}), 400

    try:
        reply = AIAssistant.chat_copilot(user_id, message, api_key_override=api_key_override)
        return jsonify({'reply': reply, 'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-gemini-key', methods=['POST'])
@login_required
def save_gemini_key_route():
    data = request.get_json() or {}
    key = data.get('gemini_api_key', '').strip()
    
    session['gemini_api_key'] = key

    env_path = BASE_DIR / ".env"
    with open(env_path, "w") as f:
        f.write(f"GEMINI_API_KEY={key}\nSECRET_KEY={SECRET_KEY}\n")
        
    os.environ["GEMINI_API_KEY"] = key
    import config
    config.GEMINI_API_KEY = key
    
    return jsonify({'success': True, 'message': 'Gemini API Key updated successfully!'})

if __name__ == '__main__':
    print("Starting Bizflow AI Web Application on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
