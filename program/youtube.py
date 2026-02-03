import os
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

YOUTUBE_KEY = os.environ.get("YOUTUBE_KEY")

class YouTubeView(discord.ui.View):
    def __init__(self, videos, stats_map, user):
        super().__init__(timeout=60)
        self.videos = videos
        self.stats_map = stats_map
        self.index = 0
        self.user = user

    def make_embed(self):
        item = self.videos[self.index]
        snippet = item["snippet"]
        video_id = item["id"]["videoId"]
        stats = self.stats_map.get(video_id, {})

        view = int(stats.get("viewCount", 0))
        like = int(stats.get("likeCount", 0))

        embed = discord.Embed(
            title=snippet["title"],
            url=f"https://www.youtube.com/watch?v={video_id}",
            description=(
                f"📺 {snippet['channelTitle']}\n"
                f"👀 再生数: {view:,}\n"
                f"👍 高評価: {like:,}"
            ),
            color=0xff0000
        )
        embed.set_thumbnail(url=snippet["thumbnails"]["high"]["url"])
        embed.set_footer(text=f"{self.index + 1} / {len(self.videos)}")
        return embed

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.user

    @discord.ui.button(label="◀ 前", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index - 1) % len(self.videos)
        await interaction.response.edit_message(
            embed=self.make_embed(),
            view=self
        )

    @discord.ui.button(label="次 ▶", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index + 1) % len(self.videos)
        await interaction.response.edit_message(
            embed=self.make_embed(),
            view=self
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

class YouTube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="youtube",
        description="YouTube検索（ボタンUI・統計付き）"
    )
    @app_commands.describe(title="検索する動画タイトル")
    async def youtube(self, interaction: discord.Interaction, title: str):
        await interaction.response.defer()

        try:
            async with aiohttp.ClientSession() as session:
                # 検索
                search_resp = await session.get(
                    "https://www.googleapis.com/youtube/v3/search",
                    params={
                        "part": "snippet",
                        "q": title,
                        "type": "video",
                        "maxResults": 10,
                        "key": YOUTUBE_KEY
                    }
                )

                if search_resp.status == 403:
                    await interaction.followup.send(
                        "🚨 YouTube APIの利用上限に達しました…\n"
                        "しばらく時間を置いてから試してください"
                    )
                    return

                search_data = await search_resp.json()
                videos = search_data.get("items", [])

                if not videos:
                    await interaction.followup.send("🔍 見つかりませんでした")
                    return

                video_ids = ",".join(v["id"]["videoId"] for v in videos)

                # 統計
                stats_resp = await session.get(
                    "https://www.googleapis.com/youtube/v3/videos",
                    params={
                        "part": "statistics",
                        "id": video_ids,
                        "key": YOUTUBE_KEY
                    }
                )

                if stats_resp.status == 403:
                    await interaction.followup.send(
                        "🚨 API上限に達してて統計情報が取れません…"
                    )
                    return

                stats_data = await stats_resp.json()

        except aiohttp.ClientError:
            await interaction.followup.send("❌ 通信エラーが起きました")
            return

        stats_map = {
            item["id"]: item["statistics"]
            for item in stats_data.get("items", [])
        }

        view = YouTubeView(videos, stats_map, interaction.user)
        await interaction.followup.send(
            embed=view.make_embed(),
            view=view
        )

async def setup(bot):
    await bot.add_cog(YouTube(bot))
