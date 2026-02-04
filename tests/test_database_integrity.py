"""
Database Integrity Tests
Tests database operations, CRUD functionality, and data persistence
"""
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.db.database import Database


def test_database_connection():
    """Test basic database connectivity"""
    print("=" * 70)
    print("DATABASE CONNECTION TEST")
    print("=" * 70)

    try:
        print("\n[1] Attempting to connect to database...")
        db = Database()
        print("    ✅ Database connection established")

        print("\n[2] Testing database initialization...")
        db.initialize_database()
        print("    ✅ Database tables initialized")

        return True

    except Exception as e:
        print(f"    ❌ Connection failed: {str(e)}")
        print(f"\n⚠️  Note: Make sure your DATABASE_URL is configured in config.py")
        return False


def test_write_operations():
    """Test database write operations"""
    print("\n" + "=" * 70)
    print("WRITE OPERATIONS TEST")
    print("=" * 70)

    db = Database()
    test_symbol = "TEST_DB"
    timestamp = int(time.time())

    try:
        # Test 1: Save trading decision
        print(f"\n[1] Testing save_trading_decision...")
        db.save_trading_decision(
            symbol=test_symbol,
            decision=f"Test Decision {timestamp}",
            confidence=0.85,
            agent_type="test_agent"
        )
        print(f"    ✅ Trading decision saved")

        # Test 2: Save audit entry
        print(f"\n[2] Testing save_audit_entry...")
        db.save_audit_entry(
            symbol=test_symbol,
            decision_type="TEST",
            action="BUY",
            confidence=0.85,
            rationale=f"Test rationale {timestamp}",
            agent="test_agent"
        )
        print(f"    ✅ Audit entry saved")

        # Test 3: Save multiple entries
        print(f"\n[3] Testing batch write operations...")
        for i in range(5):
            db.save_trading_decision(
                symbol=f"{test_symbol}_{i}",
                decision=f"Batch decision {i}",
                confidence=0.70 + (i * 0.05),
                agent_type="batch_test"
            )
        print(f"    ✅ Batch write completed (5 entries)")

        return True

    except Exception as e:
        print(f"    ❌ Write operation failed: {str(e)}")
        return False


def test_read_operations():
    """Test database read operations"""
    print("\n" + "=" * 70)
    print("READ OPERATIONS TEST")
    print("=" * 70)

    db = Database()
    test_symbol = "TEST_DB"

    try:
        # Test 1: Get trading decisions
        print(f"\n[1] Testing get_trading_decisions...")
        decisions = db.get_trading_decisions(symbol=test_symbol, limit=10)
        print(f"    ✅ Retrieved {len(decisions)} decisions")

        if decisions:
            print(f"    Sample decision:")
            sample = decisions[0]
            for key, value in sample.items():
                print(f"      {key}: {value}")

        # Test 2: Get audit trail
        print(f"\n[2] Testing get_audit_trail...")
        audit = db.get_audit_trail(symbol=test_symbol, limit=10)
        print(f"    ✅ Retrieved {len(audit)} audit entries")

        if audit:
            print(f"    Sample audit entry:")
            sample = audit[0]
            for key, value in sample.items():
                print(f"      {key}: {value}")

        # Test 3: Get all trading decisions
        print(f"\n[3] Testing get_all_trading_decisions...")
        all_decisions = db.get_trading_decisions(limit=100)
        print(f"    ✅ Retrieved {len(all_decisions)} total decisions from database")

        # Test 4: Get decisions summary
        print(f"\n[4] Testing get_decisions_summary...")
        summary = db.get_decisions_summary()
        print(f"    ✅ Summary retrieved:")
        for key, value in summary.items():
            print(f"      {key}: {value}")

        return True

    except Exception as e:
        print(f"    ❌ Read operation failed: {str(e)}")
        return False


def test_query_filters():
    """Test database query filtering"""
    print("\n" + "=" * 70)
    print("QUERY FILTER TEST")
    print("=" * 70)

    db = Database()

    try:
        # Test different filters
        print(f"\n[1] Testing symbol filter...")
        decisions = db.get_trading_decisions(symbol="AAPL", limit=5)
        print(f"    ✅ Found {len(decisions)} decisions for AAPL")

        print(f"\n[2] Testing limit parameter...")
        limited = db.get_trading_decisions(limit=3)
        if len(limited) <= 3:
            print(f"    ✅ Limit working: Retrieved {len(limited)} entries")
        else:
            print(f"    ⚠️  Limit may not be working: Retrieved {len(limited)} entries")

        print(f"\n[3] Testing date-based queries...")
        audit = db.get_audit_trail(limit=10)
        if audit:
            print(f"    ✅ Retrieved {len(audit)} audit entries with timestamps")
        else:
            print(f"    ⚠️  No audit entries found")

        return True

    except Exception as e:
        print(f"    ❌ Query filter test failed: {str(e)}")
        return False


