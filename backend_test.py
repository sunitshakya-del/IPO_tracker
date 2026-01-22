import requests
import sys
import json
from datetime import datetime

class IPOTrackerAPITester:
    def __init__(self, base_url="https://ipo-profit-tracker.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_accounts = []
        self.created_ipos = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}, Expected: {expected_status}"
            
            if not success:
                try:
                    error_detail = response.json()
                    details += f", Response: {error_detail}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test(name, success, details)
            
            if success:
                try:
                    return response.json() if response.content else {}
                except:
                    return {}
            return None

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_create_account(self):
        """Test creating a demat account"""
        account_data = {
            "account_name": f"Test Account {datetime.now().strftime('%H%M%S')}",
            "broker_name": "Test Broker"
        }
        
        result = self.run_test("Create Demat Account", "POST", "accounts", 200, account_data)
        if result and 'id' in result:
            self.created_accounts.append(result['id'])
            return result
        return None

    def test_get_accounts(self):
        """Test fetching all accounts"""
        return self.run_test("Get All Accounts", "GET", "accounts", 200)

    def test_update_account(self, account_id):
        """Test updating an account"""
        update_data = {
            "account_name": "Updated Test Account",
            "broker_name": "Updated Broker"
        }
        return self.run_test("Update Account", "PUT", f"accounts/{account_id}", 200, update_data)

    def test_create_ipo(self, account_id):
        """Test creating an IPO"""
        ipo_data = {
            "ipo_name": f"Test IPO {datetime.now().strftime('%H%M%S')}",
            "lot_size": 100,
            "application_price": 500.0,
            "allotment_quantity": 50,
            "listing_price": 600.0,
            "demat_account_id": account_id,
            "application_date": "2024-01-15",
            "listing_date": "2024-01-20"
        }
        
        result = self.run_test("Create IPO", "POST", "ipos", 200, ipo_data)
        if result and 'id' in result:
            self.created_ipos.append(result['id'])
            # Verify P&L calculation: (600 - 500) * 50 = 5000
            expected_pl = (ipo_data['listing_price'] - ipo_data['application_price']) * ipo_data['allotment_quantity']
            if abs(result.get('profit_loss', 0) - expected_pl) < 0.01:
                self.log_test("P&L Calculation Verification", True)
            else:
                self.log_test("P&L Calculation Verification", False, 
                            f"Expected: {expected_pl}, Got: {result.get('profit_loss', 0)}")
            return result
        return None

    def test_get_ipos(self):
        """Test fetching all IPOs"""
        return self.run_test("Get All IPOs", "GET", "ipos", 200)

    def test_filter_ipos_by_account(self, account_id):
        """Test filtering IPOs by account"""
        params = {"demat_account_id": account_id}
        return self.run_test("Filter IPOs by Account", "GET", "ipos", 200, params=params)

    def test_update_ipo(self, ipo_id):
        """Test updating an IPO"""
        update_data = {
            "ipo_name": "Updated Test IPO",
            "listing_price": 700.0
        }
        result = self.run_test("Update IPO", "PUT", f"ipos/{ipo_id}", 200, update_data)
        
        # Verify P&L recalculation after update
        if result:
            # Assuming original application_price was 500 and allotment_quantity was 50
            # New P&L should be (700 - 500) * 50 = 10000
            expected_pl = 200.0 * 50  # (700 - 500) * 50
            if abs(result.get('profit_loss', 0) - expected_pl) < 0.01:
                self.log_test("P&L Recalculation After Update", True)
            else:
                self.log_test("P&L Recalculation After Update", False, 
                            f"Expected: {expected_pl}, Got: {result.get('profit_loss', 0)}")
        return result

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        result = self.run_test("Dashboard Stats", "GET", "dashboard/stats", 200)
        
        if result:
            # Verify required fields are present
            required_fields = ['total_invested', 'total_returns', 'total_pl', 'active_ipos', 'win_rate', 'accounts_with_pl', 'recent_ipos']
            missing_fields = [field for field in required_fields if field not in result]
            
            if not missing_fields:
                self.log_test("Dashboard Stats Structure", True)
            else:
                self.log_test("Dashboard Stats Structure", False, f"Missing fields: {missing_fields}")
                
            # Verify data types
            if isinstance(result.get('total_invested'), (int, float)) and \
               isinstance(result.get('total_returns'), (int, float)) and \
               isinstance(result.get('total_pl'), (int, float)) and \
               isinstance(result.get('active_ipos'), int) and \
               isinstance(result.get('win_rate'), (int, float)):
                self.log_test("Dashboard Stats Data Types", True)
            else:
                self.log_test("Dashboard Stats Data Types", False, "Invalid data types in response")
        
        return result

    def test_delete_ipo(self, ipo_id):
        """Test deleting an IPO"""
        return self.run_test("Delete IPO", "DELETE", f"ipos/{ipo_id}", 200)

    def test_delete_account(self, account_id):
        """Test deleting an account"""
        return self.run_test("Delete Account", "DELETE", f"accounts/{account_id}", 200)

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        # Test 404 for non-existent account
        self.run_test("404 for Non-existent Account", "GET", "accounts/invalid-id", 404)
        
        # Test 404 for non-existent IPO
        self.run_test("404 for Non-existent IPO", "GET", "ipos/invalid-id", 404)
        
        # Test validation error for incomplete data
        incomplete_account = {"account_name": "Test"}  # Missing broker_name
        self.run_test("Validation Error - Incomplete Account", "POST", "accounts", 422, incomplete_account)

    def cleanup(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete created IPOs
        for ipo_id in self.created_ipos:
            try:
                requests.delete(f"{self.api_url}/ipos/{ipo_id}")
                print(f"Deleted IPO: {ipo_id}")
            except:
                pass
        
        # Delete created accounts
        for account_id in self.created_accounts:
            try:
                requests.delete(f"{self.api_url}/accounts/{account_id}")
                print(f"Deleted Account: {account_id}")
            except:
                pass

    def run_all_tests(self):
        """Run comprehensive API test suite"""
        print(f"🚀 Starting IPO Tracker API Tests")
        print(f"Base URL: {self.base_url}")
        print("=" * 60)

        # Test basic connectivity
        self.test_root_endpoint()

        # Test account management
        account = self.test_create_account()
        if account:
            account_id = account['id']
            self.test_get_accounts()
            self.test_update_account(account_id)

            # Test IPO management
            ipo = self.test_create_ipo(account_id)
            if ipo:
                ipo_id = ipo['id']
                self.test_get_ipos()
                self.test_filter_ipos_by_account(account_id)
                self.test_update_ipo(ipo_id)
                
                # Test dashboard after creating data
                self.test_dashboard_stats()
                
                # Test deletion
                self.test_delete_ipo(ipo_id)
            
            self.test_delete_account(account_id)

        # Test error handling
        self.test_error_handling()

        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("❌ Some tests failed!")
            failed_tests = [test for test in self.test_results if not test['success']]
            print("\nFailed Tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
            return 1

def main():
    tester = IPOTrackerAPITester()
    try:
        result = tester.run_all_tests()
        return result
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())