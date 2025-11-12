#!/usr/bin/env python3
"""
Basic usage example for AutoUpdate Python library.
"""

from autoupdate import AutoUpdateService, AutoUpdateConfig


def main():
    """Main example function."""
    # Configure for AI-Online-Radio project
    config = AutoUpdateConfig(
        github_owner='your-github-username',
        github_repo='AI-Online-Radio',
        production_branch='user-branch',  # Only this branch is checked!
        development_branch='main-dev',    # Ignored for updates
        user_data_paths=['data/', 'uploads/', 'config/'],
        version_file_path='version.json'
    )

    # Create update service
    update_service = AutoUpdateService(config)

    print("🔍 Checking for updates...")
    result = update_service.check_for_updates()

    if result.has_update:
        print("✅ Update available!")
        print(f"   Current version: {result.current_version.version}")
        print(f"   New version: {result.new_version.version}")
        if result.release_notes:
            print(f"   Release notes: {result.release_notes}")

        # Ask user if they want to apply the update
        response = input("\nDo you want to apply the update? (y/N): ").strip().lower()
        if response == 'y':
            print("\n⬇️ Applying update...")
            update_result = update_service.apply_update()

            if update_result.is_success:
                print("✅ Update applied successfully!")
                print(f"   New version: {update_result.updated_version.version}")
            else:
                print(f"✗ Update failed: {update_result.error_message}")
        else:
            print("Update cancelled.")
    else:
        print("✅ Your application is up to date")
        print(f"   Current version: {result.current_version.version}")


if __name__ == "__main__":
    main()
