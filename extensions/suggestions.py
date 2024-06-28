from interactions import slash_command, SlashContext, Embed, Extension, Client, ActionRow, Button, ButtonStyle, Color, \
    Webhook, listen
from interactions.ext.paginators import Paginator
from interactions.api.events import (
    MemberRemove,
    MessageReactionAdd,
    MessageReactionRemove,
    MessageCreate,
)
import sqlite3


print("Suggestions extension loaded")

con = sqlite3.connect("KoalaBot.db")
cur = con.cursor()

class Suggestions(Extension):
    def __init__(self, client: Client) -> None:
        self.client: Client = client

    suggestions_channel = 863262093737197568
    staff_role = 895784665049366579

    # Wait for a message to be sent in the suggestions channel
    @listen()
    async def on_message_create(self, event: MessageCreate):
        if event.message.channel.id == self.suggestions_channel:
            if event.message.author.bot:
                return
            # Get the highest suggestion number
            cur.execute("SELECT suggestion_number FROM suggestions ORDER BY suggestion_number DESC LIMIT 1")
            count = cur.fetchone()[0] + 1
            # Send an embed to the suggestions channel
            embed = Embed(
                title=f"Suggestion #{count}",
                description=event.message.content,
                color=Color.from_hex("#00aaff"),
            )
            embed.set_author(
                name=event.message.author.display_name,
                icon_url=event.message.author.avatar_url,
            )
            embed.set_footer(text=f"Status: 🟡 Pending")
            await event.message.delete()
            suggestion = await event.message.channel.send(embed=embed)
            # Add buttons to the suggestion
            components = [
                ActionRow(
                    Button(
                        style=ButtonStyle.GREEN,
                        label="👍 Upvote",
                        custom_id=f"upvote-{suggestion.id}",
                    ),
                    Button(
                        style=ButtonStyle.DANGER,
                        label="👎 Downvote",
                        custom_id=f"downvote-{suggestion.id}",
                    ),
                    Button(
                        style=ButtonStyle.PRIMARY,
                        label="🗨️ Comment",
                        custom_id=f"comment-{suggestion.id}",
                    ),
                    Button(
                        style=ButtonStyle.SECONDARY,
                        label="🗑️ Delete",
                        custom_id=f"delete-{suggestion.id}",
                    ),
                )
            ]
            await suggestion.edit(components=components)
            # Save this suggestion to the database
            cur.execute("INSERT INTO suggestions (user, suggestion, status, message_id, suggestion_number, open_discussion) VALUES (?, ?, ?, ?, ?, ?)",
                        (event.message.author.id, event.message.content, "pending", suggestion.id, count, 0))
            con.commit()
            cur.execute("INSERT INTO votes (message_id, user_id, vote) VALUES (?, ?, ?)",
                        (suggestion.id, event.message.author.id, "upvote"))
            con.commit()

    # Wait for a button to be clicked
    @listen()
    async def on_component(self, response):
        if response.ctx.custom_id.startswith("upvote-"):
            message_id = response.ctx.custom_id.split("-")[1]
            # Check if the user has already voted on this suggestion
            cur.execute("SELECT * FROM votes WHERE message_id = ? AND user_id = ?", (message_id, response.ctx.author.id))
            vote = cur.fetchone()
            if not vote:
                # Save this upvote to the database
                cur.execute("INSERT INTO votes (message_id, user_id, vote) VALUES (?, ?, ?)",
                            (message_id, response.ctx.author.id, "upvote"))
                con.commit()
                await response.ctx.send("Upvoted!", ephemeral=True)
                return
            if vote[2] == "upvote":
                # The user is trying to upvote again, we assume they want to remove their vote
                cur.execute("DELETE FROM votes WHERE message_id = ? AND user_id = ?", (message_id, response.ctx.author.id))
                con.commit()
                await response.ctx.send("Upvote removed!", ephemeral=True)
            elif vote[2] == "downvote":
                # The user is trying to upvote after downvoting, we remove the downvote and add the upvote
                cur.execute("DELETE FROM votes WHERE message_id = ? AND user_id = ?", (message_id, response.ctx.author.id))
                con.commit()
                cur.execute("INSERT INTO votes (message_id, user_id, vote) VALUES (?, ?, ?)",
                            (message_id, response.ctx.author.id, "upvote"))
                con.commit()
                await response.ctx.send("Changed your downvote into an upvote", ephemeral=True)
        elif response.ctx.custom_id.startswith("downvote-"):
            message_id = response.ctx.custom_id.split("-")[1]
            # Check if the user has already voted on this suggestion
            cur.execute("SELECT * FROM votes WHERE message_id = ? AND user_id = ?", (message_id, response.ctx.author.id))
            vote = cur.fetchone()
            if not vote:
                # Save this downvote to the database
                cur.execute("INSERT INTO votes (message_id, user_id, vote) VALUES (?, ?, ?)",
                            (message_id, response.ctx.author.id, "downvote"))
                con.commit()
                await response.ctx.send("Downvoted!", ephemeral=True)
                return
            if vote[2] == "downvote":
                # The user is trying to downvote again, we assume they want to remove their vote
                cur.execute("DELETE FROM votes WHERE message_id = ? AND user_id = ?", (message_id, response.ctx.author.id))
                con.commit()
                await response.ctx.send("Downvote removed!", ephemeral=True)
            elif vote[2] == "upvote":
                # The user is trying to downvote after upvoting, we remove the upvote and add the downvote
                cur.execute("DELETE FROM votes WHERE message_id = ? AND user_id = ?", (message_id, response.ctx.author.id))
                con.commit()
                cur.execute("INSERT INTO votes (message_id, user_id, vote) VALUES (?, ?, ?)",
                            (message_id, response.ctx.author.id, "downvote"))
                con.commit()
                await response.ctx.send("Changed your upvote into a downvote", ephemeral=True)
        elif response.ctx.custom_id.startswith("comment-"):
            # Check if the suggestion already has a thread
            cur.execute("SELECT open_discussion FROM suggestions WHERE message_id = ?", (response.ctx.custom_id.split("-")[1],))
            open_discussion = cur.fetchone()[0]
            if open_discussion == 1:
                await response.ctx.send("This suggestion already has a discussion thread!", ephemeral=True)
                return
            # Set the suggestion to have an open discussion
            cur.execute("UPDATE suggestions SET open_discussion = 1 WHERE message_id = ?", (response.ctx.custom_id.split("-")[1],))
            con.commit()
            # Get the suggestion number from the database
            cur.execute("SELECT suggestion_number FROM suggestions WHERE message_id = ?", (response.ctx.custom_id.split("-")[1],))
            suggestion_number = cur.fetchone()[0]
            # Get the user who created the suggestion
            cur.execute("SELECT user FROM suggestions WHERE message_id = ?", (response.ctx.custom_id.split("-")[1],))
            suggestee = cur.fetchone()[0]
            # Create a thread for the suggestion
            message_id = response.ctx.custom_id.split("-")[1]
            suggestion = response.ctx.channel.get_message(message_id)
            thread = await response.ctx.channel.create_thread(message=suggestion, name=f"Suggestion #{suggestion_number} discussion")
            await thread.send(f"<@{response.ctx.author.id}> feel free to discuss this suggestion here!")
            # Ping the user who created the suggestion so they know a thread has been created
            await thread.send(f"<@{suggestee}>", delete_after=1)
            # Respond to the user who clicked the button
            await response.ctx.send("Thread created!", ephemeral=True)
        elif response.ctx.custom_id.startswith("delete-"):
            message_id = response.ctx.custom_id.split("-")[1]
            # Check if the user who clicked the button is the user who created the suggestion
            cur.execute("SELECT user FROM suggestions WHERE message_id = ?", (message_id,))
            suggestee = cur.fetchone()[0]
            # Check if the user who clicked the button is the user who created the suggestion or an admin
            staff_role = response.ctx.guild.get_role(self.staff_role)
            if staff_role in response.ctx.author.roles:
                # Delete the suggestion
                cur.execute("DELETE FROM suggestions WHERE message_id = ?", (message_id,))
                con.commit()
                suggestion = response.ctx.channel.get_message(message_id)
                await suggestion.delete()
                # Fetch the suggestee's user object
                suggestee = response.ctx.guild.get_member(suggestee)
                await suggestee.send(f"Your suggestion has been deleted by an admin in {response.ctx.guild.name}")
                await response.ctx.send("Suggestion deleted!", ephemeral=True)
                return
            if response.ctx.author.id == suggestee:
                # Delete the suggestion
                cur.execute("DELETE FROM suggestions WHERE message_id = ?", (message_id,))
                con.commit()
                suggestion = response.ctx.channel.get_message(message_id)
                await suggestion.delete()
                await response.ctx.send("Suggestion deleted!", ephemeral=True)
            else:
                await response.ctx.send("You can't delete a suggestion you didn't create!", ephemeral=True)

    # An admin command to view all suggestions, paginated
    @slash_command(name="suggestions", description="View all suggestions", scopes=[858547359804555264], options=[
       {
            "name": "suggestion_number",
            "description": "The number of the suggestion you want to view",
            "type": 4,
            "required": False
        },
        {
            "name": "ephemeral",
            "description": "Whether to send the response as an ephemeral message. Defaults to false.",
            "type": 5,
            "required": False
        }
    ])
    async def suggestions(self, ctx: SlashContext, suggestion_number: int = None, ephemeral: bool = False):
        # Check if the user is an admin
        # Check if the user who clicked the button is the user who created the suggestion or an admin
        staff_role = ctx.guild.get_role(self.staff_role)
        if staff_role not in ctx.author.roles:
            await ctx.send("You don't have permission to use this command!", ephemeral=True)
            return
        if suggestion_number:
            # Get the suggestion with the given number
            cur.execute("SELECT * FROM suggestions WHERE suggestion_number = ?", (suggestion_number,))
            suggestion = cur.fetchone()
            if not suggestion:
                await ctx.send("That suggestion number doesn't exist!", ephemeral=True)
                return
            # Get the user who created the suggestion
            suggestee = ctx.guild.get_member(suggestion[0])
            # Get the number of upvotes and downvotes
            upvotes = 0
            downvotes = 0
            upvoters = []
            downvoters = []
            cur.execute("SELECT * FROM votes WHERE message_id = ?", (suggestion[3],))
            votes = cur.fetchall()
            for vote in votes:
                if vote[0] == suggestion[3]:
                    if vote[2] == "upvote":
                        upvotes += 1
                        upvoters.append(ctx.guild.get_member(vote[1]).nickname if ctx.guild.get_member(vote[1]).nickname else ctx.guild.get_member(vote[1]).display_name)
                    elif vote[2] == "downvote":
                        downvotes += 1
                        downvoters.append(ctx.guild.get_member(vote[1]).nickname if ctx.guild.get_member(vote[1]).nickname else ctx.guild.get_member(vote[1]).display_name)
            # Create an embed for the suggestion
            embed = Embed(
                title=f"Suggestion #{suggestion[4]}",
                description=suggestion[1],
                color=Color.from_hex("#00aaff"),
            )
            embed.set_author(
                name=suggestee.display_name,
                icon_url=suggestee.avatar_url,
            )
            upvoters = "\n".join(upvoters)
            downvoters = "\n".join(downvoters)
            upvote_title = "Upvote" if upvotes == 1 else "Upvotes"
            downvote_title = "Downvote" if downvotes == 1 else "Downvotes"
            embed.add_field(name=f"{upvotes} {upvote_title}", value=upvoters if upvoters else "No upvotes")
            embed.add_field(name=f"{downvotes} {downvote_title}", value=downvoters if downvoters else "No downvotes")
            if suggestion[2] == "pending":
                embed.add_field(name="Status", value="🟡 Pending")
            elif suggestion[2] == "declined":
                embed.add_field(name="Status", value="🔴 Declined")
            elif suggestion[2] == "accepted":
                embed.add_field(name="Status", value="🟢 Accepted")
            elif suggestion[2] == "review":
                embed.add_field(name="Status", value="🗨️ Under Review")
            elif suggestion[2] == "implemented":
                embed.add_field(name="Status", value="✅ Implemented")
            await ctx.send(embed=embed, ephemeral=ephemeral)
            return
        # Get all suggestions and votes from the database
        cur.execute("SELECT * FROM suggestions")
        suggestions = cur.fetchall()
        cur.execute("SELECT * FROM votes")
        votes = cur.fetchall()
        embeds = []
        for suggestion in suggestions:
            # Get the user who created the suggestion
            suggestee = ctx.guild.get_member(suggestion[0])
            # Get the number of upvotes and downvotes
            upvotes = 0
            downvotes = 0
            upvoters = []
            downvoters = []
            for vote in votes:
                if vote[0] == suggestion[3]:
                    if vote[2] == "upvote":
                        upvotes += 1
                        upvoters.append(ctx.guild.get_member(vote[1]).nickname if ctx.guild.get_member(vote[1]).nickname else ctx.guild.get_member(vote[1]).display_name)
                    elif vote[2] == "downvote":
                        downvotes += 1
                        downvoters.append(ctx.guild.get_member(vote[1]).nickname if ctx.guild.get_member(vote[1]).nickname else ctx.guild.get_member(vote[1]).display_name)
            # Create an embed for each suggestion
            embed = Embed(
                title=f"Suggestion #{suggestion[4]}",
                description=suggestion[1],
                color=Color.from_hex("#00aaff"),
            )
            embed.set_author(
                name=suggestee.display_name,
                icon_url=suggestee.avatar_url,
            )
            print(upvoters)
            print(downvoters)
            upvoters = "\n".join(upvoters)
            downvoters = "\n".join(downvoters)
            upvote_title = "Upvote" if upvotes == 1 else "Upvotes"
            downvote_title = "Downvote" if downvotes == 1 else "Downvotes"
            embed.add_field(name=f"{upvotes} {upvote_title}", value=upvoters if upvoters else "No upvotes")
            embed.add_field(name=f"{downvotes} {downvote_title}", value=downvoters if downvoters else "No downvotes")
            if suggestion[2] == "pending":
                embed.add_field(name="Status", value="🟡 Pending")
            elif suggestion[2] == "declined":
                embed.add_field(name="Status", value="🔴 Declined")
            elif suggestion[2] == "accepted":
                embed.add_field(name="Status", value="🟢 Accepted")
            elif suggestion[2] == "review":
                embed.add_field(name="Status", value="🗨️ Under Review")
            elif suggestion[2] == "implemented":
                embed.add_field(name="Status", value="✅ Implemented")
            embeds.append(embed)

        paginator = Paginator.create_from_embeds(self.client, *embeds, timeout=120)
        await paginator.send(ctx, ephemeral=ephemeral)

    # Listen for the staff reactions on a suggestion
    @listen()
    async def on_reaction_add(self, event: MessageReactionAdd):
        if event.message.channel.id == self.suggestions_channel:
            # Check if the user who clicked the button is the user who created the suggestion or an admin
            staff_role = event.message.guild.get_role(self.staff_role)
            if staff_role in event.author.roles:
                # Check if the message is a valid suggestion
                cur.execute("SELECT * FROM suggestions WHERE message_id = ?", (event.message.id,))
                suggestion = cur.fetchone()
                if suggestion:
                    if event.emoji.name == "🟡":
                        cur.execute("UPDATE suggestions SET status = 'pending' WHERE message_id = ?", (event.message.id,))
                        con.commit()
                        await event.message.remove_reaction(event.emoji, event.author)
                        # Edit the suggestion to show the new status
                        await event.message.edit(embed=Embed(
                            title=event.message.embeds[0].title,
                            description=event.message.embeds[0].description,
                            color=Color.from_hex("#FFEA00")  # yellow,
                        ).set_author(
                            name=event.message.embeds[0].author.name,
                            icon_url=event.message.embeds[0].author.icon_url,
                        ).set_footer(text="Status: 🟡 Pending"))
                        # Enable all the buttons on the suggestion
                        components = [
                            ActionRow(
                                Button(
                                    style=ButtonStyle.GREEN,
                                    label="👍 Upvote",
                                    custom_id=f"upvote-{event.message.id}",
                                ),
                                Button(
                                    style=ButtonStyle.DANGER,
                                    label="👎 Downvote",
                                    custom_id=f"downvote-{event.message.id}",
                                ),
                                Button(
                                    style=ButtonStyle.PRIMARY,
                                    label="🗨️ Comment",
                                    custom_id=f"comment-{event.message.id}",
                                ),
                                Button(
                                    style=ButtonStyle.SECONDARY,
                                    label="🗑️ Delete",
                                    custom_id=f"delete-{event.message.id}",
                                ),
                            )
                        ]
                        await event.message.edit(components=components)
                        # Send a message to the suggestee that their suggestion is pending
                        suggestee = event.message.guild.get_member(suggestion[0])
                        await suggestee.send(f"Your [suggestion](https://discord.com/channels/858547359804555264/863262093737197568/{suggestion[3]}) has been reset to pending in {event.message.guild.name}")
                    elif event.emoji.name == "🔴":
                        cur.execute("UPDATE suggestions SET status = 'declined' WHERE message_id = ?", (event.message.id,))
                        con.commit()
                        await event.message.remove_reaction(event.emoji, event.author)
                        # Edit the suggestion to show the new status
                        await event.message.edit(embed=Embed(
                            title=event.message.embeds[0].title,
                            description=event.message.embeds[0].description,
                            color=Color.from_hex("#FF0000") # red,
                        ).set_author(
                            name=event.message.embeds[0].author.name,
                            icon_url=event.message.embeds[0].author.icon_url,
                        ).set_footer(text="Status: 🔴 Declined"))
                        # Remove the vote buttons from the suggestion
                        components = [
                            ActionRow(
                                Button(
                                    style=ButtonStyle.PRIMARY,
                                    label="🗨️ Comment",
                                    custom_id=f"comment-{event.message.id}",
                                ),
                                Button(
                                    style=ButtonStyle.SECONDARY,
                                    label="🗑️ Delete",
                                    custom_id=f"delete-{event.message.id}",
                                ),
                            )
                        ]
                        await event.message.edit(components=components)
                        # Send a message to the suggestee that their suggestion has been declined
                        suggestee = event.message.guild.get_member(suggestion[0])
                        await suggestee.send(f"Your [suggestion](https://discord.com/channels/858547359804555264/863262093737197568/{suggestion[3]}) has been declined in {event.message.guild.name}")
                    elif event.emoji.name == "🟢":
                        cur.execute("UPDATE suggestions SET status = 'accepted' WHERE message_id = ?", (event.message.id,))
                        con.commit()
                        await event.message.remove_reaction(event.emoji, event.author)
                        # Edit the suggestion to show the new status
                        await event.message.edit(embed=Embed(
                            title=event.message.embeds[0].title,
                            description=event.message.embeds[0].description,
                            color=Color.from_hex("#AAFF00")  # green
                        ).set_author(
                            name=event.message.embeds[0].author.name,
                            icon_url=event.message.embeds[0].author.icon_url,
                        ).set_footer(text="Status: 🟢 Accepted"))
                        # Send a message to the suggestee that their suggestion has been accepted
                        suggestee = event.message.guild.get_member(suggestion[0])
                        await suggestee.send(f"Your [suggestion](https://discord.com/channels/858547359804555264/863262093737197568/{suggestion[3]}) has been accepted in {event.message.guild.name}")
                    elif event.emoji.name == "🗨️":
                        cur.execute("UPDATE suggestions SET status = 'review' WHERE message_id = ?", (event.message.id,))
                        con.commit()
                        await event.message.remove_reaction(event.emoji, event.author)
                        # Edit the suggestion to show the new status
                        await event.message.edit(embed=Embed(
                            title=event.message.embeds[0].title,
                            description=event.message.embeds[0].description,
                            color=Color.from_hex("#FF00FF")  # purple,
                        ).set_author(
                            name=event.message.embeds[0].author.name,
                            icon_url=event.message.embeds[0].author.icon_url,
                        ).set_footer(text="Status: 🗨️ Under Review"))
                        # Send a message to the suggestee that their suggestion is under review
                        suggestee = event.message.guild.get_member(suggestion[0])
                        await suggestee.send(f"Your [suggestion](https://discord.com/channels/858547359804555264/863262093737197568/{suggestion[3]}) is under review by staff in {event.message.guild.name}")
                    elif event.emoji.name == "✅":
                        cur.execute("UPDATE suggestions SET status = 'implemented' WHERE message_id = ?", (event.message.id,))
                        con.commit()
                        await event.message.remove_reaction(event.emoji, event.author)
                        # Edit the suggestion to show the new status
                        await event.message.edit(embed=Embed(
                            title=event.message.embeds[0].title,
                            description=event.message.embeds[0].description,
                            color=Color.from_hex("#0000FF")  # blue,
                        ).set_author(
                            name=event.message.embeds[0].author.name,
                            icon_url=event.message.embeds[0].author.icon_url,
                        ).set_footer(text="Status: ✅ Implemented"))
                        # Send a message to the suggestee that their suggestion has been implemented
                        suggestee = event.message.guild.get_member(suggestion[0])
                        await suggestee.send(f"Your [suggestion](https://discord.com/channels/858547359804555264/863262093737197568/{suggestion[3]}) has been implemented in {event.message.guild.name}")
                else:
                    return



def setup(client):
    Suggestions(client)