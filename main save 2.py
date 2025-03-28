import discord
from googletrans import Translator
import os
from dotenv import load_dotenv
from flask import Flask
import threading
import logging

# Configurer les logs pour mieux diagnostiquer les problèmes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
translator = Translator()

# Configuration des salons et langues
channels = {
    "general": "en",
    "general-fr": "fr",
    "general-en": "en",
    "general-es": "es",
    "general-uk": "uk",
    "general-br": "pt",
    "general-cn": "zh-cn",
    "general-de": "de",
    "general-kr": "ko"
}

@client.event
async def on_ready():
    logger.info(f"Connecté en tant que {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user or message.channel.name not in channels:
        return

    source_lang = channels[message.channel.name]
    for channel_name, target_lang in channels.items():
        if channel_name != message.channel.name:
            target_channel = discord.utils.get(message.guild.channels,
                                               name=channel_name)
            if target_channel:
                try:
                    translated = translator.translate(message.content,
                                                      src=source_lang,
                                                      dest=target_lang).text
                    formatted_message = f"**{message.author.name}**: {translated}"
                    await target_channel.send(formatted_message)
                except Exception as e:
                    logger.error(
                        f"Erreur de traduction vers {target_lang} : {e}")
                    await target_channel.send(f"Erreur de traduction : {e}")

# Configuration du serveur Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Nouvelle route pour le keep-alive
@app.route('/ping')
def ping():
    return "OK", 200  # Réponse simple pour indiquer que le serveur est actif

# Fonction pour lancer le bot Discord avec reconnexion en cas d'erreur
def run_bot():
    while True:
        try:
            logger.info("Démarrage du bot Discord...")
            client.run(os.getenv("DISCORD_TOKEN"))
        except Exception as e:
            logger.error(f"Le bot s'est arrêté avec une erreur : {e}")
            logger.info("Tentative de reconnexion dans 5 secondes...")
            threading.Event().wait(5)  # Attendre 5 secondes avant de relancer

# Lancer Flask et le bot en parallèle
if __name__ == "__main__":
    # Démarrer le bot dans un thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True  # Permet au thread de s'arrêter si le programme principal s'arrête
    bot_thread.start()
    # Démarrer le serveur Flask dans le thread principal
    app.run(host='0.0.0.0', port=8080, debug=False)