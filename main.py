from responses import lonely_chat
from discord import Client, Intents, Interaction, app_commands
from dotenv import load_dotenv
from typing import Final

import discord
import json
import os

# ENVIRONMENT VARIABLES
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")
GUILD_ID: Final[int] = int(os.getenv("GUILD_ID"))
WELCOME_CHANNEL_ID: Final[int] = int(os.getenv("WELCOME_CHANNEL_ID"))

# BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
intents.members = True  # NOQA


# DISCORD CLIENT CLASS
def get_rank(user_data: dict) -> int:
    total_messages: int = user_data['total_messages']
    total_exp: int = user_data['exp']

    # Calculate the average score per message
    avg_score: float = total_exp / total_messages if total_messages > 0 else 0

    # Calculate the final rank
    user_rank: int = int(avg_score * 0.5)

    return user_rank


def get_score(message: str) -> int:
    message: str = message.lower()
    points: int = 0

    # Assign 1 point for each character in the message
    points += len(message)

    # Assign 10 points if the message is a complete sentence
    if message.endswith('.'):
        points += 10

    # Assign 5 points for each occurrence of a keyword
    keywords: list[str] = ['help', 'please', 'thank you']
    points += sum(message.count(keyword) * 5 for keyword in keywords)

    return points


class DiscordClient(Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self) -> None:
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"{self.user} has connected to Discord!")

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user:
            return

        username: str = str(message.author)
        user_message: str = message.content
        channel: str = str(message.channel)

        print(f'[{channel}] {username}: "{user_message}"')
        await self.process_message(message)

    async def on_member_join(self, member):
        channel = self.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            await channel.send(f'Welcome to the server, {member.mention}! Feel free to introduce yourself.')

    async def process_message(self, message: discord.Message) -> None:
        username: str = str(message.author)
        user_message: str = message.content

        if not user_message:
            print("INFO: User message is empty")
            return

        is_private = user_message[0] == '?'
        if is_private:
            user_message = user_message[1:]

        user_data: dict = self.get_user_data(username)
        user_data['exp'] += get_score(user_message)
        user_data['total_messages'] += 1
        user_data: dict = self.update_user_data(username, user_data)

        database = self.get_database()

        if username in database['lonely-list']:
            try:
                response: str = lonely_chat(user_message)
                await (message.author.send(response) if is_private else message.channel.send(response))
            except Exception as e:
                print("Error in processing message:", e)

        new_rank: int = get_rank(user_data)
        if user_data['rank'] != new_rank:
            user_data['rank'] = new_rank
            self.update_user_data(username=username, user_data=user_data)
            response = f"Congratulations {message.author.mention}! You've reached rank {new_rank}."
            await (message.author.send(response) if is_private else message.channel.send(response))

    def get_database(self) -> dict:
        try:
            with open('database.json', 'r') as f:
                database: dict = json.load(f)
        except FileNotFoundError:
            database: dict = {"lonely-list": []}
            self.update_database(database)
        return database

    def update_database(self, new_database: dict) -> dict:
        with open('database.json', 'w') as f:
            json.dump(new_database, f, indent=4)
        return new_database

    def get_user_data(self, username: str) -> dict:
        database: dict = self.get_database()

        if username not in database:
            self.update_user_data(username=username, user_data={'exp': 0, 'total_messages': 0, 'rank': 0})
            database = self.get_database()

        return database[username]

    def update_user_data(self, username: str, user_data: dict) -> dict:
        database: dict = self.get_database()
        database[username] = user_data
        self.update_database(database)
        return database[username]


client = DiscordClient()


# HANDLING COMMANDS
@app_commands.checks.cooldown(1, 3)
@client.tree.command(
    name="ping",
    description="Responds with Pong!",
    guild=discord.Object(id=GUILD_ID)
)
async def ping(interaction: Interaction) -> None:
    await interaction.response.send_message("Pong!")


