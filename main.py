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
            target_channel = discord.utils.get(message.guild.channels, name=channel_name)
            if target_channel:
                try:
                    # Préparer le message à envoyer
                    formatted_message = f"**{message.author.name}**: "

                    # Gérer le texte s'il existe
                    if message.content:
                        translated = translator.translate(message.content, src=source_lang, dest=target_lang).text
                        formatted_message += translated
                    else:
                        formatted_message += "(Pas de texte)"  # Message par défaut si pas de contenu texte

                    # Gérer les images (attachments)
                    if message.attachments:
                        # Envoyer le message avec les URLs des images
                        attachment_urls = "\n".join([attachment.url for attachment in message.attachments])
                        formatted_message += f"\n{attachment_urls}"

                    # Envoyer le message au salon cible
                    await target_channel.send(formatted_message)

                except Exception as e:
                    logger.error(f"Erreur lors du traitement du message vers {target_lang} : {e}")
                    await target_channel.send(f"Erreur : {e}")

# Configuration du serveur Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/ping')
def ping():
    return "OK", 200  # Route keep-alive

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