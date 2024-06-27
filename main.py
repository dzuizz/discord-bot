from responses import lonely_chat
from dotenv import load_dotenv
from typing import Final, Any

import discord
import json
import os

# ENVIRONMENT VARIABLES
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")
GUILD_ID: Final[str] = os.getenv("GUILD_ID")
WELCOME_CHANNEL_ID: Final[str] = os.getenv("WELCOME_CHANNEL_ID")

# BOT SETUP
intents: discord.Intents = discord.Intents.default()
intents.message_content = True  # NOQA
intents.members = True  # NOQA
client: discord.Client = discord.Client(intents=intents)
tree: discord.app_commands.CommandTree = discord.app_commands.CommandTree(client)


# SCORING FUNCTIONALITY
def score(message: str) -> int:
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


def get_rank(user_data: dict) -> int:
    total_messages: int = user_data['total_messages']
    total_exp: int = user_data['exp']

    # Calculate the average score per message
    avg_score: float = total_exp / total_messages if total_messages > 0 else 0

    # Calculate the final rank
    user_rank: int = int(avg_score * 0.5)

    return user_rank


# DATABASE FUNCTIONALITY
def get_database() -> dict:
    try:
        with open('database.json', 'r') as f:
            database: dict = json.load(f)
    except FileNotFoundError:
        database: dict = {"lonely-list": []}
        update_database(database)
    return database


def update_database(new_database: dict) -> dict:
    with open('database.json', 'w') as f:
        json.dump(new_database, f, indent=4)
    return new_database


def get_user_data(username: str) -> dict:
    database: dict = get_database()

    if username not in database:
        update_user_data(username=username, user_data={'exp': 0, 'total_messages': 0, 'rank': 0})
        database = get_database()

    return database[username]


def update_user_data(username: str, user_data: dict) -> dict:
    database: dict = get_database()
    database[username] = user_data
    update_database(database)
    return database[username]


# MESSAGE FUNCTIONALITY
async def process_message(message: discord.Message) -> None:
    username: str = str(message.author)
    user_message: str = message.content

    if not user_message:
        print("INFO: User message is empty")
        return

    is_private = user_message[0] == '?'
    if is_private:
        user_message = user_message[1:]

    user_data: dict = get_user_data(username)
    user_data['exp'] += score(user_message)
    user_data['total_messages'] += 1
    user_data: dict = update_user_data(username, user_data)

    database = get_database()

    if username in database['lonely-list']:
        try:
            response: str = lonely_chat(user_message)
            await (message.author.send(response) if is_private else message.channel.send(response))
        except Exception as e:
            print("Error in processing message:", e)

    new_rank: int = get_rank(user_data['exp'])
    if user_data['rank'] != new_rank:
        user_data['rank'] = new_rank
        update_user_data(username=username, user_data=user_data)
        response = f"Congratulations {message.author.mention}! You've reached rank {new_rank}."
        await (message.author.send(response) if is_private else message.channel.send(response))


# HANDLING BOT STARTUP
@client.event
async def on_ready() -> None:
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"{client.user} has connected to Discord!")


# HANDLING NEW MEMBER
@client.event
async def on_member_join(member):
    channel = client.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f'Welcome to the server, {member.mention}! Feel free to introduce yourself.')

# HANDLING MESSAGES
@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await process_message(message)


# HANDLING COMMANDS
@discord.app_commands.checks.cooldown(1, 3)
@tree.command(
    name="ping",
    description="Responds with Pong!",
    guild=discord.Object(id=GUILD_ID)
)
async def ping(interaction: discord.interactions.Interaction) -> None:
    await interaction.response.send_message("Pong!")


@ping.error  # Tell the user when they've got a cooldown
async def on_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CommandOnCooldown):
        if not interaction.response.is_done():
            await interaction.response.send_message(str(error), ephemeral=True)


@discord.app_commands.checks.cooldown(1, 3)
@tree.command(
    name="chat",
    description="I'm feeling lonely. Join the club ❤️... or leave it.",
    guild=discord.Object(id=GUILD_ID)
)
async def chat(interaction: discord.interactions.Interaction) -> None:
    user: discord.User = interaction.user
    username: str = str(user)

    database: dict = get_database()

    if username in database['lonely-list']:
        database['lonely-list'].remove(username)
        response = "You've been removed from the lonely list."
    else:
        database['lonely-list'].append(username)
        response = "You're now part of the lonely list. ❤️"

    update_database(database)
    await interaction.response.send_message(response)


@chat.error  # Tell the user when they've got a cooldown
async def on_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CommandOnCooldown):
        if not interaction.response.is_done():
            await interaction.response.send_message(str(error), ephemeral=True)


@discord.app_commands.checks.cooldown(1, 3)
@tree.command(
    name="rank",
    description="Check your current rank.",
    guild=discord.Object(id=GUILD_ID)
)
async def rank(interaction: discord.interactions.Interaction) -> None:
    username: str = str(interaction.user)
    user_data = get_user_data(username)
    await interaction.response.send_message(
        f"{interaction.user.mention}, you're currently at rank {user_data['rank']}.")


@rank.error  # Tell the user when they've got a cooldown
async def on_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CommandOnCooldown):
        if not interaction.response.is_done():
            await interaction.response.send_message(str(error), ephemeral=True)


@discord.app_commands.checks.cooldown(1, 3)
@tree.command(
    name="stats",
    description="Check your current stats.",
    guild=discord.Object(id=GUILD_ID)
)
async def stats(interaction: discord.interactions.Interaction) -> None:
    user: discord.User = interaction.user
    username: str = str(user)
    user_data: dict = get_user_data(username)

    user_exp: int = user_data['exp']
    user_rank: int = user_data['rank']

    response = f"""
{user.mention}, here are your current stats:
> **User**: {username}
> - **Experience Points:** {user_exp}
> - **Rank:** {user_rank}
"""
    await interaction.response.send_message(response)


@stats.error  # Tell the user when they've got a cooldown
async def on_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CommandOnCooldown):
        if not interaction.response.is_done():
            await interaction.response.send_message(str(error), ephemeral=True)


# MAIN ENTRY POINT
def main() -> None:
    if not os.path.exists('database.json'):
        update_database({"lonely-list": []})

    print("Bot is starting...")
    try:
        client.run(TOKEN)
    except KeyboardInterrupt:
        print("Bot is shutting down...")


if __name__ == '__main__':
    main()
