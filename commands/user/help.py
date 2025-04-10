import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select
import os
from pathlib import Path

class HelpView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=60)
        self.bot = bot
        self.add_item(PrefixButton(bot))
        self.add_item(SlashButton(bot))

def get_category_from_path(path: str):
    try:
        # path: /path/to/commands/modo/warn.py → retourne 'modo'
        parts = Path(path).parts
        idx = parts.index("commands")
        return parts[idx + 1]
    except Exception:
        return "Autres"

class PrefixButton(Button):
    def __init__(self, bot):
        super().__init__(label="📘 Préfixe", style=discord.ButtonStyle.primary)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        cmds = [cmd for cmd in self.bot.commands if not cmd.hidden]
        categories = {}
        for cmd in cmds:
            path = getattr(cmd.callback.__code__, 'co_filename', None)
            category = get_category_from_path(path) if path else "Autres"
            categories.setdefault(category, []).append(cmd)

        view = View(timeout=60)
        view.add_item(PrefixSelect(categories))
        await interaction.response.send_message(
            embed=discord.Embed(title="📘 Commandes Préfixe", description="Choisis une catégorie :", color=discord.Color.blue()),
            view=view,
            ephemeral=True
        )

class SlashButton(Button):
    def __init__(self, bot):
        super().__init__(label="📗 Slash", style=discord.ButtonStyle.success)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        cmds = self.bot.tree.get_commands()
        categories = {}
        for cmd in cmds:
            if hasattr(cmd.callback, '__code__'):
                path = cmd.callback.__code__.co_filename
                category = get_category_from_path(path)
                categories.setdefault(category, []).append(cmd)

        view = View(timeout=60)
        view.add_item(SlashSelect(categories))
        await interaction.response.send_message(
            embed=discord.Embed(title="📗 Commandes Slash", description="Choisis une catégorie :", color=discord.Color.green()),
            view=view,
            ephemeral=True
        )

class PrefixSelect(Select):
    def __init__(self, categories: dict):
        options = [discord.SelectOption(label=c, value=c) for c in categories]
        super().__init__(placeholder="Catégorie (préfixe)...", options=options, min_values=1, max_values=1)
        self.categories = categories

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        cmds = self.categories[category]
        embed = discord.Embed(
            title=f"📘 {category}",
            description=f"Commandes prefix dans `{category}` :",
            color=discord.Color.blue()
        )
        for cmd in cmds:
            embed.add_field(name=f"!{cmd.name}", value=cmd.help or "Aucune description", inline=False)
        await interaction.response.edit_message(embed=embed, view=None)

class SlashSelect(Select):
    def __init__(self, categories: dict):
        options = [discord.SelectOption(label=c, value=c) for c in categories]
        super().__init__(placeholder="Catégorie (slash)...", options=options, min_values=1, max_values=1)
        self.categories = categories

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        cmds = self.categories[category]
        embed = discord.Embed(
            title=f"📗 {category}",
            description=f"Commandes slash dans `{category}` :",
            color=discord.Color.green()
        )
        for cmd in cmds:
            embed.add_field(name=f"/{cmd.name}", value=cmd.description or "Aucune description", inline=False)
        await interaction.response.edit_message(embed=embed, view=None)

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_prefix(self, ctx):
        embed = discord.Embed(
            title="📖 Menu d'aide",
            description="Bienvenue dans le menu d'aide.\nChoisis entre préfixe ou slash :",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed, view=HelpView(self.bot))

    @app_commands.command(name="help", description="Afficher le menu d’aide du bot")
    async def help_slash(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📖 Menu d'aide",
            description="Bienvenue dans le menu d'aide.\nChoisis entre préfixe ou slash :",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=HelpView(self.bot), ephemeral=True)

# === Setup
async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCommand(bot))
