"""
This extension handles creating and tracking punishments for users.

Written by: Trent Buckley (BoredManPlays)
"""

from interactions import slash_command, SlashContext, Embed, Extension, Client
# import utils.database
from datetime import datetime, timedelta

# The name of the collection in the database
COLLECTION_NAME = "punishments"

# The name of the extension
EXTENSION_NAME = "punishments"

# Create the collection if it doesn't exist
# utils.database.create_collection(COLLECTION_NAME)

print("Punishments extension loaded")


class Punishments(Extension):
    def __init__(self, client: Client) -> None:
        self.client: Client = client

    @slash_command(
        name="ban_offline",
        description="Ban a user who is not currently in the server.",
        scopes=["858547359804555264"],
        options=[
            {
                "type": 6,
                "name": "user",
                "description": "The user ID to ban.",
                "required": True
            },
            {
                "type": 3,
                "name": "reason",
                "description": "The reason for the ban.",
                "required": False
            }
        ]
    )
    async def ban_offline_command(self, ctx: SlashContext, user: str, reason: str = "no reason provided"):
        # Lookup the username using the user ID
        username = await self.client.fetch_user(user)
        # Check if the user has the ban members permission
        if not ctx.author.guild_permissions.BAN_MEMBERS:
            await ctx.send("<:error:943118535922679879> You do not have permission to ban members.", ephemeral=False)
            return
        # Check if the user is already banned
        if await ctx.guild.fetch_ban(user):
            await ctx.send(f"<:error:943118535922679879> `{username}` is already banned.", ephemeral=False)
            return
        # Check that the user is not in the server
        if ctx.guild.get_member(user):
            await ctx.send(f"<:error:943118535922679879> `{username}` is still in the server, this command is only for "
                           f"banning members after they've left.", ephemeral=False)
            return
        # Send the loading emoji
        message = await ctx.send(f"<a:typing:982927880495464448> Banning `{username}`", ephemeral=False)
        # Ban the user from the main server
        await ctx.guild.ban(user, reason=reason)
        # Ban the user from the application server
        application_server = ctx.client.get_guild(861018927752151071)
        await application_server.ban(user, reason=reason)
        # Send the success message
        await message.edit(content=f"<:success:943118562384547870> Banned `{username}` for `{reason}` in both servers.")

        # Send a message in the mod log
        mod_log = ctx.guild.get_channel(897765157940396052)
        embed = Embed(
            title="Member Banned",
            description=f"**User:** {username}\n**Moderator:** {ctx.author}\n**Reason:** {reason}",
            color="#ff0000"
        )
        embed.set_footer(text=f"User ID: {user}")
        await mod_log.send(embed=embed)

    @slash_command(
        name="ban",
        description="Ban a user who is currently in the server.",
        scopes=["858547359804555264"],
        options=[
            {
                "type": 6,
                "name": "user",
                "description": "The user ID to ban.",
                "required": True
            },
            {
                "type": 3,
                "name": "reason",
                "description": "The reason for the ban.",
                "required": False
            }
        ]
    )
    async def ban_command(self, ctx: SlashContext, user: str, reason: str = "no reason provided"):
        # Lookup the username using the user ID
        username = await self.client.fetch_user(user)
        # Check if the user has the ban members permission
        if not ctx.author.guild_permissions.BAN_MEMBERS:
            await ctx.send("<:error:943118535922679879> You do not have permission to ban members.", ephemeral=False)
            return
        # Check if the user is trying to ban themselves
        if user == ctx.author.id:
            await ctx.send("<:error:943118535922679879> You cannot ban yourself.", ephemeral=False)
            return
        # Check if the user is trying to ban the bot
        if user == self.client.user.id:
            await ctx.send("<:error:943118535922679879> You cannot ban me.", ephemeral=False)
            return
        # Check if the user is trying to ban a user with a higher role
        if ctx.author.top_role < ctx.guild.get_member(user).top_role:
            await ctx.send("<:error:943118535922679879> You cannot ban a user with a higher role than you.\n"
                           f"You have `{ctx.author.top_role.name}`, they have `{ctx.guild.get_member(user).top_role.name}`", ephemeral=False)
            return
        # Check if the user is already banned
        if await ctx.guild.fetch_ban(user):
            await ctx.send(f"<:error:943118535922679879> `{username}` is already banned.", ephemeral=False)
            return
        # Send the loading emoji
        message = await ctx.send(f"<a:typing:982927880495464448> Banning `{username}`", ephemeral=False)
        # Message the user
        try:
            await username.send(f"You have been banned from `Prism SMP` and `Prism SMP Applications` for `{reason}`")
        except:
            pass
        # Ban the user from the main server
        await ctx.guild.ban(user, reason=reason)
        # Ban the user from the application server
        application_server = ctx.client.get_guild(861018927752151071)
        await application_server.ban(user, reason=reason)
        # Send the success message
        await message.edit(content=f"<:success:943118562384547870> Banned `{username}` for `{reason}` in both servers.")
        # Send a message in the mod log
        mod_log = ctx.guild.get_channel(897765157940396052)
        embed = Embed(
            title="Member Banned",
            description=f"**User:** {username}\n**Moderator:** {ctx.author}\n**Reason:** {reason}",
            color="#ff0000"
        )
        embed.set_footer(text=f"User ID: {username.id}")
        await mod_log.send(embed=embed)

    @slash_command(
        name="kick",
        description="Kick a user from the server.",
        scopes=["858547359804555264"],
        options=[
            {
                "type": 6,
                "name": "user",
                "description": "The user ID to kick.",
                "required": True
            },
            {
                "type": 3,
                "name": "reason",
                "description": "The reason for the kick.",
                "required": False
            }
        ]
    )
    async def kick_command(self, ctx: SlashContext, user: str, reason: str = "no reason provided"):
        # Lookup the username using the user ID
        username = await self.client.fetch_user(user)
        # Check if the user has the kick members permission
        if not ctx.author.guild_permissions.KICK_MEMBERS:
            await ctx.send("<:error:943118535922679879> You do not have permission to kick members.", ephemeral=False)
            return
        # Check if the user is trying to kick themselves
        if user == ctx.author.id:
            await ctx.send("<:error:943118535922679879> You cannot kick yourself.", ephemeral=False)
            return
        # Check if the user is trying to kick the bot
        if user == self.client.user.id:
            await ctx.send("<:error:943118535922679879> You cannot kick me.", ephemeral=False)
            return
        # Check if the user is trying to kick a user with a higher role
        if ctx.author.top_role < ctx.guild.get_member(user).top_role:
            await ctx.send("<:error:943118535922679879> You cannot kick a user with a higher role than you.\n"
                           f"You have `{ctx.author.top_role.name}`, they have `{ctx.guild.get_member(user).top_role.name}`", ephemeral=False)
            return
        # Send the loading emoji
        message = await ctx.send(f"<a:typing:982927880495464448> Kicking `{username}`", ephemeral=False)
        # Message the user
        try:
            await username.send(f"You have been kicked from `Prism SMP` for `{reason}`")
        except:
            pass
        # Kick the user from the server
        await ctx.guild.kick(user, reason=reason)
        # Send the success message
        await message.edit(content=f"<:success:943118562384547870> Kicked `{username}` for `{reason}`.")
        # Send a message in the mod log
        mod_log = ctx.guild.get_channel(897765157940396052)
        embed = Embed(
            title="Member Kicked",
            description=f"**User:** {username}\n**Moderator:** {ctx.author}\n**Reason:** {reason}",
            color="#ff0000"
        )
        embed.set_footer(text=f"User ID: {username.id}")
        await mod_log.send(embed=embed)


def setup(client):
    Punishments(client)

