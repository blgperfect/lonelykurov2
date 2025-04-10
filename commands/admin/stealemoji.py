import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import re

class EmojiSteal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    async def steal_emojis(self, ctx_or_inter, emojis_raw: str):
        is_slash = isinstance(ctx_or_inter, discord.Interaction)
        if is_slash:
            await ctx_or_inter.response.defer()
            send = ctx_or_inter.followup.send
            guild = ctx_or_inter.guild
        else:
            send = ctx_or_inter.send
            guild = ctx_or_inter.guild

        found = re.findall(r"<a?:\w+:(\d+)>", emojis_raw)
        names = re.findall(r"<a?:(\w+):\d+>", emojis_raw)

        if not found:
            return await send("❌ Aucun emoji personnalisé trouvé.")

        added = []
        for emoji_id, emoji_name in zip(found, names):
            try:
                is_animated = emojis_raw.find(f"<a:{emoji_name}:{emoji_id}>") != -1
                url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{'gif' if is_animated else 'png'}"

                async with self.session.get(url) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.read()

                new_emoji = await guild.create_custom_emoji(name=emoji_name, image=data)
                added.append(f"<:{new_emoji.name}:{new_emoji.id}>")
            except discord.Forbidden:
                return await send("🚫 Je n’ai pas la permission d’ajouter des emojis.")
            except Exception as e:
                print(f"[ERREUR STEAL] {e}")
                continue

        if added:
            await send(f"✅ Emoji(s) ajouté(s) : {' '.join(added)}")
        else:
            await send("❌ Aucun emoji n’a pu être ajouté.")

    # === SLASH ===
    @app_commands.command(name="steal", description="Ajoute un ou plusieurs emojis à ce serveur.")
    @app_commands.describe(emojis="Colle un ou plusieurs emojis personnalisés")
    async def steal_slash(self, interaction: discord.Interaction, emojis: str):
        await self.steal_emojis(interaction, emojis)

    # === PREFIX ===
    @commands.command(name="steal")
    async def steal_prefix(self, ctx: commands.Context, *, emojis: str):
        await self.steal_emojis(ctx, emojis)

# === EXTENSION ===
async def setup(bot):
    await bot.add_cog(EmojiSteal(bot))
