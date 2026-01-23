#!/usr/bin/env python3
"""
Quick test script for driver work availability endpoints.
Run with: python test_work_availability.py
"""

import requests
from datetime import date, timedelta
import json

BASE_URL = "http://localhost:8000/api/v2"

# Test credentials (these should be actual JWT tokens from your auth flow)
DRIVER_JWT = "YOUR_DRIVER_JWT_TOKEN_HERE"
FLEET_OWNER_JWT = "YOUR_FLEET_OWNER_JWT_TOKEN_HERE"

def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, default=str))
    except:
        print(response.text)

def test_declare_availability():
    """Test driver declaring availability."""
    headers = {"Authorization": f"Bearer {DRIVER_JWT}"}
    
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    payload = {
        "date": tomorrow,
        "is_available": True,
        "note": "Ready for work"
    }
    
    response = requests.post(
        f"{BASE_URL}/driver/work-availability",
        json=payload,
        headers=headers
    )
    print_response("POST /driver/work-availability", response)
    return response.json().get("availability_id") if response.status_code == 201 else None

def test_list_driver_availability():
    """Test driver listing own availability."""
    headers = {"Authorization": f"Bearer {DRIVER_JWT}"}
    
    start = date.today().isoformat()
    end = (date.today() + timedelta(days=30)).isoformat()
    
    response = requests.get(
        f"{BASE_URL}/driver/work-availability",
        params={"start_date": start, "end_date": end},
        headers=headers
    )
    print_response("GET /driver/work-availability", response)

def test_declare_unavailable():
    """Test driver marking unavailable."""
    headers = {"Authorization": f"Bearer {DRIVER_JWT}"}
    
    in_two_days = (date.today() + timedelta(days=2)).isoformat()
    
    payload = {
        "date": in_two_days,
        "is_available": False,
        "note": "Doctor's appointment"
    }
    
    response = requests.post(
        f"{BASE_URL}/driver/work-availability",
        json=payload,
        headers=headers
    )
    print_response("POST /driver/work-availability (unavailable)", response)

def test_fleet_owner_view():
    """Test fleet owner viewing drivers' availability."""
    headers = {"Authorization": f"Bearer {FLEET_OWNER_JWT}"}
    
    start = date.today().isoformat()
    end = (date.today() + timedelta(days=7)).isoformat()
    
    response = requests.get(
        f"{BASE_URL}/fleet/drivers/availability",
        params={"start_date": start, "end_date": end},
        headers=headers
    )
    print_response("GET /fleet/drivers/availability", response)

def test_unauthorized_driver():
    """Test that non-JWT request fails."""
    payload = {
        "date": date.today().isoformat(),
        "is_available": True
    }
    
    response = requests.post(
        f"{BASE_URL}/driver/work-availability",
        json=payload
    )
    print_response("POST /driver/work-availability (no auth)", response)

def main():
    print("\n" + "="*60)
    print("DRIVER WORK AVAILABILITY - API TEST SUITE")
    print("="*60)
    print("\nNOTE: Replace DRIVER_JWT and FLEET_OWNER_JWT with actual tokens")
    print("To get tokens:")
    print("  1. OTP flow: POST /api/v2/auth/send-otp + POST /api/v2/auth/verify-otp")
    print("  2. Use the access_token from response")
    print("\n" + "="*60)
    
    if DRIVER_JWT == "YOUR_DRIVER_JWT_TOKEN_HERE":
        print("\n❌ ERROR: JWT tokens not configured!")
        print("\nQuick setup:")
        print("""
# Get driver token:
curl -X POST http://localhost:8000/api/v2/auth/send-otp \\
  -H "Content-Type: application/json" \\
  -d '{"phone_number": "+919876543210", "country_code": "91"}'

# Then verify:
curl -X POST http://localhost:8000/api/v2/auth/verify-otp \\
  -H "Content-Type: application/json" \\
  -d '{"phone_number": "+919876543210", "country_code": "91", "otp_code": "000000"}'

# Copy access_token to DRIVER_JWT variable
        """)
        return
    
    print("\n✓ Starting tests...\n")
    
    # Run tests
    test_unauthorized_driver()
    test_declare_availability()
    test_declare_unavailable()
    test_list_driver_availability()
    test_fleet_owner_view()
    
    print("\n" + "="*60)
    print("TESTS COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
