import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import openai
from cogs.botDBMS import BotDatabase

# Load environment variables
load_dotenv()

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)

db = BotDatabase()

def format_conversation_history(conversations):
    """Format conversation history for the GPT context"""
    formatted_history = []
    for msg, response in conversations:
        formatted_history.extend([
            {"role": "user", "content": msg},
            {"role": "assistant", "content": response}
        ])
    return formatted_history

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    db.setup_conversation_table()
    print('--------------------------------------')

@client.event
async def on_message(message):
    await client.process_commands(message)
    
    if message.content.startswith('!'):
        return
        
    if message.author == client.user:
        return
        
    if client.user in message.mentions:
        channel = message.channel
        async with channel.typing():  # Show typing indicator
            try:
                if not openai.api_key:
                    await channel.send("OpenAI API key is not configured.")
                    print("Error: OpenAI API key is not set")
                    return

                recent_conversations = db.get_recent_conversations(
                    message.author.id,
                    channel.id
                )
                
                messages = format_conversation_history(recent_conversations)
                messages.append({"role": "user", "content": message.content})
                
                response = await asyncio.to_thread(
                    openai.ChatCompletion.create,
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=1,
                    max_tokens=2048,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                
                messageToSend = response['choices'][0]['message']['content'].strip()
                
                db.store_conversation(
                    message.author.id,
                    channel.id,
                    message.content,
                    messageToSend,
                    [msg['content'] for msg in messages[:-1]]  
                )
                await channel.send(messageToSend)
                    
            except openai.error.AuthenticationError:
                await channel.send("Authentication error with OpenAI API. Please check the API key.")
                print("Error: Invalid OpenAI API key")
            except openai.error.RateLimitError:
                await channel.send("Rate limit exceeded with OpenAI API. Please try again later.")
                print("Error: OpenAI API rate limit exceeded")
            except openai.error.APIError as e:
                await channel.send("An error occurred with the OpenAI API. Please try again later.")
                print(f"OpenAI API error: {e}")
            except Exception as e:
                await channel.send("An unexpected error occurred.")
                print(f"Unexpected error: {e}")


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py" and filename != "utils.py":
            try:
                await client.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded extension: {filename[:-3]}")
            except Exception as e:
                print(f"Failed to load extension {filename[:-3]}: {e}")

async def main():
    await load_extensions()
    token = os.getenv('TOKEN')
    if token is None:
        raise ValueError("TOKEN is not set in the environment variables")
    try:
        await client.start(token)
    except discord.LoginFailure:
        print("Failed to login. Please check your token.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
def get_bot():
    return client

if __name__ == "__main__":
    asyncio.run(main())
