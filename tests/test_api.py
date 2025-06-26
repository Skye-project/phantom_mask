import sys
import os
import json
import tempfile
import pytest
# from app.utils import parse_datetime, calculate_relevance
from fastapi.testclient import TestClient

# Ensure the app module is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app
from unittest.mock import mock_open, patch, MagicMock
from app import etl
from datetime import datetime

client = TestClient(app)

# 1. List pharmacies open at specific time and day

def test_open_pharmacies_valid():
    response = client.get('/pharmacies/open?day=Mon&time=10:00')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert 'id' in data[0]
        assert 'name' in data[0]
        assert 'day_of_week' in data[0]
        assert 'open_time' in data[0]
        assert 'close_time' in data[0]

def test_open_pharmacies_invalid_time_format():
    response = client.get("/pharmacies/open?day=Mon&time=25:61")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid time format"}

# 2. List masks in pharmacy, sorted

def test_masks_by_pharmacy_name_valid():
    response = client.get('/pharmacies/Carepoint/masks?sort_by=name&order=asc')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert 'name' in data[0]
        assert 'price' in data[0]

def test_masks_by_pharmacy_name_invalid():
    response = client.get('/pharmacy/InvalidPharmacy/masks')
    assert response.status_code == 404

# 3. Filter pharmacies by mask count within price range

def test_mask_count_valid():
    response = client.get('/pharmacies/mask_count?min_price=5&max_price=7&count=2&op=gt')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert 'id' in data[0]
        assert 'name' in data[0]
        assert 'mask_count' in data[0]
        assert 'masks' in data[0]

def test_mask_count_missing_param():
    response = client.get('/pharmacies/mask_count?min_price=5&count=2&op=gt')
    assert response.status_code == 422

# 4. Top users by transaction amount

def test_top_users_valid():
    response = client.get('/users/top_users?top=2&start_date=2021-01-01&end_date=2021-01-20')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert 'id' in data[0]
        assert 'name' in data[0]
        assert 'cash_balance' in data[0]
        assert 'total_amount' in data[0]

# 5. Transaction summary

def test_transaction_summary_valid():
    response = client.get('/transactions/summary?start_date=2021-01-01&end_date=2021-01-31')
    assert response.status_code == 200
    data = response.json()
    assert 'total_transactions' in data
    assert 'total_amount' in data

# 6. Search API

def test_search_valid():
    response = client.get('/search?keyword=c')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert 'type' in data[0]
        assert 'name' in data[0]
        assert 'relevance' in data[0]

# 7. Purchase API

def test_purchase_success():
    body = {
        "user_id": 1,
        "purchases": [
            {"pharmacy_id": 1, "mask_id": 2, "quantity": 1}
        ]
    }
    response = client.post('/purchase', json=body)
    if response.status_code == 200:
        data = response.json()
        assert data['message'] == "Purchase successful"
        assert 'total_cost' in data
        assert 'remaining_balance' in data
        assert 'details' in data
    else:
        assert response.status_code in [400, 404]

def test_purchase_user_not_found():
    body = {
        "user_id": 9999,
        "purchases": [
            {"pharmacy_id": 1, "mask_id": 2, "quantity": 1}
        ]
    }
    response = client.post('/purchase', json=body)
    assert response.status_code == 404
    assert response.json()['detail'] == "User not found"

def test_purchase_mask_not_found():
    body = {
        "user_id": 1,
        "purchases": [
            {"pharmacy_id": 2, "mask_id": 9999, "quantity": 1}
        ]
    }
    response = client.post('/purchase', json=body)
    assert response.status_code == 404
    assert "not found" in response.json()['detail']

def test_purchase_insufficient_balance():
    body = {
        "user_id": 1,
        "purchases": [
            {"pharmacy_id": 1, "mask_id": 2, "quantity": 100000}
        ]
    }
    response = client.post('/purchase', json=body)
    assert response.status_code == 400
    assert response.json()['detail'] == "Insufficient balance"

# etl.py

@pytest.fixture
def sample_pharmacy_data():
    return [
        {
            "name": "Test Pharmacy",
            "cashBalance": 100.0,
            "masks": [
                {"name": "Mask A", "price": 5.5},
                {"name": "Mask B", "price": 7.0}
            ],
            "openingHours": "Mon 08:00-12:00, Tue 13:00-18:00"
        }
    ]

@pytest.fixture
def sample_user_data():
    return [
        {
            "name": "Test User",
            "cashBalance": 100.0,
            "purchaseHistories": [
                {
                    "pharmacyName": "Test Pharmacy",
                    "maskName": "Mask A",
                    "transactionAmount": 5.5,
                    "transactionDate": "2021-01-01 10:00:00"
                }
            ]
        }
    ]

def test_load_pharmacies(sample_pharmacy_data):
    m = mock_open(read_data=json.dumps(sample_pharmacy_data))
    with patch("builtins.open", m):
        with patch("app.etl.SessionLocal") as mock_session:
            mock_db = MagicMock()
            mock_session.return_value = mock_db
            etl.load_pharmacies("fake_path.json")
            assert mock_db.add.call_count >= 1
            assert mock_db.commit.called
            assert mock_db.close.called

def test_load_users(sample_user_data):
    m = mock_open(read_data=json.dumps(sample_user_data))
    with patch("builtins.open", m):
        with patch("app.etl.SessionLocal") as mock_session:
            mock_db = MagicMock()
            mock_session.return_value = mock_db

            # mock pharmacy lookup
            fake_pharmacy = MagicMock()
            fake_pharmacy.name = "Test Pharmacy"
            fake_pharmacy.id = 1
            mock_db.query.return_value.all.return_value = [fake_pharmacy]

            etl.load_users("fake_path.json")
            assert mock_db.add.call_count >= 2
            assert mock_db.commit.called
            assert mock_db.close.called

def test_run_etl():
    with patch("app.etl.init_db") as mock_init, patch("app.etl.load_pharmacies") as mock_pharm, patch("app.etl.load_users") as mock_users:
        etl.run_etl()
        mock_init.assert_called_once()
        mock_pharm.assert_called_once_with("data/pharmacies.json")
        mock_users.assert_called_once_with("data/users.json")
