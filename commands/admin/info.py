import discord
from discord.ext import commands
from discord.ui import View, Button

class InfoButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Button(label="Règlement Staff", emoji="📘", custom_id="reglement_staff", style=discord.ButtonStyle.primary))
        self.add_item(Button(label="Équipe Écoute", emoji="🫂", custom_id="equipe_ecoute", style=discord.ButtonStyle.primary))
        self.add_item(Button(label="Commandes Sanction", emoji="🔧", custom_id="commande_sanction", style=discord.ButtonStyle.primary))
        self.add_item(Button(label="Tickets – Nouveau Fonctionnement", emoji="🎫", custom_id="fonctionnement_tickets", style=discord.ButtonStyle.primary))
        self.add_item(Button(label="Hiérarchie Staff", emoji="🏛️", custom_id="hierarchie_staff", style=discord.ButtonStyle.primary))

class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info")
    async def info_command(self, ctx):
        await ctx.message.delete()

        embed = discord.Embed(
            title="📘 Menu d'information du Staff",
            description="Appuie sur un bouton ci-dessous pour consulter les informations détaillées.",
            color=discord.Color.purple()
        )
        embed.set_footer(text="lonely kurozen - sanctuaire du staff")
        embed.set_image(url="https://media.discordapp.net/attachments/1102406059722801184/1360322702203818054/7BE5F79E-1DF4-492E-B597-D52E7BA94B03.png?ex=67fab2bd&is=67f9613d&hm=6c918096e96bd5367541a520d935acd84135775a476053aaab17892475730967&=&format=webp&quality=lossless&width=618&height=618")


        await ctx.send(embed=embed, view=InfoButtons())

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.type == discord.InteractionType.component:
            return

        custom_id = interaction.data["custom_id"]

        if custom_id == "reglement_staff":
            embed = discord.Embed(
                title="𖥔・Règlement du Staff de lonely kurozen・𖥔",
                description=(
                    "Être staff ici, c’est porter une responsabilité dans l’équilibre du sanctuaire. Voici les règles à respecter pour faire rayonner l’équipe dans l’harmonie :\n\n"
                    "⸻\n\n"
                    "✦ 𝐀𝐃𝐌𝐈𝐍𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 ✦\n"
                    "\t1.\tDiscipline exemplaire : tu es garant du calme et du respect dans le serveur.\n"
                    "\t2.\tAucune embrouille avec les membres : on attend de toi du recul, du self-control, et de la maturité.\n"
                    "\t3.\tAutonomie : tu dois pouvoir gérer ton rôle sans attendre l’approbation constante des fondateurs.\n"
                    "\t4.\tPas de plaintes en privé : tout conflit ou désaccord doit être communiqué aux fondateurs, pas par DM ni en public.\n"
                    "\t5.\tGestion interne confidentielle : les problèmes internes ne se règlent pas en public, mais avec les deux fondateurs uniquement.\n"
                    "\t6.\tSanctions justifiées : tout ban doit être accompagné de preuves claires et d’une raison valable.\n\n"
                    "⸻\n\n"
                    "✦ 𝐌𝐎𝐃É𝐑𝐀𝐓𝐈𝐎𝐍 ✦\n"
                    "\t1.\tActivité obligatoire : une présence régulière et visible est indispensable. Être staff sans engagement actif n’est pas toléré.\n"
                    "\t2.\tSuivi des conversations : observe, participe, et sois attentif(ve) aux comportements.\n"
                    "\t3.\tRéactivité : tu dois être capable de gérer les conflits rapidement, sans les aggraver.\n"
                    "\t4.\tSanctions encadrées : tout ban nécessite une justification claire + preuve à l’appui.\n\n"
                    "⸻\n\n"
                    "Ce règlement peut évoluer. Si un doute persiste, la communication avec les fondateurs est essentielle.\n"
                    "Tu représentes le cœur du sanctuaire, fais-le avec sagesse."
                ),
                color=discord.Color.purple()
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1102406059722801184/1360133452023730216/8B8A2084-0198-4632-A941-AD44C978B8D1.png?ex=67fa027d&is=67f8b0fd&hm=f21458b6aa35ed436686e8af3e85b39dc72de6cfc60da6e8960ee365b25bbb54&=&format=webp&quality=lossless&width=618&height=618")
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif custom_id == "equipe_ecoute":
            embed = discord.Embed(
                title="𖥔・À propos de notre aide・𖥔",
                description=(
                    "Ce serveur est un espace d’écoute, de partage et de bienveillance.\n"
                    "Cependant, nous ne sommes pas des professionnels de santé mentale.\n"
                    "Notre équipe est là pour offrir du soutien moral, mais certaines situations dépassent notre portée.\n\n"
                    "⸻\n\n"
                    "✅ Ce que nous pouvons faire :\n\n"
                    "・Écouter activement avec empathie.\n"
                    "・Offrir un espace sûr pour s’exprimer librement.\n"
                    "・Apporter du réconfort et des conseils de base.\n"
                    "・Rediriger vers des ressources fiables (associations, lignes d’aide, etc.).\n\n"
                    "⸻\n\n"
                    "❌ Ce que nous ne pouvons pas faire :\n\n"
                    "・Gérer les situations d’urgence ou de crise aiguë (suicide, automutilation, etc.).\n"
                    "・Diagnostiquer, prescrire ou faire un suivi thérapeutique.\n"
                    "・Remplacer un professionnel de santé.\n"
                    "・Porter la responsabilité des choix ou actions des membres.\n\n"
                    "⸻\n\n"
                    "Nous sommes là pour écouter, rassurer, accompagner… mais nos moyens sont humains et limités.\n"
                    "En cas de détresse grave, tourne-toi vers des professionnels adaptés."
                ),
                color=discord.Color.purple()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1102406059722801184/1360131662029127810/vhngsEs_cZC82TBz_MQPptsVzdC4tXy20.jpg?ex=67fa00d2&is=67f8af52&hm=9f8827b58dfdd0289192ebc79c7a0487d3e68eef2dd6f558707affd7e72f7f94&")
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif custom_id == "commande_sanction":
            embed = discord.Embed(
                title="𖥔・Utilisation du bot Kurozen (Modération)・𖥔",
                description=(
                    "Toute modération passe désormais par le bot kurozen.\n"
                    "Les commandes doivent être utilisées uniquement dans :\n"
                    "<#1360135556314566848>\n\n"
                    "Cette règle est immédiate et obligatoire.\n\n"
                    "⸻\n\n"
                    "✦ Rappel rapide :\n\n"
                    "Pour consulter les commandes disponibles et vérifier vos permissions :\n"
                    " /help\n"
                    "Commande slash seulement. disponible en préfix : !staff(envoyer formulaire poussé) !info(voir le menu ici)\n\n"
                    "⸻\n\n"
                    "✅ Commandes disponibles :\n\n"
                    "・/warn\n"
                    "Permet d’ajouter un avertissement à un membre.\n"
                    "→ Exemple : “Ferme ta gueule t’es qu’une merde” / insultes répétées / non-respect des règles malgré avertissements.\n\n"
                    "・/warns\n"
                    "Affiche le nombre de warns qu’un membre possède.\n"
                    "→ Exemple : Tu veux vérifier l’historique d’un membre avant de sanctionner davantage.\n\n"
                    "・/warnlist\n"
                    "Montre la liste complète de tous les warns du serveur.\n"
                    "→ Exemple : Tu veux faire un suivi global du comportement sur le long terme.\n\n"
                    "・/resetwarns\n"
                    "Réinitialise les warns d’un membre (à utiliser avec justification).\n"
                    "→ Exemple : Un membre s’est calmé depuis longtemps, tu veux lui offrir un nouveau départ.\n\n"
                    "・/mute\n"
                    "Bloque temporairement les messages textuels ou vocaux d’un membre.\n"
                    "→ Exemple : Spam en vocal ou texte, provocations en boucle, gêne dans un canal actif.\n\n"
                    "・/unmute\n"
                    "Retire le mute précédemment appliqué.\n"
                    "→ Exemple : La situation est calmée, ou après la durée définie.\n\n"
                    "・/kick\n"
                    "Expulse un membre sans bannissement total.\n"
                    "→ Exemple : Pub sauvage, comportement déplacé persistant sans gravité extrême.\n\n"
                    "・/ban\n"
                    "Bannit définitivement un membre du serveur.\n"
                    "→ Exemple : Harcèlement, menaces, propos haineux, comportement dangereux.\n\n"
                    "⸻\n\n"
                    "Toutes les actions sont loguées automatiquement dans les logs.\n\n"
                    "⚠️ Au 3e warn, l’utilisateur est automatiquement expulsé du serveur.\n\n"
                    "⸻\n\n"
                    "Merci de respecter ce cadre clair et cohérent.\n"
                    "Chaque action doit être justifiée, réfléchie et mesurée.\n\n"
                    "En cas de doute : contacte un admin ou un fondateur."
                ),
                color=discord.Color.purple()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1102406059722801184/1360320231641186445/C9BCEBC2-B856-4863-A41F-18D195338846.png?ex=67fab070&is=67f95ef0&hm=04f22dd76c28381300dd0ebef9b08768d9a1b8d1720c51c9aa23a8e78d313bb6&")
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif custom_id == "fonctionnement_tickets":
            embed = discord.Embed(
                title="𖥔・Fonctionnement des Tickets – Pour le Staff・𖥔",
                description="""Voici l’organisation des tickets sur le serveur.
Merci de bien lire et de respecter ce fonctionnement pour une gestion claire et efficace.

⸻

✦ Catégorie : Autre demande

▶️ Urgence – <@&1350913347444412416>
▶️ Partenariat – <@&1348428905832513607>
▶️ Autre – <@&1348427864533504102>

⸻

✦ Catégorie : Application au Staff

▶️ Admin – <@&1348427342179074162> & <@&1353167649265160222>
▶️ Modérateur – <@&1348208855263350805>
▶️ Équipe Écoute – <@&1351423658400284703>
▶️ Pro Partenariat – <@&1348427864533504102>

⸻

✧ Règles de gestion des tickets :

• Votre rôle sera mentionné automatiquement lorsque vous êtes concerné.
→ Vous devez répondre en priorité aux tickets qui vous sont adressés.

• Vous êtes décisionnaire complet sur le ticket qui vous concerne.
→ Si vous avez le moindre doute, demandez à votre supérieur direct (pas à un staff du même rôle que vous).

• Un seul membre du staff par ticket.
→ Si un collègue a déjà répondu, ne répondez pas à votre tour sauf si vous êtes explicitement mentionné dans le message.

⸻

✧ Droits spéciaux et hiérarchie :

• Le Owner et le Co-Owner peuvent intervenir ou décider dans n’importe quel ticket, à tout moment.
• Le chef des Admins (aka Le GOAT) a aussi l’autorisation d’intervenir à tout moment.

⸻

✧ Fermeture des tickets :

• Seuls les membres du staff ayant la permission kick_members peuvent fermer un ticket.
→ Si vous ne pouvez pas fermer un ticket, mentionnez le Owner ou le Co-Owner.

⸻

Merci de respecter ces consignes pour garder une gestion propre et fluide.
Chaque ticket est important — traitez-le avec attention, mais aussi avec discernement.
𖥔・La cohésion de l’équipe est la clé du sanctuaire・𖥔""",
                color=discord.Color.purple()
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1102406059722801184/1360321149627793438/CB00DBD1-7546-40FA-9C0D-025E2A008AD0.png?ex=67fab14b&is=67f95fcb&hm=d2283673f55a757a9335b2624f4284c36255e422e551fab2dd017b1d1a8f9aac&=&format=webp&quality=lossless&width=722&height=722")

            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif custom_id == "hierarchie_staff":
            embed = discord.Embed(
                title="𖥔・Organisation du Staff – lonely kurozen・𖥔",
                description="""Voici ce que vous devez savoir concernant la hiérarchie et les permissions de chaque rôle au sein de l’équipe.

⸻

✦ Direction du serveur

<@&1348427342179074162> & <@&1353167649265160222>
→ Fondateurs du serveur. Ils ont autorité sur toutes les décisions et peuvent intervenir dans tous les rôles et tickets.

⸻

✦ Chef des Admins

<@&1360309516746363063>
→ Dispose des permissions administrateur complètes.
→ Peut déclasser un membre du staff (modérateur, apprenti, etc.) en cas de problème.
→ Joue un rôle clé dans la gestion du staff, avec validation directe de certaines décisions d’admin.

⸻

✦ Admins

<@&1348208855263350805>
→ Rôle haut placé avec presque tous les droits, sauf :
\t•\tVoir/Créer/Gérer les salons
\t•\tGérer les webhooks
\t•\tGérer le serveur
\t•\tMentionner @everyone ou tous les rôles

→ Peuvent évaluer si un ou plusieurs modérateurs ne sont pas adaptés à leur poste, mais doivent passer par le Chef des Admins pour toute décision.

⸻

✦ Chef des Modérateurs

<@&1353532487577370624>
→ Détient les permissions clés de modération :
\t•\tKick, Ban, suppression de messages
\t•\tMute vocal/textuel
\t•\tAccès aux salons admin

→ Peut échanger directement avec les admins et supérieurs en cas de doute ou problème concernant un membre du staff.

⸻

✦ Modérateurs

<@&1348427864533504102>
→ Possèdent des permissions similaires au Chef modo, sauf l’accès admin.
→ Sont chargés d’assurer la modération quotidienne.

⸻

✦ Apprenti Staff

<@&1353511135462031472>
→ Permissions limitées : uniquement kick et supprimer des messages.
→ Tous les nouveaux staff (peu importe leur futur rôle) commencent par ce grade.
→ Une phase d’observation est mise en place dès leur intégration à partir du vendredi 11 avril 2025 pour évaluer leur activité et implication.
→ En cas de validation, ils montent en grade vers le rôle adapté.

⸻

✦ Équipe Écoute

→ Le/la Chef d’Écoute est entièrement libre de choisir qui rejoint ou quitte son équipe.
→ Aucune validation externe n’est nécessaire pour sa gestion interne.

⸻

✧ À savoir :

Les autres rôles du serveur n’ont pas de permissions techniques spécifiques.
Ils servent avant tout à structurer, distinguer les fonctions et organiser les tickets/interventions.

⸻

Si quelque chose n’est pas clair ou que tu as un doute sur ton autorité ou ta marge d’action : contacte un supérieur.
La hiérarchie est là pour vous guider, pas vous bloquer.""",
                color=discord.Color.purple()
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1102406059722801184/1360321576943222977/321A9C33-45EF-49F6-817C-73D5F84CAA09.png?ex=67fab1b1&is=67f96031&hm=9b7126f5adf1d9ef716e3093f0ed0779233dd6ccfe10f968fb9f1b45bae3c86d&=&format=webp&quality=lossless&width=722&height=722")

            await interaction.response.send_message(embed=embed, ephemeral=True)

# Extension
async def setup(bot):
    await bot.add_cog(InfoCog(bot))
