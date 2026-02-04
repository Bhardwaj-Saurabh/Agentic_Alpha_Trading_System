"""
Master Test Suite Runner
Runs all tests and provides comprehensive summary
"""
import sys
import os
import time
from typing import Dict, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))

# Import all test modules
from tests.test_agents import test_agent_suite
from tests.test_data_quality import test_data_quality, test_data_consistency
from tests.test_edge_cases import test_edge_cases, test_concurrent_requests
from tests.test_agent_consistency import test_agent_consistency
from tests.test_performance import (
    test_single_stock_performance,
    test_multiple_stocks_performance,
    test_api_response_times,
    test_memory_usage
)
from tests.test_database_integrity import (
    test_database_connection,
    test_write_operations,
    test_read_operations,
    test_data_integrity
)
from tests.test_compliance import (
    test_regulatory_agent,
    test_audit_trail,
    test_regulation_m_compliance
)


class TestSuiteRunner:
    """Orchestrates running all test suites"""

    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.start_time = None
        self.end_time = None

    def run_test_category(self, category_name: str, tests: Dict[str, callable]) -> Tuple[int, int]:
        """Run a category of tests and return (passed, total)"""
        print(f"\n{'='*70}")
        print(f"{category_name}")
        print(f"{'='*70}")

        category_results = {}
        passed_count = 0

        for test_name, test_func in tests.items():
            print(f"\n[{list(tests.keys()).index(test_name) + 1}/{len(tests)}] Running {test_name}...")
            print("-" * 70)

            try:
                start = time.time()
                result = test_func()
                elapsed = time.time() - start

                category_results[test_name] = {
                    "passed": result,
                    "duration": elapsed
                }

                if result:
                    passed_count += 1
                    print(f"\n✅ {test_name} PASSED ({elapsed:.2f}s)")
                else:
                    print(f"\n❌ {test_name} FAILED ({elapsed:.2f}s)")

            except Exception as e:
                elapsed = time.time() - start
                category_results[test_name] = {
                    "passed": False,
                    "duration": elapsed,
                    "error": str(e)
                }
                print(f"\n❌ {test_name} FAILED with exception: {str(e)[:100]} ({elapsed:.2f}s)")

        self.results[category_name] = category_results
        return passed_count, len(tests)

    def print_summary(self):
        """Print comprehensive test summary"""
        self.end_time = time.time()
        total_duration = self.end_time - self.start_time

        print(f"\n{'='*70}")
        print("MASTER TEST SUITE - FINAL SUMMARY")
        print(f"{'='*70}")

        # Calculate overall statistics
        total_tests = 0
        total_passed = 0
        total_failed = 0

        print(f"\n📊 RESULTS BY CATEGORY")
        print(f"{'='*70}")

        for category, tests in self.results.items():
            passed = sum(1 for t in tests.values() if t["passed"])
            total = len(tests)
            total_tests += total
            total_passed += passed
            total_failed += (total - passed)

            percentage = (passed / total * 100) if total > 0 else 0
            status = "✅" if passed == total else "⚠️" if passed > 0 else "❌"

            print(f"\n{status} {category}")
            print(f"   Passed: {passed}/{total} ({percentage:.1f}%)")

            # Show individual test results
            for test_name, result in tests.items():
                test_status = "✅" if result["passed"] else "❌"
                duration = result["duration"]
                print(f"      {test_status} {test_name} ({duration:.2f}s)")
                if not result["passed"] and "error" in result:
                    print(f"         Error: {result['error'][:80]}")

        # Overall summary
        print(f"\n{'='*70}")
        print("OVERALL SUMMARY")
        print(f"{'='*70}")

        overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0

        print(f"\n📈 Total Tests Run: {total_tests}")
        print(f"✅ Passed: {total_passed} ({overall_percentage:.1f}%)")
        print(f"❌ Failed: {total_failed}")
        print(f"⏱️  Total Duration: {total_duration:.2f}s ({total_duration/60:.1f}m)")
        print()

        # Final verdict
        if total_failed == 0:
            print("🎉 " * 35)
            print("PERFECT SCORE! ALL TESTS PASSED!")
            print("🎉 " * 35)
            print("\n✨ Your Agentic Trading System is PRODUCTION READY! ✨")
        elif overall_percentage >= 90:
            print("🌟 " * 35)
            print("EXCELLENT! 90%+ Tests Passed!")
            print("🌟 " * 35)
            print(f"\n✅ System is highly reliable. {total_failed} minor issue(s) to address.")
        elif overall_percentage >= 75:
            print("👍 " * 35)
            print("GOOD! 75%+ Tests Passed!")
            print("👍 " * 35)
            print(f"\n⚠️  System is functional. {total_failed} issue(s) need attention.")
        elif overall_percentage >= 50:
            print("⚠️  " * 35)
            print("NEEDS WORK! 50%+ Tests Passed")
            print("⚠️  " * 35)
            print(f"\n⚠️  Several issues detected. Review {total_failed} failed test(s).")
        else:
            print("❌ " * 35)
            print("CRITICAL ISSUES DETECTED!")
            print("❌ " * 35)
            print(f"\n❌ Major problems found. Review {total_failed} failed test(s) immediately.")

        print()

    def run_all_tests(self, skip_slow: bool = False):
        """Run all test suites"""
        self.start_time = time.time()

        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 15 + "AGENTIC ALPHA TRADING SYSTEM" + " " * 25 + "║")
        print("║" + " " * 20 + "MASTER TEST SUITE" + " " * 31 + "║")
        print("╚" + "═" * 68 + "╝")

        # Category 1: Agent Tests
        agent_tests = {
            "Agent Suite": test_agent_suite,
        }
        self.run_test_category("🤖 AGENT TESTS", agent_tests)

        # Category 2: Data Quality Tests
        data_tests = {
            "Data Quality": test_data_quality,
            "Data Consistency": test_data_consistency,
        }
        self.run_test_category("📊 DATA QUALITY TESTS", data_tests)

        # Category 3: Edge Case Tests
        edge_tests = {
            "Edge Cases": test_edge_cases,
            "Concurrent Requests": test_concurrent_requests,
        }
        self.run_test_category("⚠️  EDGE CASE TESTS", edge_tests)

        # Category 4: Database Tests
        db_connection_result = test_database_connection()

        if db_connection_result:
            db_tests = {
                "Database Connection": lambda: db_connection_result,
                "Write Operations": test_write_operations,
                "Read Operations": test_read_operations,
                "Data Integrity": test_data_integrity,
            }
            self.run_test_category("💾 DATABASE TESTS", db_tests)
        else:
            print(f"\n⚠️  Skipping database tests - Connection failed")
            print("   Configure DATABASE_URL in config.py to enable database tests")
            self.results["💾 DATABASE TESTS"] = {
                "Database Connection": {"passed": False, "duration": 0}
            }

        # Category 5: Compliance Tests
        compliance_tests = {
            "Regulatory Agent": test_regulatory_agent,
            "Audit Trail": test_audit_trail,
            "Regulation M": test_regulation_m_compliance,
        }
        self.run_test_category("🏛️  COMPLIANCE TESTS", compliance_tests)

        # Category 6: Performance Tests (optional if slow)
        if not skip_slow:
            performance_tests = {
                "Single Stock": test_single_stock_performance,
                "Multiple Stocks": test_multiple_stocks_performance,
                "API Response Times": test_api_response_times,
                "Memory Usage": test_memory_usage,
            }
            self.run_test_category("⚡ PERFORMANCE TESTS", performance_tests)
        else:
            print(f"\n⏭️  Skipping performance tests (use --full for complete suite)")

        # Category 7: Consistency Tests (optional if slow)
        if not skip_slow:
            consistency_tests = {
                "Agent Consistency": lambda: test_agent_consistency(runs=3),
            }
            self.run_test_category("🎯 CONSISTENCY TESTS", consistency_tests)
        else:
            print(f"\n⏭️  Skipping consistency tests (use --full for complete suite)")

        # Print final summary
        self.print_summary()

        # Return success/failure for exit code
        all_passed = all(
            all(t["passed"] for t in tests.values())
            for tests in self.results.values()
        )

        return all_passed


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run comprehensive test suite for Agentic Trading System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_tests.py              # Quick test suite (skips slow tests)
  python run_all_tests.py --full       # Full test suite (includes all tests)

Test Categories:
  🤖 Agent Tests        - Test each AI agent individually
  📊 Data Quality       - Test API data consistency
  ⚠️  Edge Cases         - Test error handling
  💾 Database          - Test database operations
  🏛️  Compliance        - Test regulatory compliance
  ⚡ Performance       - Test system performance
  🎯 Consistency       - Test agent consistency (slow)
        """
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full test suite including slow tests (recommended for CI/CD)"
    )

    args = parser.parse_args()

    runner = TestSuiteRunner()
    success = runner.run_all_tests(skip_slow=not args.full)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
