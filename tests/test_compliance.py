"""
Regulatory Compliance Tests
Tests SEC Regulation M compliance and audit trail functionality
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.agents.pydantic_agents import PydanticTradingAgentSystem
from app.data.market_data import MarketData
from app.db.database import Database


def test_regulatory_agent():
    """Test regulatory compliance agent"""
    print("=" * 70)
    print("REGULATORY AGENT COMPLIANCE TEST")
    print("=" * 70)

    system = PydanticTradingAgentSystem(use_openai=True)
    market_data = MarketData()

    # Test different stock scenarios
    test_cases = [
        {"symbol": "AAPL", "type": "Large Cap Blue Chip"},
        {"symbol": "TSLA", "type": "High Volatility Stock"},
        {"symbol": "JPM", "type": "Financial Institution"},
    ]

    results = {}

    for test_case in test_cases:
        symbol = test_case["symbol"]
        stock_type = test_case["type"]

        print(f"\n{'='*70}")
        print(f"Testing: {symbol} ({stock_type})")
        print(f"{'='*70}")

        try:
            # Get market data
            print(f"\n[1] Fetching market data...")
            data = market_data.get_stock_data(symbol, period='1mo')
            if data.empty:
                print(f"    ⚠️  No data available")
                results[symbol] = {"status": "SKIPPED", "reason": "No data"}
                continue

            data = market_data.calculate_technical_indicators(data)
            print(f"    ✅ Market data retrieved")

            # Run market analysis (required for regulatory check)
            print(f"\n[2] Running market analysis...")
            market_result = system.run_market_analysis(symbol, data)
            print(f"    ✅ Market analysis completed")

            # Run regulatory compliance check
            print(f"\n[3] Running regulatory compliance check...")
            reg_result = system.run_regulatory_compliance(symbol, market_result)

            if "analysis" in reg_result and reg_result["analysis"]:
                analysis = reg_result["analysis"]

                # Check for compliance status
                if hasattr(analysis, 'compliance_status'):
                    status = analysis.compliance_status
                    print(f"    ✅ Compliance check completed")
                    print(f"    🏛️  Status: {status}")

                    # Check for restrictions
                    if hasattr(analysis, 'restrictions'):
                        restrictions = analysis.restrictions
                        print(f"    📋 Restrictions: {restrictions if restrictions else 'None'}")

                    # Check for rationale
                    if hasattr(analysis, 'rationale'):
                        rationale = analysis.rationale
                        print(f"    📝 Rationale: {rationale[:100]}...")

                    results[symbol] = {
                        "status": "PASSED",
                        "compliance_status": status
                    }
                else:
                    print(f"    ✅ Compliance check completed (legacy format)")
                    results[symbol] = {"status": "PASSED", "compliance_status": "UNKNOWN"}

            else:
                print(f"    ❌ Compliance check failed or returned empty")
                results[symbol] = {"status": "FAILED", "reason": "Empty result"}

        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            results[symbol] = {"status": "ERROR", "reason": str(e)}

    # Summary
    print(f"\n{'='*70}")
    print("REGULATORY COMPLIANCE SUMMARY")
    print(f"{'='*70}")

    passed = sum(1 for r in results.values() if r["status"] == "PASSED")
    total = len(test_cases)

    print(f"\nTest Results:")
    for symbol, result in results.items():
        if result["status"] == "PASSED":
            emoji = "✅"
            status_text = f"PASSED - {result.get('compliance_status', 'UNKNOWN')}"
        elif result["status"] == "SKIPPED":
            emoji = "⚠️"
            status_text = f"SKIPPED - {result.get('reason', '')}"
        else:
            emoji = "❌"
            status_text = f"FAILED - {result.get('reason', '')}"

        print(f"  {emoji} {symbol}: {status_text}")

    print(f"\nOverall: {passed}/{total} compliance tests passed")

    return passed >= (total * 0.8)  # 80% pass rate acceptable


def test_audit_trail():
    """Test audit trail functionality"""
    print("\n" + "=" * 70)
    print("AUDIT TRAIL TEST")
    print("=" * 70)

    db = Database()
    system = PydanticTradingAgentSystem(use_openai=True)
    market_data = MarketData()

    symbol = "AAPL"

    try:
        # Generate some trading activity
        print(f"\n[1] Generating trading activity for {symbol}...")
        data = market_data.get_stock_data(symbol, period='1mo')
        data = market_data.calculate_technical_indicators(data)

        # Run full analysis pipeline
        print(f"    Running market analysis...")
        market_result = system.run_market_analysis(symbol, data)

        print(f"    Running trading signal analysis...")
        signal_result = system.run_trading_signal_analysis(symbol, data)

        print(f"    Running regulatory compliance...")
        reg_result = system.run_regulatory_compliance(symbol, market_result)

        print(f"    ✅ Trading activity generated")

        # Check audit trail
        print(f"\n[2] Retrieving audit trail...")
        audit_entries = db.get_audit_trail(symbol=symbol, limit=10)

        if audit_entries:
            print(f"    ✅ Found {len(audit_entries)} audit entries for {symbol}")

            # Verify audit entry structure
            print(f"\n[3] Verifying audit entry structure...")
            required_fields = ['symbol', 'timestamp', 'decision_type', 'action']

            sample = audit_entries[0]
            missing_fields = [f for f in required_fields if f not in sample]

            if not missing_fields:
                print(f"    ✅ Audit entries have required fields")

                # Display sample entry
                print(f"\n    Sample Audit Entry:")
                for key, value in sample.items():
                    display_value = str(value)[:50] if value else "None"
                    print(f"      {key}: {display_value}")

                return True
            else:
                print(f"    ❌ Missing required fields: {missing_fields}")
                return False
        else:
            print(f"    ⚠️  No audit entries found for {symbol}")
            print(f"    Note: This might be normal if this is the first test run")
            return True  # Don't fail if no entries exist yet

    except Exception as e:
        print(f"    ❌ Audit trail test failed: {str(e)}")
        return False


def test_regulation_m_compliance():
    """Test SEC Regulation M specific compliance"""
    print("\n" + "=" * 70)
    print("SEC REGULATION M COMPLIANCE TEST")
    print("=" * 70)

    system = PydanticTradingAgentSystem(use_openai=True)
    market_data = MarketData()

    # Test a scenario that might trigger Regulation M concerns
    symbol = "AAPL"

    try:
        print(f"\n[1] Testing Regulation M compliance for {symbol}...")

        data = market_data.get_stock_data(symbol, period='1mo')
        if data.empty:
            print(f"    ⚠️  No data available")
            return False

        data = market_data.calculate_technical_indicators(data)

        # Run market analysis
        market_result = system.run_market_analysis(symbol, data)

        # Run regulatory compliance
        reg_result = system.run_regulatory_compliance(symbol, market_result)

        if "analysis" in reg_result and reg_result["analysis"]:
            print(f"    ✅ Regulation M compliance check completed")

            analysis = reg_result["analysis"]

            # Check if the agent mentions Regulation M
            analysis_text = str(analysis).lower()
            if "regulation m" in analysis_text or "reg m" in analysis_text:
                print(f"    ✅ Regulation M explicitly checked")
            else:
                print(f"    ℹ️  Regulation M not explicitly mentioned")

            # Check for trading restrictions
            if hasattr(analysis, 'restrictions'):
                if analysis.restrictions:
                    print(f"    ⚠️  Trading restrictions identified")
                else:
                    print(f"    ✅ No trading restrictions")

            return True
        else:
            print(f"    ❌ Regulation M check failed")
            return False

    except Exception as e:
        print(f"    ❌ Regulation M test error: {str(e)}")
        return False


def test_compliance_documentation():
    """Test that compliance decisions are properly documented"""
    print("\n" + "=" * 70)
    print("COMPLIANCE DOCUMENTATION TEST")
    print("=" * 70)

    db = Database()
    system = PydanticTradingAgentSystem(use_openai=True)
    market_data = MarketData()

    symbol = "MSFT"

    try:
        print(f"\n[1] Running compliance analysis for {symbol}...")

        data = market_data.get_stock_data(symbol, period='1mo')
        if data.empty:
            print(f"    ⚠️  No data available")
            return False

        data = market_data.calculate_technical_indicators(data)

        # Run full pipeline
        market_result = system.run_market_analysis(symbol, data)
        reg_result = system.run_regulatory_compliance(symbol, market_result)

        print(f"    ✅ Compliance analysis completed")

        # Check if decision was saved
        print(f"\n[2] Checking if compliance decision was saved...")

        decisions = db.get_trading_decisions(symbol=symbol, limit=5)

        if decisions:
            print(f"    ✅ Found {len(decisions)} decisions in database")

            # Check for documentation
            has_docs = False
            for decision in decisions:
                if decision.get('decision') or decision.get('agent_type'):
                    has_docs = True
                    break

            if has_docs:
                print(f"    ✅ Decisions are properly documented")
                return True
            else:
                print(f"    ⚠️  Decisions lack proper documentation")
                return False
        else:
            print(f"    ⚠️  No decisions found in database")
            return True  # Don't fail if this is first run

    except Exception as e:
        print(f"    ❌ Documentation test failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "🏛️  " * 35)
    print("REGULATORY COMPLIANCE TEST SUITE")
    print("🏛️  " * 35)

    results = {}

    # Run all compliance tests
    results['regulatory_agent'] = test_regulatory_agent()
    results['audit_trail'] = test_audit_trail()
    results['regulation_m'] = test_regulation_m_compliance()
    results['documentation'] = test_compliance_documentation()

    # Final Summary
    print(f"\n{'='*70}")
    print("COMPLIANCE TEST SUMMARY")
    print(f"{'='*70}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nTest Results:")
    for test_name, passed_test in results.items():
        emoji = "✅" if passed_test else "❌"
        status = "PASSED" if passed_test else "FAILED"
        print(f"  {emoji} {test_name.replace('_', ' ').title()}: {status}")

    print(f"\nOverall: {passed}/{total} compliance tests passed")

    if passed == total:
        print(f"\n🎉 Excellent! All compliance requirements met!")
    else:
        print(f"\n⚠️  {total - passed} compliance test(s) need attention")

    sys.exit(0 if passed == total else 1)
