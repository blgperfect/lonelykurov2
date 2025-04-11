import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime

# === Thèmes visuels ===
COLOR = discord.Color.from_str("#C9B6D9")
IMAGE_URL = "https://cdn.discordapp.com/attachments/1102406059722801184/1359642804053213377/3BDD3BFA-0CA4-493A-8B7A-D4C8ED0E6F5D.png?ex=67f83989&is=67f6e809&hm=6848f54c58c843fb8fdffe6ed313d907957246427e0d9339445f1a180012539b&"

# === Rôles mis à jour ===
COLOR_ROLES = {
    "🍃 Verte Éthérée": 1359631149680300104,
    "🫧 Mist Quartz": 1359630409251553421,
    "🌝 Jaune Rosa": 1359631891388563671,
    "🌸 Dream Lilac": 1359630111304978594,
    "💜 Void Améthyste": 1359630027813163213,
    "🔥 Glow Ember": 1359631551524110446,
    "🌞 Soleil Vénéneux": 1359631420925935636,
    "🌠 Starlight Mauve": 1359630751280140460,
    "🪐 Moon Dust": 1359630929567682591,
    "🧊 Glacier Spirit": 1359631662933348473,
    "🍓 Berry Eclipse": 1359631769779044382,
    "🌅 Rose Astral": 1359631312692183221,
    "🌫️ Ash Lavender": 1359630519590977626,
    "🔮 Arcane Plum": 1359630662512017438,
    "🌊 Echo Blue": 1359630998173646979,
    "🌑 Nebula Noir": 1359630256671293632,
}

SUPPLEMENTAIRES = {
    "✿・Survivant": 1348495255921754123,
    "✿・Âme Perdue": 1348483342563016725,
    "✿・Veilleur de nuit": 1348483742582308925,
    "✿・Coeur Brisé": 1348483880193232906,
    "✿・Lumiere dans l’ombre": 1348484004533239818,
    "✿・Âme créatrice": 1348484297496989727,
}

IDENTITE = {
    "𖥔・Mineur": 1348571234589347891,
    "𖥔・Majeur": 1348571322350833715,
    "𖥔・Célibataire": 1348571888233877556,
    "𖥔・Dating": 1348571966868688997,
    "𖥔・En couple": 1348572081398222898,
}

PING = {
    "☁・Annonce": 1348573200702898220,
    "☁・Dit Bonjour": 1348573308609888276,
    "☁・Nouvelle Confession": 1348573569440940052,
    "☁・Giveaways": 1348573647236759582,
    "☁・HEILLE ON VOC?": 1355261618656645422,
    "☁・Défi Personnelle": 1348574553735041046,
    "☁・Film du soir!": 1348576508716908604,
    "☁・Partenariat": 1353155776058753154,
    "☁・Challenge guérison": 1348576800451596288,
    "☁・Events": 1348579313959829535,
    "☁・Faut Parler": 1348584464170881095,
    "☁・Bump jtai dit": 1358530275209904249,
    "☁・Je m’ennuie": 1351317946806304886,
}

PERSONNALITE = {
    "⭑・Mp fermés": 1350763480562794548,
    "⭑・Mp sur demandes": 1350763538628743168,
    "⭑・Mp ouverts": 1350763438481084487,
    "⭑・Europe": 1350762939942178848,
    "⭑・Amérique": 1350763031176413276,
    "⭑・Asie": 1350763093877198878,
    "⭑・Afrique": 1350763129876906030,
    "⭑・Océanie": 1350763177758949397,
}

STYLE_ROLES = {
    "𖥔𓈒˚ 𝐑𝐎𝐋𝐄 𝐂𝐎𝐔𝐋𝐄𝐔𝐑𝐒 ˚𓈒𖥔": 1359629596902949076,
    "𖥔𓈒˚ 𝐑𝐎𝐋𝐄 𝐋𝐄𝐕𝐄𝐋𝐒 ˚𓈒𖥔": 1354922574747926700,
    "𖥔𓈒˚ 𝐑𝐎𝐋𝐄 𝐑𝐄𝐂𝐎𝐌𝐏𝐄𝐍𝐒𝐄𝐒 ˚𓈒𖥔": 1348429716645740554,
    "𖥔𓈒˚ 𝐑𝐎𝐋𝐄 𝐒𝐔𝐏𝐏𝐋𝐄𝐌𝐄𝐍𝐓𝐀𝐈𝐑𝐄𝐒 ˚𓈒𖥔": 1348483153467281558,
    "𖥔𓈒˚ 𝐑𝐎𝐋𝐄𝐒 𝐈𝐃𝐄𝐍𝐓𝐈𝐓É ˚𓈒𖥔": 1348571108374478950,
    "𖥔𓈒˚ 𝐑𝐎𝐋𝐄 𝐏𝐈𝐍𝐆 ˚𓈒𖥔": 1348573093408407562,
    "𖥔𓈒˚ 𝐑𝐎𝐋𝐄 𝐏𝐄𝐑𝐒𝐎𝐍𝐀𝐋𝐋𝐈𝐓É ˚𓈒𖥔": 1350905549679628419,
}

