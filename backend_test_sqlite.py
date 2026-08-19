#!/usr/bin/env python3
"""
Comprehensive test suite for SQLite-based desktop backend (port 8002)
Tests authentication, CRUD operations, P&L calculations, and data isolation
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://127.0.0.1:8002/api"
AUTH_TOKEN = "desktop_session_token_123"
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Test data
test_account_data = {
    "account_name": "HDFC Securities Account",
    "broker_name": "HDFC Securities"
}

test_ipo_data = {
    "ipo_name": "TechCorp IPO",
    "lot_size": 100,
    "application_price": 150.0,
    "allotment_quantity": 100,
    "listing_price": 180.0,
    "sell_price": 200.0,
    "demat_account_id": "",  # Will be filled after creating account
    "application_date": "2024-01-15",
    "listing_date": "2024-02-01",
    "broker_charges": 50.0
}

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "total": 0
}

def log_test(test_name: str, passed: bool, message: str = ""):
    """Log test result"""
    test_results["total"] += 1
    status = "✅ PASS" if passed else "❌ FAIL"
    result_msg = f"{status} - {test_name}"
    if message:
        result_msg += f": {message}"
    print(result_msg)
    
    if passed:
        test_results["passed"].append(test_name)
    else:
        test_results["failed"].append(f"{test_name}: {message}")

def test_auth_with_token():
    """Test GET /api/auth/me with valid token"""
    print("\n" + "="*60)
    print("TEST: Authentication with Valid Token")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=HEADERS)
        
        if response.status_code == 200:
            user_data = response.json()
            if "user_id" in user_data and "email" in user_data:
                log_test("Auth with valid token", True, f"User: {user_data.get('email')}")
                return user_data
            else:
                log_test("Auth with valid token", False, "Missing user_id or email in response")
                return None
        else:
            log_test("Auth with valid token", False, f"Status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        log_test("Auth with valid token", False, f"Exception: {str(e)}")
        return None

def test_auth_without_token():
    """Test authentication rejection without token"""
    print("\n" + "="*60)
    print("TEST: Authentication Without Token (Should Reject)")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me")
        
        if response.status_code == 401:
            log_test("Auth rejection without token", True, "Correctly rejected with 401")
        else:
            log_test("Auth rejection without token", False, f"Expected 401, got {response.status_code}")
    except Exception as e:
        log_test("Auth rejection without token", False, f"Exception: {str(e)}")

def test_create_demat_account() -> str:
    """Test POST /api/accounts - Create new demat account"""
    print("\n" + "="*60)
    print("TEST: Create Demat Account")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/accounts",
            headers=HEADERS,
            json=test_account_data
        )
        
        if response.status_code == 200:
            account = response.json()
            if "id" in account and account["account_name"] == test_account_data["account_name"]:
                log_test("Create demat account", True, f"Account ID: {account['id']}")
                return account["id"]
            else:
                log_test("Create demat account", False, "Invalid response structure")
                return None
        else:
            log_test("Create demat account", False, f"Status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        log_test("Create demat account", False, f"Exception: {str(e)}")
        return None

def test_get_demat_accounts():
    """Test GET /api/accounts - List all accounts"""
    print("\n" + "="*60)
    print("TEST: Get All Demat Accounts")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/accounts", headers=HEADERS)
        
        if response.status_code == 200:
            accounts = response.json()
            if isinstance(accounts, list):
                log_test("Get demat accounts", True, f"Found {len(accounts)} account(s)")
                return accounts
            else:
                log_test("Get demat accounts", False, "Response is not a list")
                return []
        else:
            log_test("Get demat accounts", False, f"Status {response.status_code}: {response.text}")
            return []
    except Exception as e:
        log_test("Get demat accounts", False, f"Exception: {str(e)}")
        return []

def test_update_demat_account(account_id: str):
    """Test PUT /api/accounts/{id} - Update account"""
    print("\n" + "="*60)
    print("TEST: Update Demat Account")
    print("="*60)
    
    update_data = {
        "account_name": "HDFC Securities Premium Account",
        "broker_name": "HDFC Securities Ltd"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/accounts/{account_id}",
            headers=HEADERS,
            json=update_data
        )
        
        if response.status_code == 200:
            account = response.json()
            if account["account_name"] == update_data["account_name"]:
                log_test("Update demat account", True, f"Updated to: {account['account_name']}")
            else:
                log_test("Update demat account", False, "Account name not updated")
        else:
            log_test("Update demat account", False, f"Status {response.status_code}: {response.text}")
    except Exception as e:
        log_test("Update demat account", False, f"Exception: {str(e)}")

def test_create_ipo(account_id: str) -> str:
    """Test POST /api/ipos - Create IPO with P&L calculation"""
    print("\n" + "="*60)
    print("TEST: Create IPO with P&L Calculation")
    print("="*60)
    
    ipo_data = {**test_ipo_data, "demat_account_id": account_id}
    
    # Expected P&L: (200 - 150) * 100 - 50 = 4950
    expected_pl = (ipo_data["sell_price"] - ipo_data["application_price"]) * ipo_data["allotment_quantity"] - ipo_data["broker_charges"]
    
    try:
        response = requests.post(
            f"{BASE_URL}/ipos",
            headers=HEADERS,
            json=ipo_data
        )
        
        if response.status_code == 200:
            ipo = response.json()
            if "id" in ipo:
                actual_pl = ipo.get("profit_loss", 0)
                if abs(actual_pl - expected_pl) < 0.01:  # Float comparison with tolerance
                    log_test("Create IPO with P&L", True, f"P&L: {actual_pl} (Expected: {expected_pl})")
                    return ipo["id"]
                else:
                    log_test("Create IPO with P&L", False, f"P&L mismatch: {actual_pl} vs {expected_pl}")
                    return ipo["id"]
            else:
                log_test("Create IPO with P&L", False, "Missing IPO id in response")
                return None
        else:
            log_test("Create IPO with P&L", False, f"Status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        log_test("Create IPO with P&L", False, f"Exception: {str(e)}")
        return None

def test_get_ipos():
    """Test GET /api/ipos - List all IPOs"""
    print("\n" + "="*60)
    print("TEST: Get All IPOs")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/ipos", headers=HEADERS)
        
        if response.status_code == 200:
            ipos = response.json()
            if isinstance(ipos, list):
                log_test("Get IPOs", True, f"Found {len(ipos)} IPO(s)")
                return ipos
            else:
                log_test("Get IPOs", False, "Response is not a list")
                return []
        else:
            log_test("Get IPOs", False, f"Status {response.status_code}: {response.text}")
            return []
    except Exception as e:
        log_test("Get IPOs", False, f"Exception: {str(e)}")
        return []

def test_update_ipo(ipo_id: str):
    """Test PUT /api/ipos/{id} - Update IPO and recalculate P&L"""
    print("\n" + "="*60)
    print("TEST: Update IPO with P&L Recalculation")
    print("="*60)
    
    update_data = {
        "sell_price": 220.0,
        "broker_charges": 75.0
    }
    
    # Expected new P&L: (220 - 150) * 100 - 75 = 6925
    expected_pl = (update_data["sell_price"] - test_ipo_data["application_price"]) * test_ipo_data["allotment_quantity"] - update_data["broker_charges"]
    
    try:
        response = requests.put(
            f"{BASE_URL}/ipos/{ipo_id}",
            headers=HEADERS,
            json=update_data
        )
        
        if response.status_code == 200:
            ipo = response.json()
            actual_pl = ipo.get("profit_loss", 0)
            if abs(actual_pl - expected_pl) < 0.01:
                log_test("Update IPO with P&L recalc", True, f"New P&L: {actual_pl} (Expected: {expected_pl})")
            else:
                log_test("Update IPO with P&L recalc", False, f"P&L mismatch: {actual_pl} vs {expected_pl}")
        else:
            log_test("Update IPO with P&L recalc", False, f"Status {response.status_code}: {response.text}")
    except Exception as e:
        log_test("Update IPO with P&L recalc", False, f"Exception: {str(e)}")

def test_dashboard_stats():
    """Test GET /api/dashboard/stats - Aggregated statistics"""
    print("\n" + "="*60)
    print("TEST: Dashboard Statistics")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard/stats", headers=HEADERS)
        
        if response.status_code == 200:
            stats = response.json()
            required_fields = ["total_invested", "total_returns", "total_pl", "active_ipos", "win_rate"]
            
            missing_fields = [field for field in required_fields if field not in stats]
            
            if not missing_fields:
                log_test("Dashboard stats", True, 
                        f"Total P&L: {stats['total_pl']}, Active IPOs: {stats['active_ipos']}, Win Rate: {stats['win_rate']}%")
                return stats
            else:
                log_test("Dashboard stats", False, f"Missing fields: {missing_fields}")
                return None
        else:
            log_test("Dashboard stats", False, f"Status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        log_test("Dashboard stats", False, f"Exception: {str(e)}")
        return None

def test_delete_ipo(ipo_id: str):
    """Test DELETE /api/ipos/{id} - Delete IPO"""
    print("\n" + "="*60)
    print("TEST: Delete IPO")
    print("="*60)
    
    try:
        response = requests.delete(f"{BASE_URL}/ipos/{ipo_id}", headers=HEADERS)
        
        if response.status_code == 200:
            log_test("Delete IPO", True, "IPO deleted successfully")
        else:
            log_test("Delete IPO", False, f"Status {response.status_code}: {response.text}")
    except Exception as e:
        log_test("Delete IPO", False, f"Exception: {str(e)}")

def test_delete_demat_account(account_id: str):
    """Test DELETE /api/accounts/{id} - Delete account"""
    print("\n" + "="*60)
    print("TEST: Delete Demat Account")
    print("="*60)
    
    try:
        response = requests.delete(f"{BASE_URL}/accounts/{account_id}", headers=HEADERS)
        
        if response.status_code == 200:
            log_test("Delete demat account", True, "Account deleted successfully")
        else:
            log_test("Delete demat account", False, f"Status {response.status_code}: {response.text}")
    except Exception as e:
        log_test("Delete demat account", False, f"Exception: {str(e)}")

def test_data_isolation():
    """Test that data is scoped to authenticated user"""
    print("\n" + "="*60)
    print("TEST: Data Isolation (User-Scoped Data)")
    print("="*60)
    
    # This test verifies that all returned data belongs to the authenticated user
    # In a real scenario, we'd test with multiple users, but here we verify the user_id is consistent
    
    try:
        user_response = requests.get(f"{BASE_URL}/auth/me", headers=HEADERS)
        if user_response.status_code != 200:
            log_test("Data isolation", False, "Cannot get user data")
            return
        
        user_id = user_response.json().get("user_id")
        
        # Check accounts
        accounts_response = requests.get(f"{BASE_URL}/accounts", headers=HEADERS)
        if accounts_response.status_code == 200:
            accounts = accounts_response.json()
            if all(acc.get("user_id") == user_id for acc in accounts):
                log_test("Data isolation - Accounts", True, f"All accounts belong to user {user_id}")
            else:
                log_test("Data isolation - Accounts", False, "Found accounts from other users")
        
        # Check IPOs
        ipos_response = requests.get(f"{BASE_URL}/ipos", headers=HEADERS)
        if ipos_response.status_code == 200:
            ipos = ipos_response.json()
            if all(ipo.get("user_id") == user_id for ipo in ipos):
                log_test("Data isolation - IPOs", True, f"All IPOs belong to user {user_id}")
            else:
                log_test("Data isolation - IPOs", False, "Found IPOs from other users")
                
    except Exception as e:
        log_test("Data isolation", False, f"Exception: {str(e)}")

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {len(test_results['passed'])}")
    print(f"Failed: {len(test_results['failed'])}")
    print(f"Success Rate: {len(test_results['passed'])/test_results['total']*100:.1f}%")
    
    if test_results['failed']:
        print("\n❌ FAILED TESTS:")
        for failure in test_results['failed']:
            print(f"  - {failure}")
    
    print("\n" + "="*60)

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SQLite Desktop Backend Test Suite")
    print(f"Base URL: {BASE_URL}")
    print(f"Auth Token: {AUTH_TOKEN}")
    print("="*60)
    
    # Test authentication
    user = test_auth_with_token()
    test_auth_without_token()
    
    if not user:
        print("\n❌ Authentication failed. Cannot proceed with other tests.")
        return
    
    # Test demat accounts CRUD
    account_id = test_create_demat_account()
    if account_id:
        test_get_demat_accounts()
        test_update_demat_account(account_id)
        
        # Test IPO CRUD with P&L calculations
        ipo_id = test_create_ipo(account_id)
        if ipo_id:
            test_get_ipos()
            test_update_ipo(ipo_id)
            
            # Test dashboard
            test_dashboard_stats()
            
            # Test data isolation
            test_data_isolation()
            
            # Cleanup
            test_delete_ipo(ipo_id)
        
        test_delete_demat_account(account_id)
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    main()
