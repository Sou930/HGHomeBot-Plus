import os
import discord
from discord.ext import commands
import aiohttp

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "moonshotai/kimi-k2"

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Bot自身は無視
        if message.author.bot:
            return

        is_mention = self.bot.user in message.mentions
        is_reply = (
            message.reference
            and isinstance(message.reference.resolved, discord.Message)
            and message.reference.resolved.author == self.bot.user
        )

        # メンション or Botへの返信 以外は無視
        if not is_mention and not is_reply:
            return

        # メンションを除去
        content = message.content.replace(f"<@{self.bot.user.id}>", "").strip()

        # 空なら何もしない
        if not content:
            return

        await message.channel.typing()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    OPENROUTER_URL,
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://discord.com",
                        "X-Title": "Discord KimiK2 Bot"
                    },
                    json={
                        "model": MODEL_NAME,
                        "messages": [
                            {
                                "role": "system",
                                "content": "あなたは親しみやすくフレンドリーなAIです。"
                            },
                            {
                                "role": "user",
                                "content": content
                            }
                        ],
                        "temperature": 0.7
                    },
                    timeout=aiohttp.ClientTimeout(total=50)
                ) as resp:

                    if resp.status != 200:
                        await message.reply(
                            "⌛ AIの応答が遅すぎます…\n"
                            "少し待ってからもう一回試してください"
                        )
                        return

                    data = await resp.json()
                    reply = data["choices"][0]["message"]["content"]

        except aiohttp.TimeoutError:
            await message.reply(
                "⌛ AIの応答が遅すぎます…\n"
                "少し待ってからもう一回試してください"
            )
            return

        except aiohttp.ClientError:
            await message.reply("❌ 通信エラーが起きました")
            return

        # Discord文字数制限対策
        if len(reply) > 2000:
            reply = reply[:1990] + "…"

        await message.reply(reply)

async def setup(bot):
    await bot.add_cog(AI(bot))
