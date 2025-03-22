import asyncio
import discord
import time
import re
import os
from discord.ext import commands
from discord.gateway import DiscordWebSocket
cooldown_messages = {}
message_timestamps = {}
group_cooldowns = {}
GLOBAL_COOLDOWN_MESSAGES = {
    "user": "{}: you are on cooldown, ends",
    "guild": "{}: this command is on cooldown, ends"
}
def group_cool(bucket_type, tries, seconds):
    def decorator(func):
        active_messages = {}

        async def wrapper(ctx, *args, **kwargs):
            key = f"{ctx.command.name}:{ctx.author.id if bucket_type == 'user' else ctx.guild.id if ctx.guild else ctx.author.id}"
            current_time = time.time()
            if key in group_cooldowns:
                elapsed = current_time - group_cooldowns[key]
                if elapsed < seconds:
                    if key not in active_messages:
                        cooldown_end = group_cooldowns[key] + seconds + 1
                        msg_template = GLOBAL_COOLDOWN_MESSAGES["guild"] if bucket_type == "guild" else GLOBAL_COOLDOWN_MESSAGES["user"]
                        embed = discord.Embed(description=f"> ⏱️ {msg_template.format(ctx.author.mention)} <t:{int(cooldown_end)}:R>", color=0x2F3136)
                        cooldown_message = await ctx.send(embed=embed)
                        active_messages[key] = cooldown_message
                        await asyncio.sleep(2)
                        try:
                            await cooldown_message.delete()
                            del active_messages[key]
                        except discord.NotFound:
                            pass
                    return
            group_cooldowns[key] = current_time
            return await func(ctx, *args, **kwargs)

        return wrapper
    return decorator
def cool(bucket_type, tries, seconds, ignore=None, custom_messages=None):
    def decorator(func):
        cooldowns = {}
        active_messages = {}
        async def wrapper(ctx, *args, **kwargs):
            key = ctx.author.id if bucket_type == "user" else ctx.guild.id if ctx.guild else ctx.author.id
            command_key = f"{key}_{ctx.command.name}"
            if ignore and callable(ignore) and ignore(ctx):
                return await func(ctx, *args, **kwargs)
            current_time = time.time()
            if key in cooldowns:
                elapsed_time = current_time - cooldowns[key]['timestamp']
                if elapsed_time < seconds:
                    if key not in active_messages:
                        retry_after = seconds - elapsed_time
                        messages = custom_messages or GLOBAL_COOLDOWN_MESSAGES
                        msg_template = messages["guild"] if bucket_type == "guild" else messages["user"]
                        cooldown_end = cooldowns[key]['timestamp'] + seconds + 1  # +1 to prevent "1 second ago"
                        embed = discord.Embed(description=f"> ⏱️ {msg_template.format(ctx.author.mention)} <t:{int(cooldown_end)}:R>", color=0x2F3136)
                        cooldown_message = await ctx.send(embed=embed)
                        active_messages[key] = cooldown_message
                        await asyncio.sleep(2)
                        try:
                            await cooldown_message.delete()
                            del active_messages[key]
                        except discord.NotFound:
                            pass
                    return
                else:
                    del cooldowns[key]
            result = await func(ctx, *args, **kwargs)
            cooldowns[key] = {'timestamp': current_time}
            return result
        return wrapper
    return decorator
async def mobile_identify(self):
    payload = {
        "op": self.IDENTIFY,
        "d": {
            "token": self.token,
            "properties": {
                "$os": "Discord iOS",
                "$browser": "Discord iOS",
                "$device": "iOS",
                "$referrer": "",
                "$referring_domain": "",
            },
            "compress": True,
            "large_threshold": 250,
        },
    }
    if self.shard_id is not None and self.shard_count is not None:
        payload["d"]["shard"] = [self.shard_id, self.shard_count]
    state = self._connection
    if state._intents is not None:
        payload["d"]["intents"] = state._intents.value
    await self.call_hooks("before_identify", self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)
