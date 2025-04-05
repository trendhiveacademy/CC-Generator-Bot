from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import random
import datetime
import requests

# BIN Lookup API
BIN_LOOKUP_URL = "https://lookup.binlist.net/{}"

# Luhn check function
def luhn_checksum(card_number):
    def digits_of(n): return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    checksum = 0
    parity = len(digits) % 2
    for i, digit in enumerate(digits):
        if i % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0

# Generate valid CC from BIN, month, year
def generate_cc(bin_code, month=None, year=None):
    while True:
        cc = bin_code
        while len(cc) < 15:
            cc += str(random.randint(0, 9))
        for last_digit in range(10):
            full_card = cc + str(last_digit)
            if luhn_checksum(full_card):
                break

        # Set month/year
        exp_month = month if month else str(random.randint(1, 12)).zfill(2)
        current_year = datetime.datetime.now().year % 100
        exp_year = year if year else str(random.randint(current_year + 1, current_year + 5)).zfill(2)
        cvv = str(random.randint(100, 999))

        return f"{full_card} | {exp_month}/{exp_year} | CVV: {cvv}"

# Get BIN details (country, brand, etc.)
def get_bin_info(bin_number):
    try:
        response = requests.get(BIN_LOOKUP_URL.format(bin_number))
        if response.status_code == 200:
            data = response.json()
            brand = data.get("scheme", "Unknown").title()
            card_type = data.get("type", "Unknown").title()
            bank = data.get("bank", {}).get("name", "Unknown")
            country = data.get("country", {}).get("name", "Unknown")
            emoji = data.get("country", {}).get("emoji", "🌍")
            return f"🏦 Bank: {bank}\n💳 Brand: {brand} | {card_type}\n🌍 Country: {country} {emoji}"
        else:
            return "🔎 BIN info not found."
    except Exception:
        return "⚠️ Failed to fetch BIN info."

# /gen command handler
def gen(update: Update, context: CallbackContext):
    try:
        if len(context.args) == 0:
            update.message.reply_text("❗ Usage: /gen <BIN> [quantity]\nOr: /gen <BIN|MM|YY> [quantity]")
            return

        parts = context.args[0].split("|")
        bin_code = parts[0]
        month = parts[1] if len(parts) > 1 else None
        year = parts[2] if len(parts) > 2 else None
        quantity = int(context.args[1]) if len(context.args) > 1 else 5

        if not bin_code.isdigit() or not (6 <= len(bin_code) <= 11):
            update.message.reply_text("❌ BIN must be 6 to 11 digits.")
            return

        if quantity > 20:
            update.message.reply_text("🚫 Max limit is 20 cards at once.")
            return

        # BIN Info
        bin_info = get_bin_info(bin_code)

        # Generate Cards
        cards = [generate_cc(bin_code, month, year) for _ in range(quantity)]
        card_text = "\n".join(cards)

        update.message.reply_text(f"{bin_info}\n\n💳 Generated {quantity} Fake CCs:\n\n{card_text}")
    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {e}")

# Start Bot
def main():
    print("Starting bot...")
    try:
        updater = Updater("7613257509:AAE-H2p7U-KSVNWTCg-EtXKIjKGUKh3mA5Q", use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("gen", gen))
        updater.start_polling()
        print("✅ Bot is polling...", flush=True)
        updater.idle()
    except Exception as e:
        print(f"❌ Bot failed: {e}")

if __name__ == '__main__':
    main()