@ping.error  # Tell the user when they've got a cooldown
async def on_command_error(interaction: Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        if not interaction.response.is_done():
            await interaction.response.send_message(str(error), ephemeral=True)


@app_commands.checks.cooldown(1, 7)
@client.tree.command(
    name="chat",
    description="I'm feeling lonely. Join the club ❤️... or leave it.",
    guild=discord.Object(id=GUILD_ID)
)
async def chat(interaction: Interaction) -> None:
    user: discord.User = interaction.user
    username: str = str(user)

    database: dict = client.get_database()

    if username in database['lonely-list']:
        database['lonely-list'].remove(username)
        response = "You've been removed from the lonely list."
    else:
        database['lonely-list'].append(username)
        response = "You're now part of the lonely list. ❤️"

    client.update_database(database)
    await interaction.response.send_message(response)


@chat.error  # Tell the user when they've got a cooldown
async def on_command_error(interaction: Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        if not interaction.response.is_done():
            await interaction.response.send_message(str(error), ephemeral=True)


@app_commands.checks.cooldown(1, 3)
@client.tree.command(
    name="rank",
    description="Check your current rank.",
    guild=discord.Object(id=GUILD_ID)
)
async def rank(interaction: Interaction) -> None:
    username: str = str(interaction.user)
    user_data = client.get_user_data(username)
    await interaction.response.send_message(
        f"{interaction.user.mention}, you're currently at rank {user_data['rank']}.")


@rank.error  # Tell the user when they've got a cooldown
async def on_command_error(interaction: Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        if not interaction.response.is_done():
            await interaction.response.send_message(str(error), ephemeral=True)


@app_commands.checks.cooldown(1, 3)
@client.tree.command(
    name="exp",
    description="Check your current EXP level.",
    guild=discord.Object(id=GUILD_ID)
)
async def exp(interaction: Interaction) -> None:
    username: str = str(interaction.user)
    user_data = client.get_user_data(username)
    await interaction.response.send_message(
        f"{interaction.user.mention}, you currently have {user_data['exp']} EXP.")


@exp.error  # Tell the user when they've got a cooldown
async def on_command_error(interaction: Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        if not interaction.response.is_done():
            await interaction.response.send_message(str(error), ephemeral=True)


@app_commands.checks.cooldown(1, 3)
@client.tree.command(
    name="messages",
    description="View your messages count",
    guild=discord.Object(id=GUILD_ID)
)
async def exp(interaction: Interaction) -> None:
    username: str = str(interaction.user)
    user_data = client.get_user_data(username)
    await interaction.response.send_message(
        f"{interaction.user.mention}, you have written {user_data['total_messages']} messages!")


@exp.error  # Tell the user when they've got a cooldown
async def on_command_error(interaction: Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        if not interaction.response.is_done():
            await interaction.response.send_message(str(error), ephemeral=True)


@app_commands.checks.cooldown(1, 3)
@client.tree.command(
    name="stats",
    description="Check your current stats.",
    guild=discord.Object(id=GUILD_ID)
)
async def stats(interaction: Interaction) -> None:
    user: discord.User = interaction.user
    username: str = str(user)
    user_data: dict = client.get_user_data(username)

    user_rank: int = user_data['rank']
    user_exp: int = user_data['exp']
    user_messages: int = user_data['total_messages']

    response = f"""
{user.mention}, here are your current stats:
> **User**: {username}
> - **Rank:** {user_rank}
> - **Experience Points:** {user_exp}
> - **Total Messages:** {user_messages}
"""
    await interaction.response.send_message(response)


@stats.error  # Tell the user when they've got a cooldown
async def on_command_error(interaction: Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        if not interaction.response.is_done():
            await interaction.response.send_message(str(error), ephemeral=True)


# MAIN ENTRY POINT
def main() -> None:
    if not os.path.exists('database.json'):
        client.update_database({"lonely-list": []})

    print("Bot is starting...")
    try:
        client.run(TOKEN)
    except KeyboardInterrupt:
        print("Bot is shutting down...")


if __name__ == '__main__':
    main()
