from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import random
import datetime
import requests

# 🔑 Replace with your real BIN lookup API key if needed
BIN_LOOKUP_URL = "https://lookup.binlist.net/{}"

# Luhn check
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

# Generate one CC
def generate_cc_from_bin(bin_prefix):
    while True:
        card_number = bin_prefix + ''.join(str(random.randint(0, 9)) for _ in range(9))
        for last_digit in range(10):
            full_card = card_number + str(last_digit)
            if luhn_checksum(full_card):
                break
        month = str(random.randint(1, 12)).zfill(2)
        year = str(random.randint(datetime.datetime.now().year % 100 + 1, datetime.datetime.now().year % 100 + 4))
        cvv = str(random.randint(100, 999))
        return f"{full_card} | {month}/{year} | CVV: {cvv}"

# Fetch BIN details
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

# Main handler
def gen(update: Update, context: CallbackContext):
    try:
        if len(context.args) == 0:
            update.message.reply_text("❗ Usage: /gen <6-digit BIN> [quantity]\nExample: /gen 414720 5")
            return

        bin_prefix = context.args[0]
        quantity = int(context.args[1]) if len(context.args) > 1 else 5

        if not bin_prefix.isdigit() or len(bin_prefix) != 6:
            update.message.reply_text("❌ BIN must be exactly 6 digits.")
            return

        if quantity > 20:
            update.message.reply_text("🚫 Max limit is 20 cards at once.")
            return

        # Get BIN info
        bin_info = get_bin_info(bin_prefix)

        # Generate cards
        cards = [generate_cc_from_bin(bin_prefix) for _ in range(quantity)]
        card_text = "\n".join(cards)

        update.message.reply_text(f"{bin_info}\n\n💳 Generated {quantity} Fake CCs:\n\n{card_text}")
    except Exception as e:
        update.message.reply_text(f"Error: {e}")

# Bot runner
def main():
    print("Starting bot...")
    try:
        updater = Updater("7613257509:AAE-H2p7U-KSVNWTCg-EtXKIjKGUKh3mA5Q", use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("gen", gen))
        updater.start_polling()
        print("Bot is polling...")
        updater.idle()
    except Exception as e:
        print(f"Bot failed: {e}")

if __name__ == '__main__':
    main()
