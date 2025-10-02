import os
from pathlib import Path
from dotenv import load_dotenv
import stripe

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")


def get_stripe_client():
    if not STRIPE_SECRET_KEY or not STRIPE_SECRET_KEY.startswith("sk_"):
        raise ValueError(f"Invalid Stripe key loaded: {repr(STRIPE_SECRET_KEY)}")
    stripe.api_key = STRIPE_SECRET_KEY
    return stripe
