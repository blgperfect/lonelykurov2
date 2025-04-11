import discord
from discord.ext import commands
from discord import app_commands
from help_data import CATEGORIES

# === Bouton "Accueil" uniquement ===
class HomeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Menu principal", style=discord.ButtonStyle.secondary, emoji="🏠", custom_id="home")

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📖 Kurozen - Menu d'aide",
            description="Voici la liste complète des commandes disponibles. Utilisez le menu déroulant pour naviguer par catégorie.",
            color=discord.Color.dark_purple()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1102406059722801184/1360120382203498516/718AAA6C-670B-4B53-8F5C-5CFCF965A134.png?ex=67f9f650&is=67f8a4d0&hm=ade97e3b7f4c4acd1327be28e6e107a0dc214436a466337f4a9ba82fb103c627&")
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        embed.set_footer(text="Kurozen • Ton assistant multifonction", icon_url=interaction.client.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=HelpView())

# === Sélecteur de commande dans une catégorie ===
class CommandSelect(discord.ui.Select):
    def __init__(self, category: str):
        options = [
            discord.SelectOption(label=cmd, value=cmd)
            for cmd in CATEGORIES[category]
        ]
        super().__init__(placeholder="Choisissez une commande à afficher", options=options)
        self.category = category

    async def callback(self, interaction: discord.Interaction):
        cmd = self.values[0]
        detail = CATEGORIES[self.category][cmd]
        embed = discord.Embed(
            title=f"Détail : {cmd}",
            description=detail,
            color=discord.Color.green()
        )
        embed.set_footer(text="Kurozen • Menu d'aide", icon_url=interaction.client.user.display_avatar.url)

        view = HelpView()
        view.add_item(CommandSelect(category=self.category))
        view.add_item(HomeButton())
        await interaction.response.edit_message(embed=embed, view=view)

# === Menu déroulant des catégories ===
class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=label,
                value=label,
                description=f"Voir les commandes dans {label}",
                emoji=label[0]
            )
            for label in CATEGORIES
        ]
        super().__init__(placeholder="Choisissez une catégorie", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        commands_list = " ".join([f"`{cmd}`" for cmd in CATEGORIES[selected]])

        embed = discord.Embed(
            title=f"{selected} - Commandes disponibles",
            description=f"**Commandes :**\n{commands_list}\n\nSélectionnez une commande ci-dessous pour voir sa description détaillée.",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Kurozen • Menu d'aide", icon_url=interaction.client.user.display_avatar.url)

        view = HelpView()
        view.add_item(CommandSelect(category=selected))
        view.add_item(HomeButton())
        await interaction.response.edit_message(embed=embed, view=view)

# === Vue simplifiée avec uniquement le select et bouton accueil ===
class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HelpSelect())

# === COG Principal ===
class HelpMenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Affiche toutes les commandes de Kurozen avec catégories")
    async def help_slash(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📖 Kurozen - Menu d'aide",
            description="Voici la liste complète des commandes disponibles. Utilisez le menu déroulant pour naviguer par catégorie.",
            color=discord.Color.dark_purple()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1102406059722801184/1360120382203498516/718AAA6C-670B-4B53-8F5C-5CFCF965A134.png?ex=67f9f650&is=67f8a4d0&hm=ade97e3b7f4c4acd1327be28e6e107a0dc214436a466337f4a9ba82fb103c627&")
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        embed.set_footer(text="Kurozen • Ton assistant multifonction", icon_url=interaction.client.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, view=HelpView(), ephemeral=False)

# === Charger le COG ===
async def setup(bot: commands.Bot):
    await bot.add_cog(HelpMenu(bot))
