addrole = prefix + slash
usage (prefix): !addrole  <member> <role>
usage (slash): /addrole  <member> <role>
- ajouté un role a un membre
perm manage_roles

addxp = slash
usage (slash): /addxp  <member> <amount>
- ajouté de l'xp a un membre
perm  administrator

afk = prefix + slash
usage (prefix): !afk <raison>
usage (slash): /afk  <raison>
- se mettre afk avec raison
perm : @everyone

anniversaire_panel = slash
usage (slash): /anniversaire_panel 
- configurer le pannel anniversaire 
perm : administrator

ban = prefix + slash
usage (prefix): !ban  <member> <raison>
usage (slash): /ban  <member> <reason>
- bannir un user
perm ban_members

changenick = prefix + slash
usage (prefix): !changenick  <member> <nickname>
usage (slash): /changenick <member> <nickname>
- changer le nickname d'un membre
perm manage_nicknames

clear = prefix + slash
usage (prefix): !clear  <amount>
usage (slash): /clear  <amount>
- supprimer des message !
perm manage_messages

confess = slash
usage (slash): /confess 
- envoyer confessions
 perm everyone

config_salon_menu = slash
usage (slash): /config_salon_menu 
- configurer les thread ou les reaction en salon
perm : administrator

delete-private = slash
usage (slash): /delete-private  <membre>
- supprimer un salon privée
perm : administrator

evolution = slash
usage (slash): /evolution 
- voir votre evolution de succes
perm : @everyone

evolution_stats = slash
usage (slash): /evolution_stats 
- voir les statistique devolution du server
perm @everyone

fermer = prefix + slash
usage (prefix): !fermer <ctx>
usage (slash): /fermer 
- permet de fermer un ticket 
perm kick_members

giveaway = slash
usage (slash): /giveaway  <lot> <description> <gagnants> <duree> <salon> <limite_participants>
- organiser un giveaways 
perm manage_guild

help = prefix + slash
usage (prefix): !help <ctx>
usage (slash): /help 
- voir le menu d'aide 
perm @everyone

kick = prefix + slash
usage (prefix): !kick <ctx> <member>
usage (slash): /kick  <member> <reason>
- kick un membre du server
perm kick_members

leaderboard = slash
usage (slash): /leaderboard 
- voir leaderboard du systeme de  niveau
perm @everyone

lvl = slash
usage (slash): /lvl 
- voir ton niveau ou celui d'un autre
perm @everyone

make-private = slash
usage (slash): /make-private  <membre> <catégorie> <raison> <temp>
- créer un salon privé pour un membre 
perm administrator

mute = slash
usage (slash): /mute  <member> <duration> <reason>
- muter un membre
perm manage_roles


presentation = slash
usage (slash): /presentation 
- publier ta présentation dans le salon présentation. acceder a ta présentation actuelle etc

regles = prefix + slash
usage (prefix): !regles <ctx>
usage (slash): /regles 
- affiché le menu d'aide
perm administrator

removerole = prefix + slash
usage (prefix): !removerole <ctx> <member> <role>
usage (slash): /removerole  <member> <role>
- retiré un role a un membre
perm manage_roles

report = slash
usage (slash): /report  <user> <raison> <preuve>
- reporter un membre du server
perm @everyone

resetwarns = prefix + slash
usage (prefix): !resetwarns <ctx> <member>
usage (slash): /resetwarns  <member>
- reinitialiser les warns d'un membre
perm kick_members

role-auto = slash
usage (slash): /role-auto 
- configuration dun role automatique onjoin 
perm administrator

rolesetup = prefix + slash
usage (prefix): !rolesetup <ctx>
usage (slash): /rolesetup 
- configuration du menu role
perm administrator

server-info = slash
usage (slash): /server-info 
- voir les info du server

setup-voc-temp = slash
usage (slash): /setup-voc-temp 
- créer les salon vocaux temporaire
perm administrator

staff = prefix
usage (prefix): !staff <ctx>
- envoie un formulaire de candidature.
perm @everyone

steal = prefix + slash
usage (prefix): !steal <ctx>
usage (slash): /steal  <emojis>
- voler des emojis 
perm manage_emojis_and_stickers

suggestions-config = slash
usage (slash): /suggestions-config 
- configurer le salon des suggestion 
perm administrator

testboost = prefix + slash
usage (prefix): !testboost <ctx>
usage (slash): /testboost 
- test le message de boost 
perm j'ai oublié

ticketpanel = prefix + slash
usage (prefix): !ticketpanel <ctx>
usage (slash): /ticketpanel 
- envoyer le pannel de ticket 
perm administrator


unmute = slash
usage (slash): /unmute  <member>
- unmuter un membre
perm manage_roles

user-info = slash
usage (slash): /user-info  <membre>
- voir les info de user 
perm @everyone

voc-stats = slash
usage (slash): /voc-stats 
- configurer les stats membre
perm administrator

warn = prefix + slash
usage (prefix): !warn <ctx> <member>
usage (slash): /warn  <member> <reason>
- warn un utulisateur
perm kick_members

warnlist = prefix + slash
usage (prefix): !warnlist <ctx>
usage (slash): /warnlist 
- voir la liste des warn du server 
perm kick_members

warns = prefix + slash
usage (prefix): !warns <ctx> <member>
usage (slash): /warns  <member>
- voir les warn d'un membre en particulier
perm kick_members





