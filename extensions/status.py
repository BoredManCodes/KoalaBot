"""
This extension handles creating and updating status embeds.

Written by: Trent Buckley (BoredManPlays)
"""
import interactions
from interactions import slash_command, SlashContext, Embed, Extension, Client

print("Status extension loaded")


class Status(Extension):
    def __init__(self, client: Client) -> None:
        self.client: Client = client

    @slash_command(
        name="status_create",
        description="Create a new status embed.",
        scopes=["858547359804555264"])
    async def status_create(self, ctx: SlashContext):
        # Create the embed
        embed = Embed(
            title="No title set yet",
            color="#00aaff"
        )
        # Send the embed
        embed_message = await ctx.send(embed=embed)
        # Ask the user for a title
        question = await ctx.send("Please provide a title for the status embed.")
        title_message = await self.client.wait_for(event="MessageCreate", checks=lambda
            m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id, timeout=60)
        # Set the title
        embed.title = title_message.message.content
        # Edit the embed
        await embed_message.edit(embed=embed)
        # Delete the answer
        await title_message.message.delete()
        # Delete the question
        await question.delete()
        # Ask the user for a description
        question = await ctx.send("Please provide a description for the status embed.")
        description_message = await self.client.wait_for(event="MessageCreate", checks=lambda
            m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id, timeout=60)
        # Set the description
        embed.description = description_message.message.content
        # Edit the embed
        await embed_message.edit(embed=embed)
        # Delete the answer
        await description_message.message.delete()
        # Delete the question
        await question.delete()
        # Ask the user for an image
        question = await ctx.send("Please provide an image URL for the status embed. or type 'none' for no image.")
        image_message = await self.client.wait_for(event="MessageCreate", checks=lambda
            m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id, timeout=60)
        if image_message.message.content.lower() != "none":
            # Set the image
            embed.set_image(url=image_message.message.content)
        # Edit the embed
        await embed_message.edit(embed=embed)
        # Delete the answer
        await image_message.message.delete()
        # Delete the question
        await question.delete()
        # Ask the user for a color
        question = await ctx.send("Please provide a color for the status embed.")
        color_message = await self.client.wait_for(event="MessageCreate", checks=lambda
            m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id, timeout=60)
        # Set the color
        embed.color = color_message.message.content
        # Edit the embed
        await embed_message.edit(embed=embed)
        # Delete the answer
        await color_message.message.delete()
        # Delete the question
        await question.delete()
        # Ask the user for a footer
        question = await ctx.send("Please provide a footer for the status embed.")
        footer_message = await self.client.wait_for(event="MessageCreate", checks=lambda
            m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id, timeout=60)
        # Set the footer
        embed.set_footer(text=footer_message.message.content)
        # Edit the embed
        await embed_message.edit(embed=embed)
        # Delete the answer
        await footer_message.message.delete()
        # Delete the question
        await question.delete()
        # Ask the user how many fields they want
        question = await ctx.send("Please provide the number of fields you want in the status embed.")
        fields_message = await self.client.wait_for(event="MessageCreate", checks=lambda
            m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id, timeout=60)
        # Set the fields
        for i in range(int(fields_message.message.content)):
            question1 = await ctx.send(f"Please provide the name for field {i + 1}.")
            name_message = await self.client.wait_for(event="MessageCreate", checks=lambda
                m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id, timeout=60)
            question2 = await ctx.send(f"Please provide the value for field {i + 1}.")
            value_message = await self.client.wait_for(event="MessageCreate", checks=lambda
                m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id, timeout=60)
            embed.add_field(name=name_message.message.content, value=value_message.message.content)
            await name_message.message.delete()
            await value_message.message.delete()
            await question1.delete()
            await question2.delete()
        # Edit the embed
        await embed_message.edit(embed=embed)
        # Delete the answer
        await fields_message.message.delete()
        # Delete the question
        await question.delete()
        # Ask which channel to send the embed to
        question = await ctx.send("Please provide the channel ID to send the embed to.")
        channel_message = await self.client.wait_for(event="MessageCreate", checks=lambda
            m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id, timeout=60)
        # Send the embed
        await self.client.get_channel(int(channel_message.message.content)).send(embed=embed)
        # Delete the answer
        await channel_message.message.delete()
        # Delete the question
        await question.delete()
        # Send the success message
        await ctx.send("Status embed created successfully!", ephemeral=False)

    @slash_command(
        name="status_update_field_value",
        description="Update an existing status embed's field value.",
        scopes=["858547359804555264"])
    async def status_update_field_value(self, ctx: SlashContext):
        # Ask the user for the message ID
        question = await ctx.send("Please provide the message ID of the status embed to update.")
        message_id_message = await self.client.wait_for(event="MessageCreate", checks=lambda
            m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id, timeout=60)
        # Get the message
        try:
            message = await ctx.channel.fetch_message(int(message_id_message.message.content))
        except:
            await ctx.send("Invalid message ID provided.", ephemeral=False)
            return
        # Delete the answer
        await message_id_message.message.delete()
        # Delete the question
        await question.delete()
        # Get the embed
        embed = message.embeds[0]
        # Ask the user for the field to update
        question = await ctx.send("Please provide the name of the field to update.")
        field_name_message = await self.client.wait_for(event="MessageCreate", checks=lambda
            m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id, timeout=60)
        # Delete the answer
        await field_name_message.message.delete()
        # Delete the question
        await question.delete()
        # Ask the user for the new value
        question = await ctx.send("Please provide the new value for the field.")
        new_value_message = await self.client.wait_for(event="MessageCreate", checks=lambda
            m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id, timeout=60)
        # Update the field
        for i in range(len(embed.fields)):
            if embed.fields[i].name == field_name_message.message.content:
                embed.fields[i] = interactions.EmbedField(name=field_name_message.message.content, value=new_value_message.message.content)
        # Edit the embed
        await message.edit(embed=embed)
        # Delete the answer
        await new_value_message.message.delete()
        # Delete the question
        await question.delete()
        # Send the success message
        await ctx.send("Status embed updated successfully!", ephemeral=False)

    @slash_command(
        name="status_update_field_name",
        description="Update an existing status embed's field name.",
        scopes=["858547359804555264"])
    async def status_update_field_name(self, ctx: SlashContext):
        # Ask the user for the message ID
        question = await ctx.send("Please provide the message ID of the status embed to update.")
        message_id_message = await self.client.wait_for(event="MessageCreate", checks=lambda
            m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id, timeout=60)
        # Get the message
        try:
            message = await ctx.channel.fetch_message(int(message_id_message.message.content))
        except:
            await ctx.send("Invalid message ID provided.", ephemeral=False)
            return
        # Delete the answer
        await message_id_message.message.delete()
        # Delete the question
        await question.delete()
        # Get the embed
        embed = message.embeds[0]
        # Ask the user for the field to update
        question = await ctx.send("Please provide the name of the field to update.")
        field_name_message = await self.client.wait_for(event="MessageCreate", checks=lambda
            m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id, timeout=60)
        # Delete the answer
        await field_name_message.message.delete()
        # Delete the question
        await question.delete()
        # Ask the user for the new name
        question = await ctx.send("Please provide the new name for the field.")
        new_name_message = await self.client.wait_for(event="MessageCreate", checks=lambda
            m: m.message.author.id == ctx.author.id and m.message.channel.id == ctx.channel.id, timeout=60)
        # Update the field
        for i in range(len(embed.fields)):
            if embed.fields[i].name == field_name_message.message.content:
                embed.fields[i] = interactions.EmbedField(name=new_name_message.message.content, value=embed.fields[i].value)
        # Edit the embed
        await message.edit(embed=embed)
        # Delete the answer
        await new_name_message.message.delete()
        # Delete the question
        await question.delete()
        # Send the success message
        await ctx.send("Status embed updated successfully!", ephemeral=False)


def setup(client):
    Status(client)
