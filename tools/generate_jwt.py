#!/usr/bin/env python3
"""Generate JWT tokens for testing the SAR submission API."""

import argparse
import jwt
import sys
from datetime import datetime, timedelta


def generate_token(
    subject: str,
    scope: str = "sar:write",
    secret: str = "dev_secret_change_in_production",
    algorithm: str = "HS256",
    hours: int = 1
) -> str:
    """
    Generate a JWT token for API authentication.
    
    Args:
        subject: User identity (sub claim)
        scope: Required scope (default: sar:write)
        secret: JWT secret key
        algorithm: JWT algorithm (default: HS256)
        hours: Token validity in hours (default: 1)
        
    Returns:
        JWT token string
    """
    payload = {
        "sub": subject,
        "scope": scope,
        "exp": datetime.utcnow() + timedelta(hours=hours),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, secret, algorithm=algorithm)
    return token


def main():
    parser = argparse.ArgumentParser(
        description="Generate JWT tokens for SAR API authentication"
    )
    parser.add_argument(
        "--subject",
        "-s",
        required=True,
        help="Subject (user identity) for the token"
    )
    parser.add_argument(
        "--scope",
        default="sar:write",
        help="Token scope (default: sar:write)"
    )
    parser.add_argument(
        "--secret",
        default="dev_secret_change_in_production",
        help="JWT secret key (default: dev_secret_change_in_production)"
    )
    parser.add_argument(
        "--algorithm",
        default="HS256",
        help="JWT algorithm (default: HS256)"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=1,
        help="Token validity in hours (default: 1)"
    )
    
    args = parser.parse_args()
    
    try:
        token = generate_token(
            subject=args.subject,
            scope=args.scope,
            secret=args.secret,
            algorithm=args.algorithm,
            hours=args.hours
        )
        
        print(f"Subject: {args.subject}")
        print(f"Scope: {args.scope}")
        print(f"Valid for: {args.hours} hour(s)")
        print(f"\nToken:")
        print(token)
        print(f"\nAuthorization header:")
        print(f"Bearer {token}")
        
    except Exception as e:
        print(f"Error generating token: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
