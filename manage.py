#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def run_preflight_checks():
    """
    Auto collect static, identify system issues, and verify tests before launching runserver.
    Only runs once in the main/parent process (not on every autoreload trigger).
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

    # Prevent duplicate runs inside Django auto-reloader child process
    if os.environ.get('RUN_MAIN') == 'true':
        return

    # If asking for help, bypass preflight checks immediately
    if '--help' in sys.argv or '-h' in sys.argv or 'help' in sys.argv:
        return

    # Check if user explicitly passed --skip-preflight
    if '--skip-preflight' in sys.argv:
        sys.argv.remove('--skip-preflight')
        return

    print("\n" + "=" * 65)
    print(" 🚀 [Royal Palace EMS] Running Pre-Flight Diagnostics & Build")
    print("=" * 65)

    try:
        import django
        django.setup()
        from django.core.management import call_command

        # 1. System Check
        print(" [1/3] 🔍 Checking System Integrity & Identifying Issues...")
        call_command('check', verbosity=1)
        print("  ✓ System check passed (0 issues).")

        # 2. Auto Collect Static
        print("\n [2/3] 📦 Auto-Collecting & Synchronizing Static Assets...")
        call_command('collectstatic', interactive=False, verbosity=1)
        print("  ✓ Static files synchronized successfully.")

        # 3. Verify Test Suite
        print("\n [3/3] 🧪 Verifying Automated Test Suite (24 tests)...")
        call_command('test', verbosity=1)
        print("  ✓ All automated tests passed successfully.")

        print("\n" + "=" * 65)
        print(" ✨ Pre-Flight Validation Succeeded! Starting Development Server...")
        print("=" * 65 + "\n")

    except SystemExit as se:
        if se.code != 0:
            print("\n❌ [Pre-Flight Warning] Test or check returned non-zero exit code.")
            sys.exit(se.code)
    except Exception as e:
        print(f"\n❌ [Pre-Flight Error] Diagnostics failed: {e}\n")
        sys.exit(1)


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

    # Run preflight diagnostics when runserver is executed
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        run_preflight_checks()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
