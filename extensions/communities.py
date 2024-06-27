"""
This extension handles creating and updating Discord and Minecraft communities.

Written by: Trent Buckley (BoredManPlays)
"""
from interactions import slash_command, SlashContext, Embed, Extension, Client, ActionRow, Button, ButtonStyle, Color

print("Communities extension loaded")

class Communities(Extension):
    def __init__(self, client: Client) -> None:
        self.client: Client = client

    @slash_command(
        name="create_community",
        description="Create a new community.",
        scopes=["858547359804555264"],
        options=[
            {
                "type": 3,
                "name": "name",
                "description": "The name of the community.",
                "required": True
            }
        ]
    )
    async def create_community_command(self, ctx: SlashContext, name: str):
        async def await_user_input(prompt: str, validator=None):
            while True:
                await ctx.channel.send(prompt)
                response = await self.client.wait_for(
                    event="MessageCreate",
                    checks=lambda m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id,
                    timeout=120
                )
                content = response.message.content.strip()
                if not validator or validator(content):
                    return content

        async def await_component(components, prompt: str):
            message = await ctx.channel.send(prompt, components=components)
            selection = await self.client.wait_for_component(components=components, timeout=120)
            return selection

        async def get_valid_members(prompt: str):
            while True:
                members = (await await_user_input(prompt)).split()
                if len(members) >= 3 and len(members) == len(set(members)):
                    return members
                await ctx.channel.send("You must have at least 3 unique members to create a community.")

        async def get_valid_colour(prompt: str):
            while True:
                colour = await await_user_input(prompt)
                if colour.startswith("#") and len(colour) in (4, 7):
                    return colour
                await ctx.channel.send("Please provide a valid hex code for the colour.")

        members = await get_valid_members(
            "Please provide the members of the community, separated by a space.\n"
            "For example: `@boredmanplays @floppop @chlain`."
        )
        # Check that all members are not bots
        for member in members:
            if ctx.guild.get_member(member.replace("<@", "").replace(">", "")).bot:
                await ctx.channel.send("You cannot create a community with a bot as a member.")
                members = await get_valid_members(
                    "Please provide the members of the community, separated by a space.\n"
                    "For example: `@boredmanplays @floppop @chlain`."
                )
                break

        description = await await_user_input("Please provide a brief description for the community.")
        colour = await get_valid_colour("Please provide a colour for the community. You can use a hex code or a colour name.")
        banner = (await await_user_input(
            "Please provide a URL for the community banner image.\nUpload your image to <https://imgbb.com/> "
            "and select the `BBCode full linked` in the `Embed codes` and send the full code here."
        )).split("[img]")[1].split("[/img]")[0]

        components = [
            ActionRow(
                Button(style=ButtonStyle.PRIMARY, label="🔓 Public", custom_id="public"),
                Button(style=ButtonStyle.PRIMARY, label="🔒 Private", custom_id="private")
            )
        ]
        selection = await await_component(components, "Is this community public or private?\n"
                                                       "Anyone can join a public community, members can invite players to private communities")
        public = selection.ctx.custom_id == "public"

        # Respond to the user with the information they provided
        embed = Embed(
            title="Community Information",
            description=f"Name: {name}\nMembers: {', '.join(members)}\nDescription: {description}\nColour: {colour}\n"
                        f"Banner: {banner}\nPublic: {public}",
            color=int(colour.replace("#", "0x"), 16)
        )
        message = await ctx.channel.send(embed=embed, content="Created the community with the information provided.")

        # Create the community role on Discord
        role = await ctx.guild.create_role(name=name, color=embed.color)
        for member in members:
            await ctx.guild.get_member(member.replace("<@", "").replace(">", "")).add_role(role)
        await ctx.channel.send("Creating your community in Minecraft, please hold...")

def setup(client):
    Communities(client)
