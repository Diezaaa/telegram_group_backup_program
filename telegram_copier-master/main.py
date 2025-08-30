import json
from pywa import WhatsApp, types
from pyrogram import Client, filters

# Telegram setup
api_id = 27960228
api_hash = "b8c3132ab61115b00ba2a90974b5cc53"
app = Client("backup_bot", api_id=api_id, api_hash=api_hash)
dest_chat=-4931692072 # Destination chat in Telegram



# JSON file with all source chat IDs
data_file= "data.json"

# Help command
@app.on_message(filters.chat(dest_chat)& filters.command("help"))
async def help(client, message):
    if message.text == "/help":
        await message.reply("commands:\n"
                            "/add_src [group id with - at the start] - forwards all existing messages and forwards all newly arriving messages.")

@app.on_message(filters.chat(dest_chat)& filters.command("view_sources"))
async def view_sources(client, message):
    if message.text == "/view_sources":
        try:
            # Trying to open and load the existing file
            with open(data_file, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is empty, start with an empty dict
            data = {}
        all_sources = ""

        for src in data["src"]:
            chat = await app.get_chat(src)
            all_sources += f"📂 Group name: {chat.title}, ID: {chat.id}\n"
        await message.reply("Source chats: \n" + all_sources)

@app.on_message(filters.chat(dest_chat)& filters.command("delete_src"))
async def delete_src(client, message):
    if message.text.startswith("/delete_src"):
        try:
            # Trying to open and load the existing file
            with open(data_file, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is empty, start with an empty dict
            data = {}
        try:
            chat_id = int(message.text.split(maxsplit=1)[1])
            if chat_id not in data["src"]:
                chat_id = int(message.text.split(maxsplit=1)[1])
                await message.reply(f"❌ Group wasn't found")

            else:
                data["src"].remove(chat_id)
                with open(data_file, "w") as f:
                    # indent=4 makes the JSON file readable
                    json.dump(data, f, indent=4)
                await message.reply("✅ Source group was deleted")
        except:
            await message.reply("❌ Invalid format for, example valid value: -4931692072")



# Forwards all messages of certain chat
async def forward_all_messages(client, message, chat_id):

    # Getting chat object
    chat = await app.get_chat(chat_id)

    # Trying to get all messages in chat and placing them into variable.
    # If a group isn't found then a suitable message would appear.
    messages = []
    async for msg in client.get_chat_history(chat_id, limit=None):
        messages.append(msg)
    await message.reply(f'🔄 Syncing chat "{chat.title}" (ID: {chat_id}) in progress.')

    # Reversing messages to make the messages be sorted from oldest to newest.
    # Then forwarding the message with a notation of the source.
    for msg in reversed(messages):  # oldest → newest
        try:
            await msg.forward(chat_id=dest_chat)
            src = f"# Source: Telegram, group name: {chat.title}, group id: {chat_id}."
            await app.send_message(chat_id=dest_chat, text=src)
        except Exception as e:
            print("Skip message:", e)

    await message.reply(f'✅ Syncing chat "{chat.title}" (ID: {chat_id}) was completed successfully.')


@app.on_message(filters.chat(dest_chat)& filters.command("add_src"))
async def add_src_chat(client, message):
    if message.text.startswith("/add_src"):
        try:
            # Trying to open and load the existing file
            with open(data_file, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is empty, start with an empty dict
            data = {}

        chat_link = message.text.split(maxsplit=1)[1]

        try:
            chat = await app.get_chat(chat_link)
            print(chat.id)
            if "src" in data and chat.id not in data["src"]:
                src = message.text
                data["src"].append(chat.id)
            elif "src" not in data:
                data["src"] = [chat.id]
            elif chat.id in data["src"]:
                await message.reply(f'📂 Chat "{chat.title}" already saved.')
                return

            await forward_all_messages(client, message, chat.id)

            with open(data_file, "w") as f:
                # indent=4 makes the JSON file readable
                json.dump(data, f, indent=4)
        except:
            await message.reply(f"❌ Group wasn't found")

@app.on_message()
async def forward_new(client, message):
    try:
        with open(data_file, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    if "src" in data and message.chat.id in data["src"]:
        src = f"# Source: Telegram, chat name: {message.chat.title}, group id: {message.chat.id}"
        await message.forward(chat_id=dest_chat)
        await app.send_message(chat_id=dest_chat, text=src)

app.run()