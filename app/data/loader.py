import pandas as pd
import sqlite3
import os
from typing import Optional
from app.config import settings
from app.utils.logging_config import logger

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure column names are stripped of whitespace and lowercase
    df.columns = df.columns.str.strip().str.lower()
    
    # Handle missing values
    # For resolution_time_hrs, if status is Open, it will naturally be missing.
    # For numeric columns, convert to numeric.
    if 'resolution_time_hrs' in df.columns:
        df['resolution_time_hrs'] = pd.to_numeric(df['resolution_time_hrs'], errors='coerce')
    if 'response_time_hrs' in df.columns:
        df['response_time_hrs'] = pd.to_numeric(df['response_time_hrs'], errors='coerce')
    if 'customer_rating' in df.columns:
        df['customer_rating'] = pd.to_numeric(df['customer_rating'], errors='coerce')

    # Dates
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')

    return df

def load_csv_to_dataframe(csv_path: str = settings.DATA_PATH) -> Optional[pd.DataFrame]:
    try:
        logger.info(f"Loading data from {csv_path}")
        df = pd.read_csv(csv_path)
        df = clean_data(df)
        logger.info(f"Successfully loaded {len(df)} records from {csv_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading CSV {csv_path}: {str(e)}")
        return None
