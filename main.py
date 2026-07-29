"""
Main Application Launcher for Local Business CRM
"""
import webbrowser
import threading
import time
from app import app, init_db, seed_admin_if_empty

def open_browser():
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("=" * 60)
    print("[SYSTEM] Initializing Bizflow AI CRM System...")
    print("=" * 60)
    
    init_db()
    seed_admin_if_empty()
    
    print("[SERVER] Starting web application at: http://127.0.0.1:5000")
    print("[INFO] Press Ctrl+C in terminal to stop server.")
    print("=" * 60)

    # Launch browser automatically
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Flask Application
    app.run(host='127.0.0.1', port=5000, debug=True)
