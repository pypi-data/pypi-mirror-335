#!/usr/bin/env python3
import argparse
import os
import sys
import time

from tiptree.client import TiptreeClient
from tiptree.interface_models import OTPSignupRequest


def _save_credentials(api_key, token_response):
    """Helper function to save credentials to file."""
    config_dir = os.path.expanduser("~/.tiptreerc")
    os.makedirs(config_dir, exist_ok=True)
    credentials_file = os.path.join(config_dir, "credentials")
    with open(credentials_file, "w") as f:
        f.write(f"TIPTREE_API_KEY={api_key}\n")
        f.write(f"TIPTREE_ACCESS_TOKEN={token_response.access_token}\n")
        if token_response.refresh_token:
            f.write(f"TIPTREE_REFRESH_TOKEN={token_response.refresh_token}\n")
        f.write(f"TIPTREE_TOKEN_EXPIRES_IN={token_response.expires_in}\n")
    print(f"Credentials saved to {credentials_file}")


def _handle_api_key_creation(token_response):
    """Helper function to handle API key creation and saving."""
    client = TiptreeClient()

    create_key = input("\nDo you want to create an API key now? (y/n): ")
    if create_key.lower() != "y":
        print(
            "\nYou can create an API key later using the 'tiptree keys create' command."
        )
        return None

    print("\nCreating API key...")
    api_key_response = client.create_api_key(token_response.access_token)
    api_key = api_key_response.api_key
    print(f"API key created successfully!")
    print(f"\nIMPORTANT: Your API key is: {api_key}")
    print("Please save this key somewhere secure as it won't be shown again.")

    save = input(
        "\nDo you want to save your credentials to ~/.tiptreerc/credentials? (y/n): "
    )
    if save.lower() == "y":
        _save_credentials(api_key, token_response)

    return api_key


def _handle_otp_verification(email, is_signup=False, first_name=None, last_name=None):
    """Common function to handle OTP verification flow for both signup and signin."""
    client = TiptreeClient()

    try:
        # Start signup/signin process
        print("\nSending verification code to your email...")

        if is_signup:
            # Create signup request
            signup_request = OTPSignupRequest(
                email=email, first_name=first_name, last_name=last_name
            )
            response = client.signup_with_otp(signup_request)
        else:
            response = client.signin_with_otp(email)

        if response.status != "ok":
            print(f"Error: {response.message}")
            return False

        # Get token from response
        token = response.payload.get("token")
        if not token:
            print("Error: No verification token received")
            return False

        # Get OTP from user
        print("\nA verification code has been sent to your email.")
        otp = input("Enter verification code: ")

        # Verify OTP
        print("\nVerifying...")
        if is_signup:
            token_response = client.verify_signup_otp(token=token, otp=otp)
        else:
            token_response = client.verify_signin_otp(token=token, otp=otp)

        print(f"\nSuccessfully {'signed up' if is_signup else 'signed in'}!")

        if is_signup:
            print("\nYou will need to create an API key to use the Tiptree API.")

        _handle_api_key_creation(token_response)
        return True

    except Exception as e:
        print(f"Error during {'signup' if is_signup else 'signin'}: {str(e)}")
        return False


def signup():
    """CLI interface for signing up."""
    print("Welcome to Tiptree Signup")
    print("------------------------")

    # Get user input
    email = input("Email: ")
    first_name = input("First name: ")
    last_name = input("Last name (optional): ") or None

    return _handle_otp_verification(
        email, is_signup=True, first_name=first_name, last_name=last_name
    )


def signin():
    """CLI interface for signing in."""
    print("Welcome to Tiptree Signin")
    print("-----------------------")

    # Get user input
    email = input("Email: ")

    return _handle_otp_verification(email, is_signup=False)


def _get_access_token():
    """Helper function to get access token from environment or credentials file."""
    access_token = os.environ.get("TIPTREE_ACCESS_TOKEN")
    if not access_token:
        # Check in credentials file
        credentials_file = os.path.expanduser("~/.tiptreerc/credentials")
        if os.path.exists(credentials_file):
            with open(credentials_file, "r") as f:
                for line in f:
                    if line.startswith("TIPTREE_ACCESS_TOKEN="):
                        access_token = line.strip().split("=", 1)[1]
                        break
    return access_token


def _get_api_key():
    """Helper function to get API key from environment or credentials file."""
    api_key = os.environ.get("TIPTREE_API_KEY")
    if not api_key:
        # Check in credentials file
        credentials_file = os.path.expanduser("~/.tiptreerc/credentials")
        if os.path.exists(credentials_file):
            with open(credentials_file, "r") as f:
                for line in f:
                    if line.startswith("TIPTREE_API_KEY="):
                        api_key = line.strip().split("=", 1)[1]
                        break
    return api_key


