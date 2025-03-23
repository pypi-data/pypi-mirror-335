from config_loader import load_project_config
import os
import sqlite3

def init_sqlite(filename):
    if not filename:
        raise ValueError("SQLite filename not specified in config file.")
    
    filename = os.path.abspath(filename)
    print(f"[+] SQLite DB file: {filename}")
    
    if os.path.exists(filename):
        print(f"[!] SQLite DB already exists at {filename}")
    else:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        print(f"[+] Creating SQLite DB at {filename}")
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT
            );
        """)

        conn.commit()
        conn.close()
        print("[+] SQLite DB created successfully.")

def main():
    db_config = load_project_config()
    db_type = db_config.get("type", "").lower()

    if db_type == "sqlite":
        filename = db_config.get("filename", "").strip()
        init_sqlite(filename)

    elif db_type in ["mysql", "mariadb"]:
        print("[!] MySQL/MariaDB not implemented in this example.")
        # You'd call init_mysql() here

    else:
        raise ValueError(f"Unsupported database type: {db_type}")

if __name__ == "__main__":
    main()
