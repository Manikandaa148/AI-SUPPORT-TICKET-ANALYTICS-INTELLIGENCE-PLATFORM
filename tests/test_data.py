import pytest
from app.data.loader import load_csv_to_dataframe
from app.data.database import init_db, get_total_tickets
from app.config import settings

def test_load_csv():
    df = load_csv_to_dataframe()
    assert df is not None
    assert not df.empty
    assert 'ticket_id' in df.columns
    assert 'created_at' in df.columns

def test_init_db():
    init_db()
    total = get_total_tickets()
    assert total > 0
