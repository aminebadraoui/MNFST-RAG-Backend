#!/usr/bin/env python3
"""
Command-line script to create a superadmin user
"""
import argparse
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.seeding import DatabaseSeeder
from app.config import settings


def create_superadmin(email: str, password: str, name: str):
    """
    Create a superadmin user with the provided credentials
    
    Args:
        email: Superadmin email
        password: Superadmin password
        name: Superadmin display name
    """
    print(f"Creating superadmin user with email: {email}")
    
    # Initialize the database seeder
    seeder = DatabaseSeeder()
    
    # Create the superadmin user
    success = seeder.create_superadmin(
        email=email,
        password=password,
        name=name
    )
    
    if success:
        print("✅ Superadmin user created successfully!")
        print(f"   Email: {email}")
        print(f"   Name: {name}")
        print(f"   Role: SUPERADMIN")
    else:
        print("❌ Failed to create superadmin user")
        sys.exit(1)


def main():
    """Main function to handle command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Create a superadmin user for MNFST-RAG"
    )
    parser.add_argument(
        "--email",
        "-e",
        required=True,
        help="Superadmin email address"
    )
    parser.add_argument(
        "--password",
        "-p",
        required=True,
        help="Superadmin password"
    )
    parser.add_argument(
        "--name",
        "-n",
        default="System Administrator",
        help="Superadmin display name (default: System Administrator)"
    )
    
    args = parser.parse_args()
    
    # Validate email format (basic check)
    if "@" not in args.email:
        print("❌ Invalid email format")
        sys.exit(1)
    
    # Validate password length
    if len(args.password) < settings.password_min_length:
        print(f"❌ Password must be at least {settings.password_min_length} characters long")
        sys.exit(1)
    
    try:
        create_superadmin(args.email, args.password, args.name)
    except Exception as e:
        print(f"❌ Error creating superadmin: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()