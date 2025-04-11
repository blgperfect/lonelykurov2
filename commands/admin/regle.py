import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Select
from datetime import datetime

# === CONFIG
GENRE_ROLES = {
    "𖥔・Femme": 1348571390491754550,
    "𖥔・Homme": 1348571478173683744,
    "𖥔・Autre genre": 1348571537409572944,
}
ROLE_MEMBER = 1348579462375018529  # 𓃠・Kurozen member

class ReglementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="regles", description="Affiche les règles du serveur avec bouton d'acceptation.")
    @app_commands.checks.has_permissions(administrator=True)
    async def regles_slash(self, interaction: discord.Interaction):
        await self.send_reglement_embed(interaction)

    async def send_reglement_embed(self, ctx_or_inter):
        embed = discord.Embed(
            title="🌙 Bienvenue sur le serveur Lonely (๑╹ω╹๑ )",
            description=(
                "˚　 ⋆⁺₊✦⁺₊ 　 ˚　.˚ .　 ☁.　　. 　 ˚　⁺⋆₊　.˚ .　. ✦⋆⁺₊ 　 ˚　. ☁ ˚　.˚　 ✩₊˚. ☾ ⋆ ⁺₊✧ \n\n"
                "☁️ ˚₊‧⁺ **Règlement des membres** ⁺‧₊˚ ☁️\n"
                "Avant de discuter ou de vous installer, merci de lire les règles ci-dessous avec attention 🫶\n\n"
                "**Respect mutuel**\n"
                "Ce serveur est un espace sûr pour toutes les âmes sensibles.\n"
                "Soyez gentils, bienveillants… avec les autres, et avec vous-même.\n\n"
                "**Zéro haine**\n"
                "Aucun propos raciste, sexiste, homophobe, transphobe ou discriminatoire.\n⚠️ Sanctions immédiates.\n\n"
                "**Vie privée & sécurité**\n"
                "Ne partagez jamais d’infos perso sans consentement. Respect total de l’espace de chacun.\n\n"
                "**Attitude appropriée**\n"
                "Ce serveur est un refuge pour les personnes seules ou en souffrance.\n"
                "🚫 Toute attitude toxique = kick ou ban.\n\n"
                "**Pas de spam ni pub sauvage**\n"
                "Pas de messages répétés, flood ou pub sans autorisation.\n\n"
                "**Besoin d’aide ?**\n"
                "Vous pouvez toujours contacter le staff ou passer par les salons prévus à cet effet 🫂\n\n"
                "**Plaintes privées interdites**\n"
                "Aucune plainte ne doit être envoyée en MP à un staff.\n"
                "➡️ Utilisez les tickets, ou contactez uniquement la fondatrice.\n\n"
                "┊ ➶ ｡˚ ° ✧\n\n"
                "☁️ 🌟 **Pour faire partie du staff :**\n"
                "Vous devez faire partie du serveur depuis au minimum 1 mois.\n"
                "Prenez le temps d’apprendre nos valeurs avant de postuler 💜\n\n"
                "**✦ ˚₊‧⁺ Règlement du staff ⁺‧₊˚ ✦**\n"
                "➤ Discipline et autonomie\n"
                "➤ Pas de conflits internes : restez matures.\n"
                "➤ Aucune plainte privée acceptée → dirigez vers les tickets ou la fondatrice.\n"
                "➤ Sanctions = **preuves obligatoires**.\n"
                "➤ Présence & implication dans le serveur.\n\n"
                "(っ◔◡◔)っ ⭐️ Des questions ?\n"
                "**Contactez-moi ou un membre avec le rôle <@&1348208855263350805> **\n\n"
                "₍ᐢ. .ᐢ₎‧₊˚✩彡\n"
                "**Merci de faire partie de cette famille, on vous aime fort.**"
            ),
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Lonely kurozen System | Règlement")
        embed.set_image(url="https://cdn.discordapp.com/attachments/1102406059722801184/1359646879217881100/5B2B6AEC-6688-465B-B1FE-6E8415CEF3FE.png?ex=67f83d55&is=67f6ebd5&hm=bfe3103a5cf36ffb1e126e34b83aa5e1e4b00281f1b56dd2bb7d1c507fc507b3&")

        view = AcceptRulesView()
        if isinstance(ctx_or_inter, commands.Context):
            await ctx_or_inter.send(embed=embed, view=view)
        else:
            await ctx_or_inter.response.send_message(embed=embed, view=view)

# === VUE & ACTION BOUTON ACCEPTATION ===

class AcceptRulesView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ J'accepte", style=discord.ButtonStyle.success)
    async def accept_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "Merci d’avoir accepté les règles !\nVeuillez sélectionner votre genre : \n **Pour les autre roles on se retrouve ici** : <#1348421343296618568> ", 
            view=GenderSelectionView(), ephemeral=True
        )

# === VUE SÉLECTION DE GENRE ===

class GenderSelectionView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GenderSelect())

class GenderSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=str(role_id)) for label, role_id in GENRE_ROLES.items()
        ]
        super().__init__(placeholder="Choisis ton genre...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        selected_role_id = int(self.values[0])
        member = interaction.user
        guild = interaction.guild

        genre_role = guild.get_role(selected_role_id)
        base_role = guild.get_role(ROLE_MEMBER)

        await member.add_roles(genre_role)
        await member.add_roles(base_role)

        await interaction.response.send_message(
            "🎉 Merci d'avoir accepté le règlement ! Vous avez maintenant accès au serveur ✨", ephemeral=True
        )

# === EXTENSION ===

async def setup(bot):
    await bot.add_cog(ReglementCog(bot))
