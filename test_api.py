#!/usr/bin/env python3
"""
Test client for the Vera API.

Usage:
    # In one terminal, start the API:
    python api.py

    # In another terminal, run the tests:
    python test_api.py
"""

import json
import time
import subprocess
import sys
from pathlib import Path
from urllib import request as urlrequest, error as urlerror


BASE_URL = "http://localhost:8080"
TIMEOUT = 5


def test_health():
    """Test the health endpoint."""
    try:
        req = urlrequest.Request(f"{BASE_URL}/health")
        with urlrequest.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["status"] == "healthy", f"Unexpected health status: {data}"
            print("✓ Health check passed")
            return True
    except urlerror.URLError as e:
        print(f"✗ Health check failed: {e}")
        return False


def load_sample_contexts():
    """Load sample contexts from the expanded dataset."""
    project_dir = Path(__file__).parent
    dataset_dir = project_dir / "expanded"

    if not dataset_dir.exists():
        print("⚠ No expanded dataset found. Run submission_generator.py first.")
        return None, None, None, None

    categories = {}
    for path in (dataset_dir / "categories").glob("*.json"):
        with open(path) as f:
            data = json.load(f)
            categories[data["slug"]] = data

    merchants = []
    for path in (dataset_dir / "merchants").glob("*.json"):
        with open(path) as f:
            merchants.append(json.load(f))

    customers = []
    for path in (dataset_dir / "customers").glob("*.json"):
        with open(path) as f:
            customers.append(json.load(f))

    triggers = []
    for path in (dataset_dir / "triggers").glob("*.json"):
        with open(path) as f:
            triggers.append(json.load(f))

    return list(categories.values()), merchants, customers, triggers


def test_compose():
    """Test the compose endpoint with real data."""
    categories, merchants, customers, triggers = load_sample_contexts()
    if not categories or not merchants or not triggers:
        print("✗ Could not load sample contexts")
        return False

    # Pick a sample merchant, category, and trigger
    merchant = merchants[0]
    category = next((c for c in categories if c["slug"] == merchant.get("category_slug")), categories[0])
    trigger = next((t for t in triggers if t.get("merchant_id") == merchant.get("merchant_id")), triggers[0])

    payload = {
        "category": category,
        "merchant": merchant,
        "trigger": trigger,
        "customer": None,
    }

    try:
        req = urlrequest.Request(
            f"{BASE_URL}/compose",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlrequest.urlopen(req, timeout=TIMEOUT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            assert "body" in result, "Missing 'body' in response"
            assert "cta" in result, "Missing 'cta' in response"
            assert "send_as" in result, "Missing 'send_as' in response"
            assert len(result["body"]) > 10, "Body too short"
            print(f"✓ Compose endpoint passed")
            print(f"  Message: {result['body'][:80]}...")
            print(f"  CTA: {result['cta']}")
            return True
    except urlerror.URLError as e:
        print(f"✗ Compose endpoint failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Compose test error: {e}")
        return False


def main():
    print("Testing Vera API...\n")

    # Test health
    if not test_health():
        print("API is not running. Start it with: python api.py")
        sys.exit(1)

    print()

    # Test compose
    if not test_compose():
        sys.exit(1)

    print("\n✓ All tests passed!")


if __name__ == "__main__":
    main()
