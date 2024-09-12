
from telegram import Update, Bot, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackContext
import logging
import json
import os

# Token-ul botului tău - folosit din variabilele de mediu Railway
TOKEN = os.getenv('TOKEN')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID'))  # ID-ul tău de admin din variabilele de mediu

# Fișierul pentru stocarea utilizatorilor
USERS_FILE = 'registered_users.json'

# Inițializarea logger-ului
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Încarcă utilizatorii înregistrați din fișier sau inițializează o listă goală
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'r') as file:
        registered_users = set(json.load(file))
else:
    registered_users = set()

# Salvarea utilizatorilor în fișier
def save_users():
    with open(USERS_FILE, 'w') as file:
        json.dump(list(registered_users), file)

# Funcție pentru a gestiona comanda /start
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in registered_users:
        registered_users.add(user_id)  # Înregistrează utilizatorul
        save_users()  # Salvează utilizatorii în fișier
    context.bot.send_message(chat_id=user_id, text="Bine ai venit la botul nostru! 😊")

# Funcție pentru a trimite mesaje tuturor utilizatorilor înregistrați
def send_message_to_all(context: CallbackContext, text: str, image_path: str = None):
    for user_id in registered_users:
        try:
            if image_path:
                context.bot.send_photo(chat_id=user_id, photo=open(image_path, 'rb'), caption=text)
            else:
                context.bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            logging.error(f"Eroare la trimiterea mesajului către {user_id}: {e}")

# Handler pentru comanda /send_all care primește un mesaj și opțional o imagine de la utilizatorul admin
def send_all(update: Update, context: CallbackContext):
    if update.effective_user.id == ADMIN_USER_ID:
        if len(context.args) < 1:
            update.message.reply_text("Utilizare: /send_all <mesaj> [cale_către_imagine]")
            return
        
        text = ' '.join(context.args[:-1])  # Mesajul de trimis
        image_path = context.args[-1] if len(context.args) > 1 else None

        send_message_to_all(context, text, image_path)
        update.message.reply_text("Mesajul a fost trimis către toți utilizatorii.")
    else:
        update.message.reply_text("Nu ai permisiunea să folosești această comandă.")

# Configurare bot
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Adăugăm handler-ul pentru comanda /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Adăugăm handler-ul pentru comanda /send_all pentru admin
    dispatcher.add_handler(CommandHandler("send_all", send_all))

    # Pornim botul
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
