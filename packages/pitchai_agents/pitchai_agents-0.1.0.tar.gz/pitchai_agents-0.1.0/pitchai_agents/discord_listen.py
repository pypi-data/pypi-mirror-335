import discord
import asyncio
from discord.ext import commands
from agent.dev_loop import start_dev_until_succeed
import uuid
import os
from faker import Faker

fake = Faker()

TOKEN = 'MTM0NzY3NDAwODA2MTIxNDc1NA.Gs419x.nq78u-L6atKDBeIWcN1TFpRle3ys0nD6dX3aOw'
CHANNEL_ID = 1347672879332069456  # Converted to an integer

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

# Define a background listener for additional messages in the thread.
async def listen_for_thread_messages(thread, agent_name):
    def thread_check(message):
        return message.channel.id == thread.id and message.author != bot.user
    while True:
        try:
            msg = await bot.wait_for('message', check=thread_check)
            print("New message in thread:", msg.content)
            filepath = f'/Users/sethvanderbijl/PitchAI Code/agent/logs/incoming/{agent_name}_incoming.md'
            # Ensure parent directory exists
            parent_path = os.path.dirname(filepath)
            if not os.path.exists(parent_path):
                os.makedirs(parent_path, exist_ok=True)
            with open(filepath, 'a') as f:
                f.write(f"\n{msg.content}")
        except Exception as e:
            print("Error while listening to thread messages:", e)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    # Optional: send a message automatically when the bot comes online
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        channel = await bot.fetch_channel(CHANNEL_ID)
    if channel:
        await channel.send("Bot is now online!")
    await start_listening(None)

@bot.command(name='work')
async def start_listening(ctx):
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        channel = await bot.fetch_channel(CHANNEL_ID)
    
    if channel:
        # Send the initial message to the channel
        initial_message = await channel.send("I am ready to start working on the task. What should I do?")
        # Create a thread from the initial message
        thread = await initial_message.create_thread(name="Task Discussion", auto_archive_duration=60)
        await thread.send("Please reply in this thread.")

        # Define a check for messages in the thread (and not from the bot)
        def check(message):
            return message.channel.id == thread.id and message.author != bot.user

        try:
            # Wait for the initial response that starts the dev_loop
            response = await bot.wait_for('message', check=check)
            
            # Parse the response into its components:
            response_content = response.content.strip()
            response_lines = response_content.split('\n')
            project_path = response_lines[0]  # e.g., "/path/to/project"
            interpreter_path = response_lines[1]  # e.g., "/path/to/interpreter"
            goal = '\n'.join(response_lines[2:])
            
            # Use the thread's send method as the communication callback
            async def communication_callback(msg):
                if len(msg) > 2000:
                    msg = msg[:1997] + "..."
                try:
                    await thread.send(msg)
                except Exception as e:
                    print(f"Could not send message to thread: {e}")

            # Create agent name + id
            agent_name = f"{fake.name()}_{fake.random_int(0, 1000)}"
            print(f"Starting dev_loop for agent: {agent_name}")

            # Start the background listener so that any additional messages in the thread are printed.
            asyncio.create_task(listen_for_thread_messages(thread, agent_name))

            # Start the dev_loop process (this awaits until it completes)
            await start_dev_until_succeed(goal, project_path, interpreter_path, communication_callback=communication_callback, agent_id=agent_name)
            
            print(f"Received response: {response.content.strip()}")
        except asyncio.TimeoutError:
            await thread.send("No response received in time.")
            print("Timed out waiting for a response.")
    else:
        if ctx:
            await ctx.send(f"Channel with ID {CHANNEL_ID} not found.")

bot.run(TOKEN)
