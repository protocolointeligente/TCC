import os
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

_PRICE_MAP_ENV = {
    "basic": "STRIPE_PRICE_BASIC",
    "pro": "STRIPE_PRICE_PRO",
}


def create_checkout_session(clerk_user_id: str, plan: str) -> str:
    env_key = _PRICE_MAP_ENV.get(plan)
    if not env_key:
        raise ValueError(f"Plano inválido: {plan}")
    price_id = os.getenv(env_key)
    if not price_id:
        raise ValueError(f"Price ID não configurado para o plano '{plan}'.")

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{FRONTEND_URL}/dashboard?payment=success",
        cancel_url=f"{FRONTEND_URL}/pricing?payment=cancel",
        metadata={"clerk_user_id": clerk_user_id, "plan": plan},
    )
    return session.url
