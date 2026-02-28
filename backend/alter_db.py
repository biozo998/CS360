from database import get_db
from sqlalchemy import text

db = next(get_db())
try:
    db.execute(text("ALTER TABLE cliente ALTER COLUMN cnpj DROP NOT NULL;"))
    db.execute(text("ALTER TABLE cliente DROP CONSTRAINT IF EXISTS cliente_cnpj_key;"))
    db.commit()
    print("Database schema relaxed for CNPJ.")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
