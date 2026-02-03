import discord
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="ヘルプを表示します")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="ℹ️ ヘルプ",
            color=discord.Color.green()
        )

        embed.add_field(
            name="🔍 YouTube検索",
            value="/youtube title:キーワード … YouTubeの動画を検索します（使用制限あり）",
            inline=False
        )

        embed.add_field(
            name="🔴 タイムアウト（管理者）",
            value="/timeout user:@ユーザー duration:10 … 指定時間タイムアウトします",
            inline=False
        )

        embed.add_field(
            name="🔴 ロール付与（管理者）",
            value="/giverole user:@ユーザー role:Moderator … ロールを付与します",
            inline=False
        )

        embed.set_footer(text="HGHomeBot v0.1")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
