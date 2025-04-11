CATEGORIES = {
    "🔧 Modération": {
        "/ban": "**Description** : Bannir un utilisateur.\n**Type** : slash\n**Usage (slash)** : `/ban <member> <reason>`\n**Permission** : `ban_members`",
        "/kick": "**Description** : Expulser un membre du serveur.\n**Type** : slash\n**Usage (slash)** : `/kick <member> <reason>`\n**Permission** : `kick_members`",
        "/mute": "**Description** : Muter un membre.\n**Type** : slash\n**Usage (slash)** : `/mute <member> <duration> <reason>`\n**Permission** : `manage_roles`",
        "/unmute": "**Description** : Unmuter un membre.\n**Type** : slash\n**Usage (slash)** : `/unmute <member>`\n**Permission** : `manage_roles`",
        "/warn": "**Description** : Avertir un utilisateur.\n**Type** :slash\n**Usage (slash)** : `/warn <member> <reason>`\n**Permission** : `kick_members`",
        "/warns": "**Description** : Voir les avertissements d’un membre.\n**Type** : slash\n**Usage (slash)** : `/warns <member>`\n**Permission** : `kick_members`",
        "/warnlist": "**Description** : Liste des avertissements du serveur.\n**Type** : slash\n**Usage (slash)** : `/warnlist`\n**Permission** : `kick_members`",
        "/resetwarns": "**Description** : Réinitialiser les avertissements d’un membre.\n**Type** : slash\n**Usage (slash)** : `/resetwarns <member>`\n**Permission** : `kick_members`",
        "/clear": "**Description** : Supprimer un nombre de messages.\n**Type** : slash\n**Usage (slash)** : `/clear <amount>`\n**Permission** : `manage_messages`",
        "/fermer": "**Description** : Fermer un ticket.\n**Type** : slash\n**Usage (slash)** : `/fermer`\n**Permission** : `kick_members`",
        "/staff": "**Description** : Envoyer un formulaire de candidature.\n**Type** : prefix\n**Usage (prefix)** : `!staff <ctx>`\n**Permission** : `@everyone`"
    },
    "🛠️ Configuration & Gestion": {
        "/config_salon_menu": "**Description** : Configurer les threads ou réactions d’un salon.\n**Type** : slash\n**Usage (slash)** : `/config_salon_menu`\n**Permission** : `administrator`",
        "/delete-private": "**Description** : Supprimer un salon privé.\n**Type** : slash\n**Usage (slash)** : `/delete-private <membre>`\n**Permission** : `administrator`",
        "/make-private": "**Description** : Créer un salon privé pour un membre.\n**Type** : slash\n**Usage (slash)** : `/make-private <membre> <catégorie> <raison> <temp>`\n**Permission** : `administrator`",
        "/role-auto": "**Description** : Configurer un rôle automatique on join.\n**Type** : slash\n**Usage (slash)** : `/role-auto`\n**Permission** : `administrator`",
        "/rolesetup": "**Description** : Configuration du menu de rôles.\n**Type** :  slash\n**Usage (slash)** : `/rolesetup`\n**Permission** : `administrator`",
        "/setup-voc-temp": "**Description** : Créer des salons vocaux temporaires.\n**Type** : slash\n**Usage (slash)** : `/setup-voc-temp`\n**Permission** : `administrator`",
        "/ticketpanel": "**Description** : Envoyer le panneau de ticket.\n**Type** : slash\n**Usage (slash)** : `/ticketpanel`\n**Permission** : `administrator`",
        "/suggestions-config": "**Description** : Configurer le salon des suggestions.\n**Type** : slash\n**Usage (slash)** : `/suggestions-config`\n**Permission** : `administrator`",
        "/regles": "**Description** : Afficher le règlement du serveur.\n**Type** :  slash\n**Usage (slash)** : `/regles`\n**Permission** : `administrator`"
    },
    "⭐ Niveaux & Présentation": {
        "/lvl": "**Description** : Voir ton niveau ou celui d’un autre.\n**Type** : slash\n**Usage (slash)** : `/lvl`\n**Permission** : `@everyone`",
        "/leaderboard": "**Description** : Voir le classement du système de niveau.\n**Type** : slash\n**Usage (slash)** : `/leaderboard`\n**Permission** : `@everyone`",
        "/addxp": "**Description** : Ajouter de l’XP à un membre.\n**Type** : slash\n**Usage (slash)** : `/addxp <member> <amount>`\n**Permission** : `administrator`",
        "/presentation": "**Description** : Publier ou gérer sa présentation.\n**Type** : slash\n**Usage (slash)** : `/presentation`\n**Permission** : `@everyone`",
        "/evolution": "**Description** : Voir ton évolution personnelle.\n**Type** : slash\n**Usage (slash)** : `/evolution`\n**Permission** : `@everyone`",
        "/evolution_stats": "**Description** : Statistiques d’évolution du serveur.\n**Type** : slash\n**Usage (slash)** : `/evolution_stats`\n**Permission** : `@everyone`"
    },
    "🧰 Utilitaires & Infos": {
        "/addrole": "**Description** : Ajouter un rôle à un membre.\n**Type** :slash\n**Usage (slash)** : `/addrole <member> <role>`\n**Permission** : `manage_roles`",
        "/removerole": "**Description** : Retirer un rôle à un membre.\n**Type** :  slash\n**Usage (slash)** : `/removerole <member> <role>`\n**Permission** : `manage_roles`",
        "/steal": "**Description** : Voler un emoji depuis un autre serveur.\n**Type** :slash\n**Usage (slash)** : `/steal <emojis>`\n**Permission** : `manage_emojis_and_stickers`",
        "/report": "**Description** : Signaler un utilisateur.\n**Type** : slash\n**Usage (slash)** : `/report <user> <raison> <preuve>`\n**Permission** : `@everyone`",
        "/user-info": "**Description** : Voir les infos d’un utilisateur.\n**Type** : slash\n**Usage (slash)** : `/user-info <membre>`\n**Permission** : `@everyone`",
        "/server-info": "**Description** : Voir les infos du serveur.\n**Type** : slash\n**Usage (slash)** : `/server-info`\n**Permission** : `@everyone`",
        "/testboost": "**Description** : Tester le message de boost.\n**Type** : prefix + slash\n**Usage (prefix)** : `!testboost <ctx>`\n**Usage (slash)** : `/testboost`\n**Permission** : `Non précisée`",
        "/changenick": "**Description** : Changer le pseudo d’un membre.\n**Type** : slash\n**Usage (slash)** : `/changenick <member> <nickname>`\n**Permission** : `manage_nicknames`",
        "/help": "**Description** : Afficher le menu d’aide.\n**Type** : slash\n**Usage (slash)** : `/help`\n**Permission** : `@everyone`",
        "/afk": "**Description** : Se mettre AFK avec une raison.\n**Type** :  slash\n**Usage (slash)** : `/afk <raison>`\n**Permission** : `@everyone`",
        "/voc-stats": "**Description** : Configurer les stats vocales.\n**Type** : slash\n**Usage (slash)** : `/voc-stats`\n**Permission** : `administrator`"
    },
    "🎉 Événements": {
        "/giveaway": "**Description** : Organiser un giveaway.\n**Type** : slash\n**Usage (slash)** : `/giveaway <lot> <description> <gagnants> <duree> <salon> <limite_participants>`\n**Permission** : `manage_guild`",
        "/anniversaire_panel": "**Description** : Configurer le panneau anniversaire.\n**Type** : slash\n**Usage (slash)** : `/anniversaire_panel`\n**Permission** : `administrator`",
        "/confess": "**Description** : Envoyer une confession anonyme.\n**Type** : slash\n**Usage (slash)** : `/confess`\n**Permission** : `@everyone`"
    }
}
