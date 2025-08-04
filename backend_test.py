#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Fragrance Discounter Search Engine
Tests all endpoints and functionality as specified in test_result.md
"""

import requests
import json
import sys
from typing import Dict, List, Any
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://5c6aec5a-390b-4344-beee-6955c52e6a75.preview.emergentagent.com/api"

class FragranceAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
        if not success:
            self.failed_tests.append(test_name)
    
    def make_request(self, endpoint: str, params: Dict = None) -> tuple:
        """Make HTTP request and return response and success status"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            return response, True
        except Exception as e:
            return str(e), False
    
    def test_health_check(self):
        """Test health check endpoint"""
        print("\n=== Testing Health Check ===")
        response, success = self.make_request("/health")
        
        if not success:
            self.log_test("Health Check", False, f"Request failed: {response}")
            return
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                self.log_test("Health Check", True, "Service is healthy")
            else:
                self.log_test("Health Check", False, f"Unexpected response: {data}")
        else:
            self.log_test("Health Check", False, f"Status code: {response.status_code}")
    
    def test_get_all_fragrances(self):
        """Test getting all fragrances"""
        print("\n=== Testing Get All Fragrances ===")
        response, success = self.make_request("/fragrances")
        
        if not success:
            self.log_test("Get All Fragrances", False, f"Request failed: {response}")
            return
        
        if response.status_code == 200:
            fragrances = response.json()
            if isinstance(fragrances, list) and len(fragrances) == 6:
                # Check if we have expected fragrances
                fragrance_names = [f.get("name") for f in fragrances]
                expected_names = ["Bleu de Chanel", "Miss Dior", "Sauvage", "Black Opium", "Acqua di Gio", "Coco Mademoiselle"]
                
                if all(name in fragrance_names for name in expected_names):
                    self.log_test("Get All Fragrances", True, f"Retrieved {len(fragrances)} fragrances correctly")
                else:
                    self.log_test("Get All Fragrances", False, f"Missing expected fragrances. Got: {fragrance_names}")
            else:
                self.log_test("Get All Fragrances", False, f"Expected 6 fragrances, got {len(fragrances) if isinstance(fragrances, list) else 'non-list'}")
        else:
            self.log_test("Get All Fragrances", False, f"Status code: {response.status_code}")
    
    def test_get_specific_fragrance(self):
        """Test getting specific fragrance with price comparison"""
        print("\n=== Testing Get Specific Fragrance ===")
        
        # Test with Bleu de Chanel (f1)
        response, success = self.make_request("/fragrances/f1")
        
        if not success:
            self.log_test("Get Specific Fragrance", False, f"Request failed: {response}")
            return
        
        if response.status_code == 200:
            data = response.json()
            if "fragrance" in data and "price_comparison" in data:
                fragrance = data["fragrance"]
                prices = data["price_comparison"]
                
                if fragrance.get("name") == "Bleu de Chanel" and len(prices) >= 3:
                    self.log_test("Get Specific Fragrance", True, f"Retrieved fragrance with {len(prices)} price comparisons")
                else:
                    self.log_test("Get Specific Fragrance", False, f"Incorrect fragrance data or price count")
            else:
                self.log_test("Get Specific Fragrance", False, "Missing fragrance or price_comparison fields")
        else:
            self.log_test("Get Specific Fragrance", False, f"Status code: {response.status_code}")
        
        # Test with invalid ID
        response, success = self.make_request("/fragrances/invalid_id")
        if success and response.status_code == 404:
            self.log_test("Get Specific Fragrance - Invalid ID", True, "Correctly returned 404 for invalid ID")
        else:
            self.log_test("Get Specific Fragrance - Invalid ID", False, "Should return 404 for invalid ID")
    
    def test_get_discounters(self):
        """Test getting all discounters"""
        print("\n=== Testing Get Discounters ===")
        response, success = self.make_request("/discounters")
        
        if not success:
            self.log_test("Get Discounters", False, f"Request failed: {response}")
            return
        
        if response.status_code == 200:
            discounters = response.json()
            if isinstance(discounters, list) and len(discounters) == 4:
                discounter_names = [d.get("name") for d in discounters]
                expected_names = ["FragranceX", "FragranceNet", "Jomashop", "Perfume.com"]
                
                if all(name in discounter_names for name in expected_names):
                    self.log_test("Get Discounters", True, f"Retrieved {len(discounters)} discounters correctly")
                else:
                    self.log_test("Get Discounters", False, f"Missing expected discounters. Got: {discounter_names}")
            else:
                self.log_test("Get Discounters", False, f"Expected 4 discounters, got {len(discounters) if isinstance(discounters, list) else 'non-list'}")
        else:
            self.log_test("Get Discounters", False, f"Status code: {response.status_code}")
    
    def test_get_brands(self):
        """Test getting all brands"""
        print("\n=== Testing Get Brands ===")
        response, success = self.make_request("/brands")
        
        if not success:
            self.log_test("Get Brands", False, f"Request failed: {response}")
            return
        
        if response.status_code == 200:
            brands = response.json()
            expected_brands = ["Chanel", "Dior", "Giorgio Armani", "Yves Saint Laurent"]
            
            if isinstance(brands, list) and all(brand in brands for brand in expected_brands):
                self.log_test("Get Brands", True, f"Retrieved brands correctly: {brands}")
            else:
                self.log_test("Get Brands", False, f"Missing expected brands. Got: {brands}")
        else:
            self.log_test("Get Brands", False, f"Status code: {response.status_code}")
    
    def test_get_popular_fragrances(self):
        """Test getting popular fragrances"""
        print("\n=== Testing Get Popular Fragrances ===")
        response, success = self.make_request("/popular")
        
        if not success:
            self.log_test("Get Popular Fragrances", False, f"Request failed: {response}")
            return
        
        if response.status_code == 200:
            popular = response.json()
            if isinstance(popular, list) and len(popular) > 0:
                # Check structure of first item
                first_item = popular[0]
                if "fragrance" in first_item and "lowest_price" in first_item and "discounter_count" in first_item:
                    self.log_test("Get Popular Fragrances", True, f"Retrieved {len(popular)} popular fragrances")
                else:
                    self.log_test("Get Popular Fragrances", False, "Incorrect response structure")
            else:
                self.log_test("Get Popular Fragrances", False, "No popular fragrances returned")
        else:
            self.log_test("Get Popular Fragrances", False, f"Status code: {response.status_code}")
    
    def test_get_deals(self):
        """Test getting best deals"""
        print("\n=== Testing Get Best Deals ===")
        response, success = self.make_request("/deals")
        
        if not success:
            self.log_test("Get Best Deals", False, f"Request failed: {response}")
            return
        
        if response.status_code == 200:
            deals = response.json()
            if isinstance(deals, list) and len(deals) > 0:
                # Check structure of first item
                first_deal = deals[0]
                if "fragrance" in first_deal and "best_price" in first_deal and "discounter" in first_deal:
                    # Check if deals are sorted by discount percentage
                    discount_percentages = [deal["best_price"].get("discount_percentage", 0) for deal in deals]
                    is_sorted = all(discount_percentages[i] >= discount_percentages[i+1] for i in range(len(discount_percentages)-1))
                    
                    if is_sorted:
                        self.log_test("Get Best Deals", True, f"Retrieved {len(deals)} deals, properly sorted by discount")
                    else:
                        self.log_test("Get Best Deals", False, "Deals not properly sorted by discount percentage")
                else:
                    self.log_test("Get Best Deals", False, "Incorrect response structure")
            else:
                self.log_test("Get Best Deals", False, "No deals returned")
        else:
            self.log_test("Get Best Deals", False, f"Status code: {response.status_code}")
    
    def test_basic_search(self):
        """Test basic search functionality"""
        print("\n=== Testing Basic Search ===")
        
        # Test search for "Chanel"
        response, success = self.make_request("/search", {"query": "Chanel"})
        
        if not success:
            self.log_test("Basic Search - Chanel", False, f"Request failed: {response}")
            return
        
        if response.status_code == 200:
            data = response.json()
            if "results" in data and "total_count" in data:
                results = data["results"]
                if len(results) == 2:  # Should return Bleu de Chanel and Coco Mademoiselle
                    fragrance_names = [r["fragrance"]["name"] for r in results]
                    if "Bleu de Chanel" in fragrance_names and "Coco Mademoiselle" in fragrance_names:
                        self.log_test("Basic Search - Chanel", True, f"Found {len(results)} Chanel fragrances")
                    else:
                        self.log_test("Basic Search - Chanel", False, f"Incorrect fragrances returned: {fragrance_names}")
                else:
                    self.log_test("Basic Search - Chanel", False, f"Expected 2 results, got {len(results)}")
            else:
                self.log_test("Basic Search - Chanel", False, "Missing results or total_count in response")
        else:
            self.log_test("Basic Search - Chanel", False, f"Status code: {response.status_code}")
    
    def test_gender_filter(self):
        """Test gender filtering"""
        print("\n=== Testing Gender Filter ===")
        
        # Test Men's fragrances
        response, success = self.make_request("/search", {"gender": "Men"})
        
        if not success:
            self.log_test("Gender Filter - Men", False, f"Request failed: {response}")
            return
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            # Should return Bleu de Chanel, Sauvage, and Acqua di Gio
            if len(results) == 3:
                all_men = all(r["fragrance"]["gender"] == "Men" for r in results)
                if all_men:
                    self.log_test("Gender Filter - Men", True, f"Found {len(results)} men's fragrances")
                else:
                    self.log_test("Gender Filter - Men", False, "Some results are not men's fragrances")
            else:
                self.log_test("Gender Filter - Men", False, f"Expected 3 men's fragrances, got {len(results)}")
        else:
            self.log_test("Gender Filter - Men", False, f"Status code: {response.status_code}")
        
        # Test Women's fragrances
        response, success = self.make_request("/search", {"gender": "Women"})
        
        if success and response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            # Should return Miss Dior, Black Opium, and Coco Mademoiselle
            if len(results) == 3:
                all_women = all(r["fragrance"]["gender"] == "Women" for r in results)
                if all_women:
                    self.log_test("Gender Filter - Women", True, f"Found {len(results)} women's fragrances")
                else:
                    self.log_test("Gender Filter - Women", False, "Some results are not women's fragrances")
            else:
                self.log_test("Gender Filter - Women", False, f"Expected 3 women's fragrances, got {len(results)}")
        else:
            self.log_test("Gender Filter - Women", False, "Failed to get women's fragrances")
    
    def test_brand_filter(self):
        """Test brand filtering"""
        print("\n=== Testing Brand Filter ===")
        
        # Test Dior brand
        response, success = self.make_request("/search", {"brand": "Dior"})
        
        if not success:
            self.log_test("Brand Filter - Dior", False, f"Request failed: {response}")
            return
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            # Should return Miss Dior and Sauvage
            if len(results) == 2:
                all_dior = all(r["fragrance"]["brand"] == "Dior" for r in results)
                if all_dior:
                    fragrance_names = [r["fragrance"]["name"] for r in results]
                    if "Miss Dior" in fragrance_names and "Sauvage" in fragrance_names:
                        self.log_test("Brand Filter - Dior", True, f"Found {len(results)} Dior fragrances")
                    else:
                        self.log_test("Brand Filter - Dior", False, f"Incorrect Dior fragrances: {fragrance_names}")
                else:
                    self.log_test("Brand Filter - Dior", False, "Some results are not Dior fragrances")
            else:
                self.log_test("Brand Filter - Dior", False, f"Expected 2 Dior fragrances, got {len(results)}")
        else:
            self.log_test("Brand Filter - Dior", False, f"Status code: {response.status_code}")
    
    def test_price_filter(self):
        """Test price range filtering"""
        print("\n=== Testing Price Filter ===")
        
        # Test price range $50-$80
        response, success = self.make_request("/search", {"min_price": 50, "max_price": 80})
        
        if not success:
            self.log_test("Price Filter", False, f"Request failed: {response}")
            return
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if len(results) > 0:
                # Check if all results have prices within range
                valid_prices = True
                for result in results:
                    if result["lowest_price"] > 80 or result["highest_price"] < 50:
                        valid_prices = False
                        break
                
                if valid_prices:
                    self.log_test("Price Filter", True, f"Found {len(results)} fragrances in price range $50-$80")
                else:
                    self.log_test("Price Filter", False, "Some results are outside the price range")
            else:
                self.log_test("Price Filter", False, "No results found in price range")
        else:
            self.log_test("Price Filter", False, f"Status code: {response.status_code}")
    
    def test_sorting(self):
        """Test sorting functionality"""
        print("\n=== Testing Sorting ===")
        
        # Test price ascending sort
        response, success = self.make_request("/search", {"sort_by": "price_asc"})
        
        if not success:
            self.log_test("Sort by Price Ascending", False, f"Request failed: {response}")
            return
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if len(results) > 1:
                prices = [r["lowest_price"] for r in results]
                is_sorted = all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
                
                if is_sorted:
                    self.log_test("Sort by Price Ascending", True, f"Results properly sorted by price: {prices}")
                else:
                    self.log_test("Sort by Price Ascending", False, f"Results not properly sorted: {prices}")
            else:
                self.log_test("Sort by Price Ascending", False, "Not enough results to test sorting")
        else:
            self.log_test("Sort by Price Ascending", False, f"Status code: {response.status_code}")
        
        # Test name ascending sort
        response, success = self.make_request("/search", {"sort_by": "name_asc"})
        
        if success and response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if len(results) > 1:
                names = [r["fragrance"]["name"] for r in results]
                is_sorted = all(names[i] <= names[i+1] for i in range(len(names)-1))
                
                if is_sorted:
                    self.log_test("Sort by Name Ascending", True, f"Results properly sorted by name")
                else:
                    self.log_test("Sort by Name Ascending", False, f"Results not properly sorted by name: {names}")
            else:
                self.log_test("Sort by Name Ascending", False, "Not enough results to test sorting")
        else:
            self.log_test("Sort by Name Ascending", False, "Failed to test name sorting")
    
    def test_pagination(self):
        """Test pagination functionality"""
        print("\n=== Testing Pagination ===")
        
        # Test with limit=2, offset=0
        response, success = self.make_request("/search", {"limit": 2, "offset": 0})
        
        if not success:
            self.log_test("Pagination - First Page", False, f"Request failed: {response}")
            return
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            total_count = data.get("total_count", 0)
            
            if len(results) == 2 and total_count >= 6:
                self.log_test("Pagination - First Page", True, f"Got {len(results)} results, total: {total_count}")
                
                # Test second page
                response2, success2 = self.make_request("/search", {"limit": 2, "offset": 2})
                
                if success2 and response2.status_code == 200:
                    data2 = response2.json()
                    results2 = data2.get("results", [])
                    
                    # Check that results are different
                    first_page_ids = [r["fragrance"]["id"] for r in results]
                    second_page_ids = [r["fragrance"]["id"] for r in results2]
                    
                    if not any(id in first_page_ids for id in second_page_ids):
                        self.log_test("Pagination - Second Page", True, "Second page has different results")
                    else:
                        self.log_test("Pagination - Second Page", False, "Second page has overlapping results")
                else:
                    self.log_test("Pagination - Second Page", False, "Failed to get second page")
            else:
                self.log_test("Pagination - First Page", False, f"Expected 2 results, got {len(results)}")
        else:
            self.log_test("Pagination - First Page", False, f"Status code: {response.status_code}")
    
    def test_combined_filters(self):
        """Test combining multiple filters"""
        print("\n=== Testing Combined Filters ===")
        
        # Test brand + gender filter
        response, success = self.make_request("/search", {"brand": "Chanel", "gender": "Women"})
        
        if not success:
            self.log_test("Combined Filters", False, f"Request failed: {response}")
            return
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            # Should return only Coco Mademoiselle
            if len(results) == 1:
                result = results[0]
                if (result["fragrance"]["brand"] == "Chanel" and 
                    result["fragrance"]["gender"] == "Women" and
                    result["fragrance"]["name"] == "Coco Mademoiselle"):
                    self.log_test("Combined Filters", True, "Correctly filtered by brand and gender")
                else:
                    self.log_test("Combined Filters", False, "Incorrect result for combined filters")
            else:
                self.log_test("Combined Filters", False, f"Expected 1 result, got {len(results)}")
        else:
            self.log_test("Combined Filters", False, f"Status code: {response.status_code}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting Fragrance Discounter Search Engine API Tests")
        print(f"🔗 Testing against: {self.base_url}")
        
        # Run all test methods
        self.test_health_check()
        self.test_get_all_fragrances()
        self.test_get_specific_fragrance()
        self.test_get_discounters()
        self.test_get_brands()
        self.test_get_popular_fragrances()
        self.test_get_deals()
        self.test_basic_search()
        self.test_gender_filter()
        self.test_brand_filter()
        self.test_price_filter()
        self.test_sorting()
        self.test_pagination()
        self.test_combined_filters()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        if self.failed_tests:
            print(f"\n🚨 Failed Tests:")
            for test in self.failed_tests:
                print(f"   - {test}")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = FragranceAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Backend API is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the details above.")
        sys.exit(1)