#!/usr/bin/env python3
"""
CLI tool for checking and applying updates manually.
Usage: python -m autoupdate.cli.check_updates [options]
"""

import argparse
import sys
import os
from autoupdate import AutoUpdateService, AutoUpdateConfig


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="AutoUpdate CLI - Check and apply updates manually",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m autoupdate.cli.check_updates                    # Check for updates
  python -m autoupdate.cli.check_updates --apply           # Check and apply updates
  python -m autoupdate.cli.check_updates --config config.json --verbose

Configuration:
The tool looks for configuration in this order:
1. Configuration file specified with --config
2. Environment variables (AUTOUPDATE_*)
3. Default configuration

Environment Variables:
  AUTOUPDATE_GITHUB_OWNER          GitHub repository owner
  AUTOUPDATE_GITHUB_REPO           GitHub repository name
  AUTOUPDATE_PRODUCTION_BRANCH     Production branch (default: main)
  AUTOUPDATE_DEVELOPMENT_BRANCH    Development branch (default: main)
  AUTOUPDATE_USER_DATA_PATHS       Comma-separated user data paths
  AUTOUPDATE_VERSION_FILE_PATH     Path to version.json (default: version.json)
  AUTOUPDATE_BACKUP_DIRECTORY      Backup directory (default: backup/)
  AUTOUPDATE_HTTP_TIMEOUT          HTTP timeout in seconds (default: 30)
  AUTOUPDATE_ENABLE_LOGGING        Enable logging (default: true)
        """
    )

    parser.add_argument(
        '-c', '--check',
        action='store_true',
        help='Check for available updates (default action)'
    )

    parser.add_argument(
        '-a', '--apply',
        action='store_true',
        help='Apply available updates'
    )

    parser.add_argument(
        '-f', '--config',
        help='Path to configuration file'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    return parser


def load_config(config_path=None):
    """
    Load configuration from various sources.

    Args:
        config_path: Path to config file

    Returns:
        AutoUpdateConfig instance
    """
    if config_path:
        try:
            config = AutoUpdateConfig.from_file(config_path)
            print(f"✓ Loaded configuration from: {config_path}")
            return config
        except Exception as e:
            print(f"✗ Failed to load config file: {e}")
            sys.exit(1)

    # Try environment variables
    config = AutoUpdateConfig.from_environment()
    errors = config.validate()

    if errors:
        print("⚠ Configuration loaded from environment variables with errors:")
        for error in errors:
            print(f"  - {error}")
        print("Using default configuration...")

    return config


def main():
    """Main CLI function."""
    parser = create_parser()
    args = parser.parse_args()

    # Default action is check
    if not args.check and not args.apply:
        args.check = True

    try:
        # Load configuration
        config = load_config(args.config)

        # Validate configuration
        errors = config.validate()
        if errors:
            print("✗ Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)

        print(f"🔍 Checking updates for: {config.github_owner}/{config.github_repo}")
        print(f"📦 Production branch: {config.production_branch}")

        # Create update service
        update_service = AutoUpdateService(config)

        if args.check:
            print("\n🔍 Checking for updates...")
            result = update_service.check_for_updates()

            if result.has_update:
                print("✅ Update available!")
                print(f"   Current version: {result.current_version.version}")
                print(f"   New version: {result.new_version.version}")
                if result.release_notes:
                    print(f"   Release notes: {result.release_notes}")

                if not args.apply:
                    print("\n💡 Use --apply flag to install the update")
            else:
                print("✅ Your application is up to date")
                print(f"   Current version: {result.current_version.version}")

            if args.apply and result.has_update:
                print("\n⬇️ Applying update...")
                update_result = update_service.apply_update()

                if update_result.is_success:
                    print("✅ Update applied successfully!")
                    print(f"   New version: {update_result.updated_version.version}")
                else:
                    print(f"✗ Update failed: {update_result.error_message}")
                    sys.exit(1)

        elif args.apply:
            print("\n⬇️ Applying update...")
            result = update_service.apply_update()

            if result.is_success:
                print("✅ Update applied successfully!")
                print(f"   New version: {result.updated_version.version}")
            else:
                print(f"✗ Update failed: {result.error_message}")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
