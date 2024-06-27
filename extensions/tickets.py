from interactions import (
    slash_command,
    listen,
    SlashContext,
    Embed,
    Extension,
    Client,
    Task,
    IntervalTrigger,
    ActionRow,
    Button,
    ButtonStyle,
    OverwriteType,
    PermissionOverwrite,
    Permissions,
)
from interactions.api.events import (
    MemberRemove,
    MessageReactionAdd,
    MessageReactionRemove,
    MessageCreate,
)
import sqlite3

print("Tickets extension loaded")

ticket_channel = 976847293699477544
ticket_category = 976846151909277736
waiting_on_application_role = 1221740715260907550
new_member_role = 897774734278787093
staff_role = 895784665049366579
prismian_role = 858547687191085126
mod_log_channel = 897765157940396052

con = sqlite3.connect("KoalaBot.db")
cur = con.cursor()



class Tickets(Extension):
    def __init__(self, client: Client) -> None:
        self.client: Client = client

    @listen()
    async def on_message_create(self, event: MessageCreate):
        if event.message.author != 324504908013240330:
            return
        if event.message.content == "create_ticket":
            channel = self.client.get_channel(ticket_channel)
            # Create the embed for the application
            embed = Embed(
                title="Need help?",
                description="To ask for help, please click the button below to create a ticket.",
                color="#00aaff",
            )
            components = [
                ActionRow(
                    Button(style=ButtonStyle.DANGER, label="Create Ticket", custom_id="Ticket")
                )
            ]
            await channel.send(embed=embed, components=components)
    #
    # # Create the application
    # async def create_application(self, response):
    #     answers = []
    #     # Check if the user has already started an application
    #     cur.execute(
    #         "SELECT * FROM interview_channels WHERE user = ? AND status = 'started'", (response.ctx.author.id,)
    #     )
    #     result = cur.fetchone()
    #     if result:
    #         await response.ctx.send(
    #             "You have already started an application. Please complete your current application before starting a new one.",
    #             delete_after=120,
    #         )
    #         return
    #     # Create a channel for the application
    #     channel = await response.ctx.guild.create_text_channel(
    #         f"{response.ctx.author.username}-application",
    #         category=applications_category,
    #     )
    #
    #     await channel.edit_permission(
    #         PermissionOverwrite(
    #             id=response.ctx.author.id,
    #             type=OverwriteType.MEMBER,
    #             allow=Permissions.VIEW_CHANNEL
    #             | Permissions.SEND_MESSAGES
    #             | Permissions.READ_MESSAGE_HISTORY,
    #         )
    #     )
    #     await channel.edit_permission(
    #         PermissionOverwrite(
    #             id=response.ctx.guild.default_role.id,
    #             type=OverwriteType.ROLE,
    #             deny=Permissions.VIEW_CHANNEL,
    #         )
    #     )
    #     # Save that the user has started an application to the database
    #     cur.execute(
    #         "INSERT INTO interview_channels (user, interview_channel, status) VALUES (?, ?, ?)",
    #         (response.ctx.author.id, channel.id, "started"),
    #     )
    #     con.commit()
    #     # Send a message in the applications channel telling them that the application has been created
    #     await response.ctx.send(
    #         f"Your application channel has been created in {channel.mention}. Please answer the following questions "
    #         f"to apply to join Prism.\nAfter this members from Prism will assess your application and have the "
    #         f"opportunity to ask you anything further.",
    #         delete_after=120,
    #     )
    #     # Create the embed for the application
    #     embed = Embed(
    #         title="Prism Application",
    #         description="Please answer the following questions to apply to join Prism.\nAfter this members from Prism "
    #         "will assess your application and have the opportunity to ask you anything further.",
    #         color="#00aaff",
    #     )
    #     embed.set_footer(
    #         text="Please answer carefully and send only one message per question."
    #     )
    #     await channel.send(embed=embed)
    #     # For question in questions, ask and wait for a response
    #     for idx, question in enumerate(questions):
    #         await channel.send(question)
    #         # Save the question to the database
    #         if idx == 0:
    #             cur.execute(
    #                 f"INSERT INTO answers (user, q{idx}, channel) VALUES (?, ?, ?)",
    #                 (response.ctx.author.id, question, channel.id),
    #             )
    #             con.commit()
    #         else:
    #             cur.execute(
    #                 f"UPDATE answers SET q{idx} = ? WHERE user = ?",
    #                 (question, response.ctx.author.id),
    #             )
    #             con.commit()
    #         try:
    #             answer = await self.client.wait_for(
    #                 event="MessageCreate",
    #                 checks=lambda m: m.message.channel == channel
    #                 and m.message.author == response.ctx.author,
    #                 timeout=360000000,
    #             )
    #             # Save the answer to the database
    #             cur.execute(
    #                 f"UPDATE answers SET a{idx} = ? WHERE user = ?",
    #                 (answer.message.content, response.ctx.author.id),
    #             )
    #             con.commit()
    #             answers.append(answer.message.content)
    #         except BaseException as e:
    #             await channel.send("You took too long to respond, please try again.")
    #             # Save this to the database
    #             cur.execute("UPDATE interview_channels SET status = 'timed_out' WHERE user = ?", (response.ctx.author.id,))
    #             con.commit()
    #             print(e)
    #     # Send the embed to modlog to keep a record of the application
    #     embed = Embed(
    #         title="Prism Application",
    #         description=f"{response.ctx.author.username} | Applied!",
    #         color="#00aaff",
    #     )
    #     for i, question in enumerate(questions):
    #         embed.add_field(name=question, value=answers[i], inline=False)
    #     components = [
    #         ActionRow(
    #             Button(
    #                 style=ButtonStyle.GREEN,
    #                 label="Approve",
    #                 custom_id=f"accept-{response.ctx.author.id}",
    #             ),
    #             Button(
    #                 style=ButtonStyle.DANGER,
    #                 label="Deny",
    #                 custom_id=f"deny-{response.ctx.author.id}",
    #             ),
    #         )
    #     ]
    #     await channel.send(
    #         "Please wait for a staff member to review your application.",
    #         components=components,
    #     )
    #     # Update the interview channel status to submitted
    #     cur.execute("UPDATE interview_channels SET status = 'submitted' WHERE user = ?", (response.ctx.author.id,))
    #     con.commit()
    #     mod_log = self.client.get_channel(mod_log_channel)
    #     message = await mod_log.send(embed=embed)
    #     # Save the message id to the database
    #     cur.execute("INSERT INTO interview_mod_log_channels (user, channel, message) VALUES (?, ?, ?)", (response.ctx.author.id, channel.id, message.id))
    #     con.commit()
    #     # Add the Application Reviewers to the channel
    #     await channel.edit_permission(
    #         PermissionOverwrite(
    #             id=response.ctx.guild.get_role(application_reviewer_role).id,
    #             type=OverwriteType.ROLE,
    #             allow=Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES,
    #         )
    #     )
    #
    #     # Create a channel for the reviewers to discuss the application privately
    #     reviewer_channel = await response.ctx.guild.create_text_channel(
    #         f"{response.ctx.author.username}-review", category=applications_category
    #     )
    #     # Save the channel to the database
    #     cur.execute("UPDATE interview_channels SET review_channel = ? WHERE user = ? AND status = 'submitted'", (reviewer_channel.id, response.ctx.author.id))
    #     con.commit()
    #     await reviewer_channel.edit_permission(
    #         PermissionOverwrite(
    #             id=response.ctx.guild.get_role(application_reviewer_role).id,
    #             type=OverwriteType.ROLE,
    #             allow=Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES,
    #         )
    #     )
    #     await reviewer_channel.edit_permission(
    #         PermissionOverwrite(
    #             id=response.ctx.guild.default_role.id,
    #             type=OverwriteType.ROLE,
    #             deny=Permissions.VIEW_CHANNEL,
    #         )
    #     )
    #     # Send a copy of the embed to the review channel
    #     await reviewer_channel.send(embed=embed)
    #     # Send a message in the applications channel telling them that the review channel has been created
    #     await reviewer_channel.send(
    #         f"<@&{application_reviewer_role}> this is the review channel for {response.ctx.author.username}'s application. Please discuss the application here and come to a decision on whether to accept or deny the application. {response.ctx.author.mention} is not able to see this channel, you may ask them further questions in their application channel."
    #     )
    #
    # # A debug command to send the components to the channel
    # @listen()
    # async def on_message_create(self, event: MessageCreate):
    #     if event.message.content == "<@1217002267417514084> kill":
    #         if event.message.author.id != 324504908013240330:
    #             event.message.channel.send("You do not have permission to kill me.")
    #             return
    #         await event.message.channel.send("\*dies\*")
    #         quit(0)
    #     if event.message.content == "send_components":
    #         components = [
    #             ActionRow(
    #                 Button(
    #                     style=ButtonStyle.GREEN,
    #                     label="Approve",
    #                     custom_id=f"accept-{event.message.author.id}",
    #                 ),
    #                 Button(
    #                     style=ButtonStyle.DANGER,
    #                     label="Deny",
    #                     custom_id=f"deny-{event.message.author.id}",
    #                 ),
    #             )
    #         ]
    #         await event.message.channel.send(
    #             "Please wait for a staff member to review your application.",
    #             components=components,
    #         )
    #
    # # Accept or deny the application
    # @listen()
    # async def on_component(self, response):
    #     global staff_role
    #     if response.ctx.custom_id == "apply":
    #         await self.create_application(response)
    #     if response.ctx.custom_id.startswith("accept"):
    #         # Check if user is staff
    #         staff_role = response.ctx.guild.get_role(staff_role)
    #         if staff_role not in response.ctx.author.roles:
    #             error = await response.ctx.send(
    #                 "You do not have permission to approve or deny applications."
    #             )
    #             await error.reply(
    #                 f"https://tenor.com/view/approval-denied-gif-10601164"
    #             )
    #             return
    #         user_id = response.ctx.custom_id.split("-")[1]
    #         user = await response.ctx.guild.fetch_member(user_id)
    #         await response.ctx.send(
    #             f"{user.mention} has been accepted into Prism by <@{response.ctx.author.id}>!\nPlease read <#861317568807829535>."
    #         )
    #         # Update the database to show that the user has been accepted
    #         cur.execute("UPDATE interview_channels SET status = 'accepted' WHERE user = ? AND status = 'submitted' AND interview_channel = ?", (user.id, response.ctx.channel.id))
    #         con.commit()
    #         await user.add_role(response.ctx.guild.get_role(new_member_role))
    #         await user.remove_role(
    #             response.ctx.guild.get_role(waiting_on_application_role)
    #         )
    #         await user.send(
    #             f"Congratulations! You have been accepted into Prism SMP. Welcome to the community!"
    #         )
    #         # Fetch the user's modlog message and edit it to show that the user has been accepted
    #         mod_log = self.client.get_channel(mod_log_channel)
    #         cur.execute("SELECT message FROM interview_mod_log_channels WHERE user = ? AND channel = ?", (user.id, response.ctx.channel.id))
    #         message_id = cur.fetchone()
    #         # Fetch the message by the id
    #         async for message in mod_log.history(limit=100):
    #             if message.id == message_id[0]:
    #                 # Edit the message to show that the user has been accepted
    #                 message.embeds[0].description = f"{user.username} | Accepted!"
    #                 await message.edit(embed=message.embeds[0])
    #                 return
    #
    #     if response.ctx.custom_id.startswith("deny"):
    #         # Fuck the checks, allow the user to deny themselves
    #         # staff_role = response.ctx.guild.get_role(staff_role)
    #         # if staff_role not in response.ctx.author.roles:
    #         #     await response.ctx.send("You do not have permission to accept or deny applications.")
    #         #     return
    #         user_id = response.ctx.custom_id.split("-")[1]
    #         user = await response.ctx.guild.fetch_member(user_id)
    #         await response.ctx.send(
    #             f"{user.mention} has been denied from Prism by <@{response.ctx.author.id}>."
    #         )
    #         # Save this to the database
    #         cur.execute("UPDATE interview_channels SET status = 'denied' WHERE user = ? AND status = 'submitted' AND interview_channel = ?", (user.id, response.ctx.channel.id))
    #         con.commit()
    #         await user.send(
    #             f"Unfortunately, your application to Prism SMP has been denied. Thank you for applying and best of luck in your future endeavors."
    #         )
    #         # Fetch the user's modlog message and edit it to show that the user has been accepted
    #         mod_log = self.client.get_channel(mod_log_channel)
    #         cur.execute("SELECT message FROM interview_mod_log_channels WHERE user = ? AND channel = ?",
    #                     (user.id, response.ctx.channel.id))
    #         message_id = cur.fetchone()
    #         # Fetch the message by the id
    #         async for message in mod_log.history(limit=100):
    #             if message.id == message_id[0]:
    #                 # Edit the message to show that the user has been accepted
    #                 message.embeds[0].description = f"{user.username} | Accepted!"
    #                 await message.edit(embed=message.embeds[0])
    #                 return
    #         await user.kick(reason="Application Denied")
    #
    # @slash_command(
    #     name="close_application",
    #     description="Close the application channel for the user.",
    #     scopes=[858547359804555264],
    # )
    # async def close_application(self, ctx: SlashContext):
    #     try:
    #         if staff_role not in ctx.author.roles:
    #             await ctx.send("You do not have permission to close applications.")
    #             return
    #         # Fetch the user's application channel
    #         cur.execute("SELECT interview_channel FROM interview_channels WHERE user = ?", (ctx.target_user.id,))
    #         channel_id = cur.fetchone()
    #         channel = ctx.guild.get_channel(channel_id[0])
    #         # Delete the channel
    #         await channel.delete()
    #         # Fetch the user's review channel
    #         cur.execute("SELECT review_channel FROM interview_channels WHERE user = ?", (ctx.target_user.id,))
    #         channel_id = cur.fetchone()
    #         channel = ctx.guild.get_channel(channel_id[0])
    #         # Delete the channel
    #         await channel.delete()
    #     except BaseException as e:
    #         print(e)
    #         await ctx.send(
    #             "An error occurred while trying to close the application channel."
    #         )
    #
    # # If the member leaves, delete their application channels
    # @listen()
    # async def on_member_remove(self, event: MemberRemove):
    #     cur.execute("SELECT interview_channel, review_channel FROM interview_channels WHERE user = ?", (event.member.id,))
    #     channels = cur.fetchone()
    #     if channels:
    #         channel = event.guild.get_channel(channels[0])
    #         await channel.delete()
    #         channel = event.guild.get_channel(channels[1])
    #         await channel.delete()
    #     cur.execute("DELETE FROM interview_channels WHERE user = ?", (event.member.id,))
    #     con.commit()
    #
    #
    #

def setup(client):
    Tickets(client)
