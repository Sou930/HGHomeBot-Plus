import discord
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="ヘルプを表示します")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="ℹ️ヘルプ",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Youtube検索",
            value=(
                "/youtube title: … Youtubeの動画を検索します、一日の使用制限あり...\n"
            ),
            name="🔴タイムアウト",
            value=(
                "/timeout user:Sou930 duration:10 … タイムアウトをします\n"
            ),
            name="🔴ロール付与",
            value=(
                "/giverole user:Sou930 role:Moderator …ロール付与をします
            inline=False
        )

        embed.set_footer(text="HGHomeBot v0.1")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