DiscordWebSocket.identify = mobile_identify
class BucketType:
    user = "user"
    guild = "guild"
class Cooldown:
    def __init__(self, rate, per, type):
        self.rate = rate
        self.per = per
        self.type = type
class CommandOnCooldown(Exception):
    def __init__(self, retry_after, cooldown):
        self.retry_after = retry_after
        self.cooldown = cooldown
class Saint(commands.Bot):
    def __init__(self, prefix=",", blacklist=None):
        self.blacklist = blacklist
        self.processed_edits = {}
        self.blacklisted_words = []
        self.blacklist_pattern = None
        intents = discord.Intents.all()
        super().__init__(command_prefix=prefix, intents=intents, case_insensitive=True, help_command=None)
        self.add_listener(self.on_command_error, 'on_command_error')
        self.add_listener(self.on_message_edit, 'on_message_edit')
        self.load_blacklisted_words()
    def load_blacklisted_words(self):
        try:
            if os.path.exists("data/black.txt"):
                with open("data/black.txt", "r", encoding="utf-8") as f:
                    self.blacklisted_words = [line.strip() for line in f.readlines() if line.strip()]
            else:
                self.blacklisted_words = ["nigger", "nigga"]
                os.makedirs("data", exist_ok=True)
                with open("data/black.txt", "w", encoding="utf-8") as f:
                    f.write("\n".join(self.blacklisted_words))
            if self.blacklisted_words:
                self.blacklist_pattern = re.compile(r'\b(' + '|'.join(map(re.escape, self.blacklisted_words)) + r')\b', re.IGNORECASE)
            else:
                self.blacklist_pattern = None
            print(f"Loaded {len(self.blacklisted_words)} blacklisted words")
        except Exception as e:
            print(f"Error loading blacklisted words: {e}")
            self.blacklisted_words = ["nigger", "nigga"]
            self.blacklist_pattern = re.compile(r'\b(' + '|'.join(map(re.escape, self.blacklisted_words)) + r')\b', re.IGNORECASE)
    async def contains_blacklisted_word(self, content):
        if not content or not self.blacklist_pattern:
            return False
        return bool(self.blacklist_pattern.search(content))
    async def on_message_edit(self, before, after):
        if before.content == after.content:
            return
        if (after.edited_at.timestamp() - before.created_at.timestamp()) > 30:
            return
        edit_key = f"{after.channel.id}_{after.id}"
        if edit_key in self.processed_edits:
            return
        try:
            self.processed_edits[edit_key] = time.time()
            asyncio.create_task(self._clear_processed_edit(edit_key, 60))
            ctx = await self.get_context(after)
            if ctx.valid and ctx.command:
                await ctx.reinvoke()
        except Exception as e:
            print(f"Error processing edited message: {e}")
    async def _clear_processed_edit(self, key, delay):
        await asyncio.sleep(delay)
        if key in self.processed_edits:
            del self.processed_edits[key]
    async def on_ready(self):
        print(f"Bot is ready as {self.user}")
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.CustomActivity(name="🔗 discord.gg/saint")
        )
    async def process_commands(self, message):
        if self.blacklist and await self.blacklist(message.author):
            return
        try:
            if message.content and await self.contains_blacklisted_word(message.content):
                await message.channel.send("😐")
                return
        except Exception as e:
            print(f"Error checking blacklisted words: {e}")
        await super().process_commands(message)
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after = error.retry_after
            embed = discord.Embed(
                description=f"> ⏱️ {ctx.author.mention}: this commanmdnddd",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
    def cmd(self, **kwargs):
        def decorator(func):
            cooldown = kwargs.pop('cool', None)
            if cooldown:
                amount, per, bucket = cooldown
                func = cool(bucket, amount, per)(func)
            command = commands.Command(func, **kwargs)
            self.add_command(command)
            return func
        return decorator
__all__ = ['Saint', 'cool', 'group_cool']
