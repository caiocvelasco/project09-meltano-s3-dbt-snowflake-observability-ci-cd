import os
import stripe
import random
import string
from dotenv import load_dotenv

# -------------------------------
# 1. Load API keys from .env
# -------------------------------
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# -------------------------------
# 2. Configurable parameters
# -------------------------------
NUM_CUSTOMERS = 10         # Number of fake customers
PAYMENTS_PER_CUSTOMER = 2  # Payments per customer

# Example currencies to pick from
CURRENCIES = ["usd", "eur"]  

# Stripe test cards (for variability)
TEST_CARDS = ["pm_card_visa", "pm_card_mastercard", "pm_card_amex", "pm_card_chargeCustomerFail"]

# Amount range in cents ($1 to $100)
AMOUNT_MIN = 100
AMOUNT_MAX = 10000

# -------------------------------
# Helper: generate random string
# -------------------------------
def random_suffix(length=6):
    """Return a random lowercase alphanumeric string."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

# -------------------------------
# 3. Create fake customers with unique names
# -------------------------------
customers = []
for i in range(NUM_CUSTOMERS):
    unique_name = f"Test Customer {random_suffix()}"
    email = f"{unique_name.replace(' ', '_').lower()}@example.com"
    customer = stripe.Customer.create(
        email=email,
        name=unique_name
    )
    customers.append(customer)
    print(f"👤 Created test customer {i+1}: {customer['id']} ({unique_name})")

# -------------------------------
# 4. Create random payments for each customer
# -------------------------------
for customer in customers:
    for i in range(PAYMENTS_PER_CUSTOMER):
        amount = random.randint(AMOUNT_MIN, AMOUNT_MAX)  # Random amount
        currency = random.choice(CURRENCIES)            # Random currency
        card = random.choice(TEST_CARDS)               # Random test card

        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer["id"],
                payment_method_types=["card"],
                confirm=True,
                payment_method=card
            )
            print(f"💳 Payment {i+1} for {customer['id']}: {payment_intent['id']} "
                  f"Amount: {amount/100:.2f} {currency.upper()}, Card: {card}")
        except stripe.error.CardError as e:
            print(f"⚠️ Payment {i+1} for {customer['id']} failed: {e.user_message}")

# -------------------------------
# 5. Observability & schema impact
# -------------------------------
# - Customers → `customers` stream
# - PaymentIntents → `payment_intents` stream
# - Each confirmed PaymentIntent → Charge → `charges` stream
# - Events fired → `events` stream
# - Random amounts, currencies, and test cards simulate real-world variability for schema checks