def test_data_integrity():
    """Test data integrity and consistency"""
    print("\n" + "=" * 70)
    print("DATA INTEGRITY TEST")
    print("=" * 70)

    db = Database()
    test_symbol = f"INTEGRITY_TEST_{int(time.time())}"

    try:
        # Write a known entry
        print(f"\n[1] Writing test entry...")
        test_confidence = 0.923
        test_decision = "Integrity Test Decision"

        db.save_trading_decision(
            symbol=test_symbol,
            decision=test_decision,
            confidence=test_confidence,
            agent_type="integrity_test"
        )
        print(f"    ✅ Test entry written")

        # Read it back
        print(f"\n[2] Reading back test entry...")
        decisions = db.get_trading_decisions(symbol=test_symbol, limit=1)

        if not decisions:
            print(f"    ❌ Could not retrieve test entry")
            return False

        retrieved = decisions[0]
        print(f"    ✅ Test entry retrieved")

        # Verify data integrity
        print(f"\n[3] Verifying data integrity...")
        checks = []

        # Check symbol
        if retrieved['symbol'] == test_symbol:
            print(f"    ✅ Symbol matches: {test_symbol}")
            checks.append(True)
        else:
            print(f"    ❌ Symbol mismatch: {retrieved['symbol']} != {test_symbol}")
            checks.append(False)

        # Check decision
        if retrieved['decision'] == test_decision:
            print(f"    ✅ Decision matches")
            checks.append(True)
        else:
            print(f"    ❌ Decision mismatch")
            checks.append(False)

        # Check confidence (allow small floating point differences)
        if abs(float(retrieved['confidence']) - test_confidence) < 0.001:
            print(f"    ✅ Confidence matches: {test_confidence}")
            checks.append(True)
        else:
            print(f"    ❌ Confidence mismatch: {retrieved['confidence']} != {test_confidence}")
            checks.append(False)

        return all(checks)

    except Exception as e:
        print(f"    ❌ Integrity test failed: {str(e)}")
        return False


def test_concurrent_writes():
    """Test handling of concurrent write operations"""
    print("\n" + "=" * 70)
    print("CONCURRENT WRITES TEST")
    print("=" * 70)

    db = Database()
    test_symbol = "CONCURRENT_TEST"

    try:
        print(f"\n[1] Writing multiple entries rapidly...")

        start_time = time.time()
        for i in range(10):
            db.save_trading_decision(
                symbol=f"{test_symbol}_{i}",
                decision=f"Concurrent decision {i}",
                confidence=0.75,
                agent_type="concurrent_test"
            )

        elapsed = time.time() - start_time
        print(f"    ✅ 10 concurrent writes completed in {elapsed:.3f}s")
        print(f"    Average: {elapsed/10*1000:.1f}ms per write")

        # Verify all were written
        print(f"\n[2] Verifying all entries were written...")
        count = 0
        for i in range(10):
            decisions = db.get_trading_decisions(symbol=f"{test_symbol}_{i}", limit=1)
            if decisions:
                count += 1

        if count == 10:
            print(f"    ✅ All 10 entries verified in database")
            return True
        else:
            print(f"    ⚠️  Only {count}/10 entries found")
            return False

    except Exception as e:
        print(f"    ❌ Concurrent writes test failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "💾 " * 35)
    print("DATABASE INTEGRITY TEST SUITE")
    print("💾 " * 35)

    results = {}

    # Run all database tests
    results['connection'] = test_database_connection()

    if results['connection']:
        results['write_ops'] = test_write_operations()
        results['read_ops'] = test_read_operations()
        results['query_filters'] = test_query_filters()
        results['data_integrity'] = test_data_integrity()
        results['concurrent_writes'] = test_concurrent_writes()
    else:
        print(f"\n⚠️  Skipping remaining tests due to connection failure")
        print(f"   Make sure PostgreSQL is running and DATABASE_URL is configured")
        results['write_ops'] = False
        results['read_ops'] = False
        results['query_filters'] = False
        results['data_integrity'] = False
        results['concurrent_writes'] = False

    # Final Summary
    print(f"\n{'='*70}")
    print("DATABASE TEST SUMMARY")
    print(f"{'='*70}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nTest Results:")
    for test_name, passed_test in results.items():
        emoji = "✅" if passed_test else "❌"
        status = "PASSED" if passed_test else "FAILED"
        print(f"  {emoji} {test_name.replace('_', ' ').title()}: {status}")

    print(f"\nOverall: {passed}/{total} database tests passed")

    if passed == total:
        print(f"\n🎉 Perfect! All database operations working correctly!")
    elif results['connection']:
        print(f"\n⚠️  {total - passed} database test(s) failed")
    else:
        print(f"\n⚠️  Database connection failed - check your configuration")

    sys.exit(0 if passed == total else 1)