# === Suite dans le Bloc 2/2 : Vues et commandes ===

# === BOUTONS ===

class ExclusiveButton(Button):
    def __init__(self, label, role_id, all_ids):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.role_id = role_id
        self.all_ids = all_ids

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild = interaction.guild
        selected = guild.get_role(self.role_id)

        # Enlever les autres rôles de la catégorie exclusive
        for rid in self.all_ids:
            role = guild.get_role(rid)
            if role in member.roles and role.id != self.role_id:
                await member.remove_roles(role)

        # Toggle le rôle sélectionné
        if selected in member.roles:
            await member.remove_roles(selected)
            msg = f"❌ **{selected.name}** retiré."
        else:
            await member.add_roles(selected)
            msg = f"✅ **{selected.name}** attribué !"

        await interaction.response.send_message(msg, ephemeral=True)


class MultiRoleButton(Button):
    def __init__(self, label, role_id):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        role = interaction.guild.get_role(self.role_id)

        if role in member.roles:
            await member.remove_roles(role)
            msg = f"❌ **{role.name}** retiré."
        else:
            await member.add_roles(role)
            msg = f"✅ **{role.name}** attribué !"

        await interaction.response.send_message(msg, ephemeral=True)

# === VUES ===

class ColorRolesView(View):
    def __init__(self):
        super().__init__(timeout=None)
        role_ids = list(COLOR_ROLES.values())
        for name, role_id in COLOR_ROLES.items():
            self.add_item(ExclusiveButton(name, role_id, role_ids))

class MultiRoleView(View):
    def __init__(self, roles_dict):
        super().__init__(timeout=None)
        for name, role_id in roles_dict.items():
            self.add_item(MultiRoleButton(name, role_id))

class StyleRolesView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for name, role_id in STYLE_ROLES.items():
            self.add_item(MultiRoleButton(name, role_id))

# === VUE PRINCIPALE ===

class MainRoleView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎨 Rôles Couleurs", style=discord.ButtonStyle.primary)
    async def couleur(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Choisis une couleur :", view=ColorRolesView(), ephemeral=True)

    @discord.ui.button(label="🌟 Supplémentaires", style=discord.ButtonStyle.primary)
    async def supp(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Choisis tes rôles :", view=MultiRoleView(SUPPLEMENTAIRES), ephemeral=True)

    @discord.ui.button(label="🪪 Identité", style=discord.ButtonStyle.primary)
    async def identite(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Qui es-tu ?", view=MultiRoleView(IDENTITE), ephemeral=True)

    @discord.ui.button(label="🔔 Ping", style=discord.ButtonStyle.primary)
    async def ping(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Choisis tes pings :", view=MultiRoleView(PING), ephemeral=True)

    @discord.ui.button(label="🧠 Personnalité", style=discord.ButtonStyle.primary)
    async def perso(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Rôles de personnalité :", view=MultiRoleView(PERSONNALITE), ephemeral=True)

    @discord.ui.button(label="🎀 Style", style=discord.ButtonStyle.secondary)
    async def style(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Juste pour le style :", view=StyleRolesView(), ephemeral=True)

# === COMMANDE PRINCIPALE ===

class RoleSetupCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rolesetup", description="Affiche le panneau des rôles interactifs.")
    @app_commands.checks.has_permissions(administrator=True)
    async def rolesetup_slash(self, interaction: discord.Interaction):
        await self.send_roles_embed(interaction)

    async def send_roles_embed(self, ctx_or_inter):
        embed = discord.Embed(
            title="𓈒𖥔˚｡˖ 𝐑𝐎𝐋𝐄𝐒 𝐈𝐍𝐓𝐄𝐑𝐀𝐂𝐓𝐈𝐅𝐒 ˖ ࣪⭑",
            description="**Clique pour sélectionner tes rôles ci-dessous.**",
            color=COLOR,
            timestamp=datetime.utcnow()
        )
        embed.set_image(url=IMAGE_URL)
        embed.set_footer(text="Kurozen Role System")

        view = MainRoleView()
        if isinstance(ctx_or_inter, commands.Context):
            await ctx_or_inter.send(embed=embed, view=view)
        else:
            await ctx_or_inter.response.send_message(embed=embed, view=view)

# === EXTENSION ===

async def setup(bot):
    await bot.add_cog(RoleSetupCommand(bot))
