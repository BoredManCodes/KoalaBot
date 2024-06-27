from interactions import slash_command, SlashContext, Embed, Extension, Client, ActionRow, Button, ButtonStyle, Color, Webhook
import sqlite3


print("Fun extension loaded")

con = sqlite3.connect("KoalaBot.db")
cur = con.cursor()

class Fun(Extension):
    def __init__(self, client: Client) -> None:
        self.client: Client = client

    @slash_command(
        name="sudo",
        description="Pretend to be someone else!",
        scopes=["858547359804555264"],
        options=[
            {
                "name": "user",
                "description": "The user to pretend to be.",
                "type": 6,
                "required": True
            },
            {
                "name": "message",
                "description": "The message to send.",
                "type": 3,
                "required": True
            }
        ]
    )
    async def sudo(self, ctx: SlashContext, user: str, message: str):
        # Fetch the users display name and avatar
        user = ctx.guild.get_member(user)
        avatar_url = user.avatar_url
        # Check if a webhook for this channel exists in the database
        cur.execute("SELECT * FROM webhooks WHERE channel_id = ?", (ctx.channel.id,))
        webhook = cur.fetchone()
        if webhook:
            # Fetch the webhook
            webhook_url = webhook[1]
            webhook = Webhook.from_url(webhook_url, self.client)
            await webhook.send(f"{message}", avatar_url=avatar_url, username=user.display_name)
        else:
            # Create a webhook and save it to the database
            webhook = await ctx.channel.create_webhook(name="KoalaBot Sudo")
            cur.execute("INSERT INTO webhooks VALUES (?, ?)", (ctx.channel.id, webhook.url))
            con.commit()
            await webhook.send(f"{message}", avatar_url=avatar_url, username=user.display_name)
        await ctx.send("Message sent!", ephemeral=True)


def setup(client):
    Fun(client)
