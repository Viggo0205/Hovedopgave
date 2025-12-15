"""
Apply database migration for US-25 (add is_active columns)
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# Read migration SQL
with open('migrations/add_user_active_status.sql', 'r') as f:
    migration_sql = f.read()

# Connect to database
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    database=os.getenv('DB_NAME', 'developer_skills'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD')
)

print("Connected to database")

# Execute migration
try:
    cur = conn.cursor()
    cur.execute(migration_sql)
    conn.commit()
    print("✓ Migration applied successfully!")
    
    # Show results
    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]
    print(f"✓ Total users: {total}")
    
    cur.execute("SELECT COUNT(*) FROM users WHERE is_active = TRUE")
    active = cur.fetchone()[0]
    print(f"✓ Active users: {active}")
    
    cur.close()
except Exception as e:
    conn.rollback()
    print(f"✗ Error applying migration: {e}")
finally:
    conn.close()
    print("Database connection closed")
