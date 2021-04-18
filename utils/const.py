import os
from decimal import Decimal

JWT_SECRET_KEY = "583a3ceddd97521c7c2a22300e1dafd35a86d5d263d0e6136a0fbe025574f5ee"  # openssl rand -hex 32
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME_MINUTES = 24 * 60  # 1 day

JWT_EXPIRED_MSG = "Your JWT is expired."
JWT_INVALID_MSG = "Invalid JWT"
JWT_INVALID_CREDENTIALS_MSG = "Invalid credentials"
JWT_INVALID_ROLE_MSG = "Unauthorized role"

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "app")
DB_USER = os.environ.get("DB_USER", "appuser")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "superS3cretpassw0rd")
DB_URL = os.environ.get("DATABASE_URL", f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
DB_URL = "postgres://mdjwblfxhyktec:c628c82c087c7481b789cffd3b9bbed2de197129a13258b2b99fa72930b1a8e4@ec2-54-205-183-19.compute-1.amazonaws.com:5432/d2p7pl042merm3"

DAYS_TO_RETURN_MOVIES = 5
DELAY_PENALTY_PERCENTAGE_PER_DAY = Decimal("0.01")
