import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    """Test home page loads"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Expense Tracker' in response.data


def test_add_page(client):
    """Test add expense page loads"""
    response = client.get('/add')
    assert response.status_code == 200
    assert b'Add Expense' in response.data


def test_add_expense_post(client):
    """Test adding an expense"""
    response = client.post('/add', data={
        'title': 'Test Expense',
        'amount': '100',
        'category': 'Food',
        'expense_date': '2026-06-19'
    })
    # Should redirect to home
    assert response.status_code == 302
