import discord
import asyncio

# Function to send a message to Discord and wait for a response
async def send_message_and_wait(message_content):
    token = 'MTM0NzY3NDAwODA2MTIxNDc1NA.Gs419x.nq78u-L6atKDBeIWcN1TFpRle3ys0nD6dX3aOw'
    channel_id = '1347672879332069456'
    # Create a Discord client
    client = discord.Client(intents=discord.Intents.all())

    # Event listener for when the bot is ready
    @client.event
    async def on_ready():
        print(f'Logged in as {client.user}!')

        # Get the channel
        channel = await client.fetch_channel(channel_id)
        if not channel:
            raise ValueError(f"Channel with ID {channel_id} not found.")

        # Send the message
        await channel.send(message_content)

    # Event listener for when a message is received
    @client.event
    async def on_message(message):
        if message.channel.id == channel_id and message.author != client.user:
            # Print received message for debugging
            print(f'Received message: {message.content.strip()}')
            await client.close()
            return message.content.strip()

    try:
        # Run the client with the provided token
        await client.start(token)
        # Wait indefinitely until the message is received
        await asyncio.sleep(float('inf'))
    finally:
        await client.close()

# Example usage
async def main():
    message_content = "Hello, Discord! What is your response?"

    # Call the send_message_and_wait function
    response = await send_message_and_wait(message_content)
    print(f'Received response: {response}')

if __name__ == "__main__":
    asyncio.run(main())
