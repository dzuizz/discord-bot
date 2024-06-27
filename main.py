from responses import lonely_chat
from dotenv import load_dotenv
from typing import Final

import discord
import json
import os


# ENVIRONMENT VARIABLES
load_dotenv()
GUILD_ID: Final[str] = os.getenv("GUILD_ID")
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# BOT SETUP
intents: discord.Intents = discord.Intents.default()
intents.message_content = True  # NOQA
client: discord.Client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


def update(data: dict) -> dict:
    with open('database.json', 'w') as f:
        json.dump(data, f)
        f.seek(0)

    return json.load(open('database.json', 'r'))


# MESSAGE FUNCTIONALITY
async def process_message(message: discord.Message) -> None:
    username: str = str(message.author)
    user_message: str = message.content

    if not user_message:
        print("User message is empty.")
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    data = json.load(open('database.json', 'r'))
    data["exp"] += len(user_message)
    data = update(data)

    if username in data['lonely-list']:
        try:
            response: str = lonely_chat(user_message)
            await message.author.send(response) if is_private else await message.channel.send(response)
        except Exception as e:
            print("Error in process_message:", e)

    new_rank: int = data["exp"] // 100
    if data["rank"] != new_rank:
        data["rank"] = new_rank
        update(data)
        response = f"Congratulations @{username}! You've reached rank {new_rank}."
        await message.author.send(response) if is_private else await message.channel.send(response)


# HANDLING BOT STARTUP
@client.event
async def on_ready() -> None:
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f'{client.user} has connected to Discord!')


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

@tree.command(
    name="ping",
    description="Responds with Pong!",
    guild=discord.Object(id=GUILD_ID)
)
async def ping(interaction: discord.interactions.Interaction) -> None:
    await interaction.response.send_message("Pong!")


@tree.command(
    name="chat",
    description="I'm feeling lonely. Join the club ❤️... or leave it.",
    guild=discord.Object(id=GUILD_ID)
)
async def chat(interaction: discord.interactions.Interaction) -> None:
    username: str = str(interaction.user)

    with open('database.json', 'r+') as f:
        data = json.load(f)

        if username in data['lonely-list']:
            data['lonely-list'].remove(username)
            response = "You've been removed from the lonely list."
        else:
            data["lonely-list"].append(str(interaction.user))
            response = "You're now part of the lonely list. ❤️"

        f.seek(0)
        json.dump(data, f)

    await interaction.response.send_message(response)


@tree.command(
    name="rank",
    description="Check your current rank.",
    guild=discord.Object(id=GUILD_ID)
)
async def rank(interaction: discord.interactions.Interaction) -> None:
    data = json.load(open('database.json', 'r'))

    await interaction.response.send_message(f"You're currently at rank {data['rank']}.")


# MAIN ENTRY POINT
def main() -> None:
    # Reset database
    with open('database.json', 'w') as f:
        json.dump({
            "lonely-list": [],
            "exp": 0,
            "rank": 0
        }, f)
        f.seek(0)

    print("Bot is starting...")
    try:
        client.run(token=TOKEN)
    except KeyboardInterrupt:
        print("Bot is shutting down...")


if __name__ == '__main__':
    main()