def create_api_key():
    """Create a new API key."""
    # Check for access token
    access_token = _get_access_token()

    if not access_token:
        print("Error: No access token found. Please sign in first.")
        return False

    client = TiptreeClient()

    try:
        print("Creating new API key...")
        response = client.create_api_key(access_token)

        api_key = response.api_key
        print(f"\nAPI key created successfully!")
        print(f"Your new API key is: {api_key}")

        save = input(
            "\nDo you want to save this API key to ~/.tiptreerc/credentials? (y/n): "
        )
        if save.lower() == "y":
            config_dir = os.path.expanduser("~/.tiptreerc")
            os.makedirs(config_dir, exist_ok=True)
            credentials_file = os.path.join(config_dir, "credentials")

            # Read existing credentials
            existing_lines = []
            if os.path.exists(credentials_file):
                with open(credentials_file, "r") as f:
                    existing_lines = f.readlines()

            # Update or add API key
            api_key_updated = False
            for i, line in enumerate(existing_lines):
                if line.startswith("TIPTREE_API_KEY="):
                    existing_lines[i] = f"TIPTREE_API_KEY={api_key}\n"
                    api_key_updated = True
                    break

            if not api_key_updated:
                existing_lines.append(f"TIPTREE_API_KEY={api_key}\n")

            # Write back to file
            with open(credentials_file, "w") as f:
                f.writelines(existing_lines)

            print(f"API key saved to {credentials_file}")

        return True

    except Exception as e:
        print(f"Error creating API key: {str(e)}")
        return False


def list_api_keys():
    """List all API keys for the authenticated user."""
    api_key = _get_api_key()
    if not api_key:
        print(
            "Error: No API key found. Please set the TIPTREE_API_KEY environment variable."
        )
        return False

    client = TiptreeClient(api_key=api_key)

    try:
        print("Fetching API keys...")
        api_sessions = client.list_api_keys()

        if not api_sessions:
            print("You don't have any active API keys.")
            return True

        print("\nYour API keys:")
        print("--------------")
        for i, session in enumerate(api_sessions, 1):
            created = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(session.created_at)
            )
            expires = (
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(session.expires_at))
                if session.expires_at
                else "Never"
            )
            revoked = (
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(session.revoked_at))
                if session.revoked_at
                else "No"
            )

            print(f"{i}. ID: {session.id}")
            print(f"   Created: {created}")
            print(f"   Expires: {expires}")
            print(f"   Revoked: {revoked}")
            print()

        return True

    except Exception as e:
        print(f"Error fetching API keys: {str(e)}")
        return False


def revoke_api_key():
    """Revoke an API key."""
    api_key = os.environ.get("TIPTREE_API_KEY")
    if not api_key:
        print(
            "Error: No API key found. Please set the TIPTREE_API_KEY environment variable."
        )
        return False

    api_key = _get_api_key()
    if not api_key:
        print(
            "Error: No API key found. Please set the TIPTREE_API_KEY environment variable."
        )
        return False

    client = TiptreeClient(api_key=api_key)

    try:
        # List API keys
        api_sessions = client.list_api_keys()

        if not api_sessions:
            print("You don't have any active API keys to revoke.")
            return True

        print("\nYour API keys:")
        print("--------------")
        for i, session in enumerate(api_sessions, 1):
            created = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(session.created_at)
            )
            expires = (
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(session.expires_at))
                if session.expires_at
                else "Never"
            )
            revoked = "Yes" if session.revoked_at else "No"

            print(f"{i}. ID: {session.id}")
            print(f"   Created: {created}")
            print(f"   Expires: {expires}")
            print(f"   Revoked: {revoked}")
            print()

        # Ask which key to revoke
        selection = input(
            "Enter the number of the API key to revoke (or 'q' to quit): "
        )
        if selection.lower() == "q":
            return True

        try:
            index = int(selection) - 1
            if 0 <= index < len(api_sessions):
                session = api_sessions[index]
                if session.revoked_at:
                    print("This API key is already revoked.")
                    return True

                # Confirm revocation
                confirm = input(
                    f"Are you sure you want to revoke API key {session.id}? (y/n): "
                )
                if confirm.lower() != "y":
                    print("Operation cancelled.")
                    return True

                # Revoke key
                print("Revoking API key...")
                response = client.revoke_api_key(session.id)
                print("API key successfully revoked.")

                # If we're revoking the current key, warn the user
                current_key_id = None
                for sess in api_sessions:
                    if not sess.revoked_at and session.id == sess.id:
                        current_key_id = sess.id
                        break

                if current_key_id:
                    print("\nWARNING: You revoked your current API key.")
                    print("You will need to sign in again to get a new API key.")

                return True
            else:
                print("Invalid selection.")
                return False
        except ValueError:
            print("Invalid input. Please enter a number.")
            return False

    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(description="Tiptree CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Signup command
    signup_parser = subparsers.add_parser("signup", help="Sign up for a new account")

    # Signin command
    signin_parser = subparsers.add_parser("signin", help="Sign in to your account")

    # API keys commands
    keys_parser = subparsers.add_parser("keys", help="Manage API keys")
    keys_subparsers = keys_parser.add_subparsers(
        dest="keys_command", help="API keys commands"
    )

    list_keys_parser = keys_subparsers.add_parser("list", help="List your API keys")
    revoke_keys_parser = keys_subparsers.add_parser("revoke", help="Revoke an API key")
    create_keys_parser = keys_subparsers.add_parser(
        "create", help="Create a new API key"
    )

    args = parser.parse_args()

    if args.command == "signup":
        return signup()
    elif args.command == "signin":
        return signin()
    elif args.command == "keys":
        if args.keys_command == "list":
            return list_api_keys()
        elif args.keys_command == "revoke":
            return revoke_api_key()
        elif args.keys_command == "create":
            return create_api_key()
        else:
            keys_parser.print_help()
    else:
        parser.print_help()

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
