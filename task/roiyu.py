import discord
from discord.ext import commands
import random

class Roiyu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_user_id = 983420447985123408  # Remplace par l'ID du membre ciblé

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if any(mention.id == self.target_user_id for mention in message.mentions) and not message.reference:
            responses = [
                {
                    "title": "♛ Audience refusée",
                    "desc": (
                        "Vous avez osé appeler <@{id}> sans autorisation.\n"
                        "Le Seigneur des Ombres siège sur son trône, insensible aux plaintes du royaume."
                    )
                },
                {
                    "title": "🪦 Il ne descend pas de son trône pour si peu",
                    "desc": (
                        "<@{id}> est occupé à juger les mortels depuis son siège.\n"
                        "Tente encore, et peut-être qu’un regard te sera accordé."
                    )
                },
                {
                    "title": "⛓️ Membre enchaîné",
                    "desc": (
                        "Impossible de contacter <@{id}>. Des chaînes d’ombres le retiennent dans un autre plan."
                    )
                },
                {
                    "title": "👁️ Il vous a vu, mais ne répondra pas",
                    "desc": (
                        "Un regard froid vous traverse. <@{id}> ne juge pas cette mention digne d'une réponse."
                    )
                }
            ]

            choice = random.choice(responses)

            embed = discord.Embed(
                title=choice["title"],
                description=choice["desc"].format(id=self.target_user_id),
                color=discord.Color.dark_red()
            )

            # Affiche l'image en haut à droite (icône mini)
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1351165531591409705/1354286956506255361/6D9B6E98-7A1F-46CF-96B9-9E2CDB969521.jpg?ex=67e4bd83&is=67e36c03&hm=f080db311c26d482cc728584e8301047d22e306682ee68cc26f820fb671128cb&")

            embed.set_footer(text="Seuls les élus peuvent oser réclamer son attention...")

            sent_msg = await message.channel.send(embed=embed)
            await sent_msg.add_reaction("❌")

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Roiyu(bot))