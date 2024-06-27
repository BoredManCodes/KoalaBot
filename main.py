"""
The main file for KoalaBot, a Discord general utility bot.

This file is the entry point for the bot, and contains the main loop for the bot.

Written by: Trent Buckley (BoredManPlays)
"""

from interactions import slash_command, SlashContext, Embed, Intents, Client, listen, InteractionContext
import logging
import dotenv

# Read the token from the .env file
dotenv.load_dotenv()
TOKEN = dotenv.get_key(".env", "TOKEN")


# Set up the logging
logging.basicConfig(filename="bot.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Set up the bot
bot = Client(intents=Intents.ALL)


# Send a message when the on ready event is called
@listen()
async def on_ready():
    print(f"Bot Information\n---------------\nBot Owner: {bot.owner}\nBot Name: {bot.user.display_name}")


@slash_command(name="ping", description="Shows the bot's ping in ms.")
async def ping(ctx: SlashContext):
    latency = round(int(bot.latency * 1000))  # Calculate the bots latency
    await ctx.send(f"Pong! Latency: {latency} ms")


@slash_command(name="botinfo", description="Get the bot's information!")
async def botinfo(ctx: InteractionContext):
    message = await ctx.send("Processing!", ephemeral=False)
    embed = Embed(
        title=f"Bot Information",
        description=f"Bot Owner: {bot.owner}\nBot Name: {bot.user.display_name}\nSupports Slash Commands: True",
        color="#00aaff"
    )

    embed.set_image(
        url="https://cdnb.artstation.com/p/assets/covers/images/027/989/379/large/yei-bodmer-yei-bodmer-thumbnail.jpg")

    await message.edit(embed=embed, content="")


bot.load_extension("extensions.punishments")
bot.load_extension("extensions.status")
bot.load_extension("extensions.fun")
bot.load_extension("extensions.interviews")
bot.load_extension("extensions.suggestions")
bot.load_extension("extensions.tickets")
# bot.load_extension("extensions.role_selections")
print("Starting bot...")
bot.start(TOKEN)
