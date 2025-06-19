#!/usr/bin/env python3
"""
Quick start script for the NCOS Predictive Engine
Runs validation, backtest, and provides next steps
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True
        )

        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Failed to run: {e}")
        return False

def main():
    print("🎯 NCOS PREDICTIVE ENGINE - QUICK START")
    print("="*60)

    # Step 1: Validate system
    if not run_command(
        "python validate_predictive.py",
        "Step 1: Validating System Components"
    ):
        print("\n⚠️  Please fix validation errors before proceeding.")
        sys.exit(1)

    # Step 2: Run backtest
    print("\n" + "="*60)
    response = input("\n📊 Run backtest analysis? (y/n): ")

    if response.lower() == 'y':
        if run_command(
            "python predictive_backtest.py",
            "Step 2: Running Backtest Analysis"
        ):
            print("\n✅ Backtest complete!")
            print("\n📁 Generated files:")
            print("  - predictive_backtest_results.json")
            print("  - predictive_trades_log.csv")
            print("  - predictive_backtest_analysis.png")

    # Step 3: Next steps
    print("\n" + "="*60)
    print("🎯 NEXT STEPS")
    print("="*60)
    print("\n1. Review Results:")
    print("   - Check predictive_backtest_results.json for metrics")
    print("   - View predictive_backtest_analysis.png for charts")

    print("\n2. Launch Dashboard (requires streamlit):")
    print("   streamlit run grade_analysis_dashboard.py")

    print("\n3. Test Individual Components:")
    print("   python test_predictive_engine.py")

    print("\n4. Start Live Trading:")
    print("   python ncos_master_orchestrator.py")

    print("\n5. Read Documentation:")
    print("   - PREDICTIVE_ENGINE_GUIDE.md")
    print("   - config/predictive_engine_config.yaml")

    print("\n✨ The Predictive Engine is ready to enhance your trading!")

if __name__ == "__main__":
    main()
