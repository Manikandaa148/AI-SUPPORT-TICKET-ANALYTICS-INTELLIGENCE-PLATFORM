import sqlite3
import os
import pandas as pd
from app.config import settings
from app.utils.logging_config import logger
from app.data.loader import load_csv_to_dataframe

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(settings.DATABASE_PATH):
        logger.info(f"Database {settings.DATABASE_PATH} already exists.")
        return

    logger.info(f"Initializing database at {settings.DATABASE_PATH}")
    df = load_csv_to_dataframe(settings.DATA_PATH)
    
    if df is None or df.empty:
        logger.error("No data available to initialize database.")
        return
        
    try:
        conn = get_db_connection()
        # Ensure created_at is converted to string for sqlite
        df_sql = df.copy()
        if 'created_at' in df_sql.columns:
            df_sql['created_at'] = df_sql['created_at'].astype(str)
            
        df_sql.to_sql("support_tickets", conn, if_exists="replace", index=False)
        
        # Create indexes
        cursor = conn.cursor()
        cursor.execute("CREATE INDEX idx_ticket_id ON support_tickets (ticket_id)")
        cursor.execute("CREATE INDEX idx_category ON support_tickets (category)")
        cursor.execute("CREATE INDEX idx_priority ON support_tickets (priority)")
        cursor.execute("CREATE INDEX idx_status ON support_tickets (status)")
        cursor.execute("CREATE INDEX idx_agent_id ON support_tickets (agent_id)")
        conn.commit()
        
        logger.info("Database initialized and populated successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

def get_total_tickets() -> int:
    try:
        if not os.path.exists(settings.DATABASE_PATH):
            return 0
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM support_tickets")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        logger.error(f"Error getting total tickets: {e}")
        return 0
