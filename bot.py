import discord
from discord.ext import commands
import motor.motor_asyncio
import os
import asyncio
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Configuration du bot avec intents
intents = discord.Intents.all()
intents.members = True  # Active l'intent des membres !
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
discord_client = discord.Client(intents=intents, activity=discord.CustomActivity('Lonely kurozen!!! <3'))

# Connexion à MongoDB avec motor (async)
client_mongo = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client_mongo[DATABASE_NAME]

# Variables pour compter les chargements
command_count = 0
task_count = 0

# Fonction pour charger les commandes dynamiquement
async def load_extensions():
    global command_count
    print("🔄 Chargement des commandes...")
    for root, _, files in os.walk("./commands"):
        for file in files:
            if file.endswith(".py"):
                module_path = os.path.join(root, file).replace("./", "").replace("/", ".")[:-3]
                try:
                    if module_path in bot.extensions:
                        await bot.reload_extension(module_path)
                    else:
                        await bot.load_extension(module_path)
                    command_count += 1
                except Exception as e:
                    print(f" Erreur lors du chargement de {module_path} : {e}")
    print(f"✅ {command_count} commandes chargées avec succès.")

# Fonction pour charger les cogs dans le dossier "task/"
async def load_task_extensions():
    global task_count
    print("🔄 Chargement des cogs (task)...")
    for filename in os.listdir("./task"):
        if filename.endswith(".py") and filename != "__init__.py":
            cog_name = f"task.{filename[:-3]}"
            try:
                if cog_name in bot.extensions:
                    await bot.reload_extension(cog_name)
                else:
                    await bot.load_extension(cog_name)
                task_count += 1
            except Exception as e:
                print(f" Erreur lors du chargement de {cog_name} : {e}")
    print(f"✅ {task_count} cogs chargés avec succès.")

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user} ({bot.user.id})")
    
    # Synchronisation des commandes slash
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} commandes slash synchronisées avec Discord.")
    except Exception as e:
        print(f" Erreur de synchronisation des commandes slash : {e}")

    # Changer la présence du bot
    await discord_client.start(os.environ["DISCORD_TOKEN"])

# Commande de test classique
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong ! Latence : {round(bot.latency * 1000)}ms")

# 🚀 Lancer le bot avec asyncio
async def main():
    async with bot:
        await load_task_extensions()  # Charge les fichiers du dossier task/
        await load_extensions()  # Charge les commandes
        print(f"🚀 Tout est chargé : {command_count} commandes et {task_count} cogs.")
        await bot.start(TOKEN)

asyncio.run(main())  # Lancement du bot
