import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import zoneinfo
import datetime
from discord.ext import commands,tasks
from aiohttp import web 

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

TimeZone = zoneinfo.ZoneInfo("Asia/Kolkata")
PollTime = datetime.time(hour=9,minute=0,second=0, tzinfo=TimeZone)
ChannelID = 1554002252451024939

async def handle_ping(request):
    return web.Response(text="Bot is online and running 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")



@tasks.loop(time=PollTime)
async def day_poll():
    today = datetime.datetime.now(TimeZone).weekday()
    if today not in (1,2):
        return
    if today==1:
        channel = bot.get_channel(ChannelID)
        if not channel:
            try:
                channel = await bot.fetch_channel(ChannelID)
            except Exception as e:
                print(f"Failed to fetch channel: {e}")
                return
        poll = discord.Poll(
            question="Choose day for our call",
            duration=datetime.timedelta(hours=24),  # Poll duration (max 168 hours / 7 days)
            multiple=True,  # Set to True to allow selecting multiple options
        )

        poll.add_answer(text="Friday")
        poll.add_answer(text="Saturday")
        poll.add_answer(text="Sunday")
    elif today==2:
        channel = bot.get_channel(ChannelID)
        if not channel:
            try:
                channel = await bot.fetch_channel(ChannelID)
            except Exception as e:
                print(f"Failed to fetch channel: {e}")
                return
        poll = discord.Poll(
            question="Choose time",
            duration=datetime.timedelta(hours=24),  # Poll duration (max 168 hours / 7 days)
            multiple=True,  # Set to True to allow selecting multiple options
                )
        
        poll.add_answer(text="10 a.m.")
        poll.add_answer(text="3 p.m.")
        poll.add_answer(text="6 p.m.")
        poll.add_answer(text="9 p.m.")
    await channel.send(poll=poll)

@bot.command(name="testpoll")
async def test_poll(ctx):
    """Triggers a poll on demand for testing."""
    poll = discord.Poll(
        question="[TEST] Tuesday Poll: What is your primary focus today?",
        duration=datetime.timedelta(hours=1),
        multiple=False,
    )
    poll.add_answer(text="Building new features", emoji="🚀")
    poll.add_answer(text="Fixing bugs & refactoring", emoji="🛠️")
    poll.add_answer(text="Documentation & planning", emoji="📝")

    await ctx.send(poll=poll)
    await ctx.send("✅ Poll test successful!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    # Start the scheduled task loop if it's not already running
    if not day_poll.is_running():
        day_poll.start()


bot.run(token=token, log_handler=handler, log_level=logging.DEBUG)