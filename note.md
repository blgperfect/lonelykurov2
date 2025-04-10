🔍 Ce que t’as déjà (résumé utile) :
Modération (ban/kick/warn/clear/report)
Utilisateurs (userinfo, niveau, vocstats, rôles, présentation)
Server tools (makeprivate, makevocale, autorole, rules, stealemoji, suggestion, reaction msg, threads, confessions)
Logs/Events (edit/delete, invites, booster, anniversaire, tickets, logs)
Commandes utilitaires (help, serverinfo)
Fun/Gestion (giveaways, annonce, tâches manuelles)





okay alors maintenant en respectant ma structure de code actuelle
fait moi une commande slash et prefix qui permettre a un membre de ce mettre afk nom de commande : afk
quand il l'utuliserais son pseudo seras immédiatement changer pour AFK | ici sont nom d'utulisateur , et au moment ou la personne parle dans un salon ou rentre dans un vocale enleve automatique et lui remet celui qu'il avais 
au besoin utulise mongodb dans le code comme suis (renomme seulemeent la collection)
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
client_mongo = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client_mongo[DATABASE_NAME]
role_auto_col = db["role_auto"]