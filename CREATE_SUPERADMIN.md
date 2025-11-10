# Creating a Superadmin User

This document explains how to use the `create_superadmin.py` script to create a superadmin user for the MNFST-RAG application.

## Prerequisites

1. Make sure you have the database configured and running
2. Ensure your environment variables are set up (especially `DATABASE_URL`)
3. Install the required dependencies:
   ```bash
   cd mnfst-rag-backend
   uv sync
   ```

## Usage

The script can be executed from the terminal with the following command:

```bash
cd mnfst-rag-backend
source .venv/bin/activate
python create_superadmin.py --email <email> --password <password> [--name <name>]
```

Alternatively, using uv:

```bash
cd mnfst-rag-backend
uv run python create_superadmin.py --email <email> --password <password> [--name <name>]
```

### Parameters

- `--email` or `-e`: (Required) The email address for the superadmin user
- `--password` or `-p`: (Required) The password for the superadmin user
- `--name` or `-n`: (Optional) The display name for the superadmin user (default: "System Administrator")

### Examples

1. Create a superadmin with minimal parameters:
   ```bash
   cd mnfst-rag-backend
   source .venv/bin/activate
   python create_superadmin.py --email admin@example.com --password securepassword123
   ```

2. Create a superadmin with a custom name:
   ```bash
   cd mnfst-rag-backend
   source .venv/bin/activate
   python create_superadmin.py --email admin@example.com --password securepassword123 --name "Main Admin"
   ```

3. Using short flags:
   ```bash
   cd mnfst-rag-backend
   source .venv/bin/activate
   python create_superadmin.py -e admin@example.com -p securepassword123 -n "Main Admin"
   ```

4. Using uv instead of activating venv:
   ```bash
   cd mnfst-rag-backend
   uv run python create_superadmin.py -e admin@example.com -p securepassword123 -n "Main Admin"
   ```

## What the Script Does

1. Validates the email format and password length
2. Connects to the database using the configured `DATABASE_URL`
3. Checks if a superadmin with the provided email already exists
4. If not exists, creates a new superadmin user with:
   - The provided email, password (hashed), and name
   - Role set to `SUPERADMIN`
   - No tenant association (superadmin is tenant-agnostic)

## Security Notes

- Choose a strong password for the superadmin user
- The superadmin user has full system access, so protect these credentials carefully
- The password is automatically hashed using bcrypt before storage

## Troubleshooting

If you encounter any issues:

1. Make sure your database is running and accessible
2. Check that your `.env` file has the correct `DATABASE_URL`
3. Ensure the database tables have been created (run migrations if needed)
4. Verify you have the necessary permissions to create users in the database