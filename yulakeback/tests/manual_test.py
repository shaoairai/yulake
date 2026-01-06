"""
手動 API 測試腳本
執行方式: python tests/manual_test.py
"""
from datetime import date, timedelta

from app import create_app, db
from app.models import Salon, Service, Stylist, SalonOwner, Customer


def run_tests():
    app = create_app()
    client = app.test_client()

    # === 公開 API 測試 ===
    print("=" * 60)
    print("1. PUBLIC API TESTS")
    print("=" * 60)

    # 1.1 Health Check
    print("[1.1] Health Check")
    r = client.get("/api/health")
    status = "✓" if r.status_code == 200 else "✗"
    print(f"  Status: {r.status_code} {status}")

    # 1.2 Get Salon Info
    print("[1.2] Get Salon Info")
    r = client.get("/api/salons/nailart")
    data = r.get_json()
    status = "✓" if data.get("success") else "✗"
    print(f"  Status: {r.status_code} {status}")
    if data.get("success"):
        print(f"    Salon: {data['data']['name']}")

    # 1.3 Get Services
    print("[1.3] Get Services")
    r = client.get("/api/salons/nailart/services")
    data = r.get_json()
    status = "✓" if data.get("success") else "✗"
    print(f"  Status: {r.status_code} {status}, Count: {len(data.get('data', []))}")

    # 1.4 Get Stylists
    print("[1.4] Get Stylists")
    r = client.get("/api/salons/nailart/stylists")
    data = r.get_json()
    status = "✓" if data.get("success") else "✗"
    print(f"  Status: {r.status_code} {status}, Count: {len(data.get('data', []))}")

    # 1.5 Get Available Slots
    print("[1.5] Get Available Slots")
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    r = client.get(
        f"/api/salons/nailart/available-slots?stylist_id=stylist_001&service_id=service_001&date={tomorrow}"
    )
    data = r.get_json()
    status = "✓" if data.get("success") else "✗"
    slots_count = (
        len(data.get("data", {}).get("slots", [])) if data.get("success") else 0
    )
    print(f"  Status: {r.status_code} {status}, Slots: {slots_count}")

    # === 認證 API 測試 ===
    print()
    print("=" * 60)
    print("2. AUTH API TESTS")
    print("=" * 60)

    # 2.1 Customer Login
    print("[2.1] Customer Login")
    r = client.post(
        "/api/auth/customer/login",
        json={"email": "wang@example.com", "password": "password123"},
    )
    data = r.get_json()
    if data.get("success"):
        customer_token = data["data"]["token"]
        print(f"  Status: {r.status_code} ✓ Token obtained")
    else:
        print(
            f"  Status: {r.status_code} ✗ {data.get('error', {}).get('message', 'Unknown error')}"
        )
        customer_token = None

    # 2.2 Salon Login
    print("[2.2] Salon Login")
    r = client.post(
        "/api/auth/salon/login",
        json={"email": "admin@nailart.com", "password": "password123"},
    )
    data = r.get_json()
    if data.get("success"):
        salon_token = data["data"]["token"]
        print(f"  Status: {r.status_code} ✓ Token obtained")
    else:
        print(
            f"  Status: {r.status_code} ✗ {data.get('error', {}).get('message', 'Unknown error')}"
        )
        salon_token = None

    # 2.3 Get Customer Me
    print("[2.3] Get Customer Me")
    if customer_token:
        r = client.get(
            "/api/auth/customer/me",
            headers={"Authorization": f"Bearer {customer_token}"},
        )
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}")
        if data.get("success"):
            print(f"    User: {data['data']['name']} ({data['data']['email']})")
    else:
        print("  Skipped - No token")

    # 2.4 Get Salon Me
    print("[2.4] Get Salon Me")
    if salon_token:
        r = client.get(
            "/api/auth/salon/me", headers={"Authorization": f"Bearer {salon_token}"}
        )
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}")
        if data.get("success"):
            d = data["data"]
            if "owner" in d:
                print(f"    Owner: {d['owner']['name']}")
                print(f"    Salon: {d['salon']['name']}")
            elif "name" in d:
                print(f"    Name: {d['name']}")
    else:
        print("  Skipped - No token")

    # === 店家後台 API 測試 ===
    print()
    print("=" * 60)
    print("3. SALON ADMIN API TESTS")
    print("=" * 60)

    if salon_token:
        headers = {"Authorization": f"Bearer {salon_token}"}

        # 3.1 Dashboard
        print("[3.1] Dashboard")
        r = client.get("/api/salon/dashboard", headers=headers)
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}")
        if data.get("success"):
            d = data["data"]
            print(
                f"    Today: {d.get('today_bookings', 0)}, Pending: {d.get('pending_bookings', 0)}, Week: {d.get('week_bookings', 0)}"
            )

        # 3.2 Get Bookings
        print("[3.2] Get Bookings")
        r = client.get("/api/salon/bookings", headers=headers)
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}, Count: {len(data.get('data', []))}")

        # 3.3 Get Services
        print("[3.3] Get Services")
        r = client.get("/api/salon/services", headers=headers)
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}, Count: {len(data.get('data', []))}")

        # 3.4 Get Stylists
        print("[3.4] Get Stylists")
        r = client.get("/api/salon/stylists", headers=headers)
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}, Count: {len(data.get('data', []))}")

        # 3.5 Get Customers
        print("[3.5] Get Customers")
        r = client.get("/api/salon/customers", headers=headers)
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}, Count: {len(data.get('data', []))}")

        # 3.6 Get Settings
        print("[3.6] Get Settings")
        r = client.get("/api/salon/settings", headers=headers)
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}")
        if data.get("success"):
            s = data["data"]
            print(f"    Salon: {s['salon']['name']}")
            print(f"    Business hours: {len(s['business_hours'])} days")
            print(f"    Slot interval: {s['booking_rule']['slot_interval']} mins")

        # 3.7 Calendar
        print("[3.7] Calendar")
        r = client.get(
            f"/api/salon/calendar?start_date={date.today()}&end_date={date.today() + timedelta(days=7)}",
            headers=headers,
        )
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}, Events: {len(data.get('data', []))}")

        # 3.8 Membership Tiers
        print("[3.8] Membership Tiers")
        r = client.get("/api/salon/membership/tiers", headers=headers)
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}, Count: {len(data.get('data', []))}")

        # 3.9 Point Rules
        print("[3.9] Point Rules")
        r = client.get("/api/salon/membership/point-rules", headers=headers)
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}")

        # 3.10 Membership Stats
        print("[3.10] Membership Stats")
        r = client.get("/api/salon/membership/stats", headers=headers)
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}")
        if data.get("success"):
            s = data["data"]
            print(f"    Total customers: {s.get('total_customers', 0)}")

        # 3.11 Email Templates
        print("[3.11] Email Templates")
        r = client.get("/api/salon/email/templates", headers=headers)
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}, Count: {len(data.get('data', []))}")

        # 3.12 Auto Email Rules
        print("[3.12] Auto Email Rules")
        r = client.get("/api/salon/email/auto-rules", headers=headers)
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}, Count: {len(data.get('data', []))}")

    else:
        print("  Skipped - No salon token")

    # === 顧客 API 測試 ===
    print()
    print("=" * 60)
    print("4. CUSTOMER API TESTS")
    print("=" * 60)

    if customer_token:
        headers = {"Authorization": f"Bearer {customer_token}"}

        # 4.1 Get My Bookings
        print("[4.1] Get My Bookings")
        r = client.get("/api/me/bookings", headers=headers)
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}, Count: {len(data.get('data', []))}")

        # 4.2 Get My Profile
        print("[4.2] Get My Profile")
        r = client.get("/api/me/profile", headers=headers)
        data = r.get_json()
        status = "✓" if data.get("success") else "✗"
        print(f"  Status: {r.status_code} {status}")
        if data.get("success"):
            p = data["data"]
            print(f"    Name: {p['name']}, Email: {p['email']}")
    else:
        print("  Skipped - No customer token")

    print()
    print("=" * 60)
    print("ALL API TESTS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
