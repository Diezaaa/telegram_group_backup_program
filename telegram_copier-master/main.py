from pyrogram import Client, filters

# API credentials from https://my.telegram.org
api_id = 27960228
api_hash = "b8c3132ab61115b00ba2a90974b5cc53"

# Mapping between source group and backup group
# key = backup group ID, value = source group ID
GROUP_MAPPING = {
    -1002593050095: -1002908756624,   # backup_group : source_group
    -1002588434895: -1002995195677
}

app = Client("backup_bot", api_id=api_id, api_hash=api_hash)


# Store which groups are in "sync mode"
active_syncs = set()


@app.on_message(filters.command("start") & filters.chat(list(GROUP_MAPPING.keys())))
async def backup_handler(client, message):
    backup_group = message.chat.id

    source_group = GROUP_MAPPING[backup_group]

    await message.reply("⏳ Backing up old messages...")

    # Collect messages in chronological order
    messages = []
    async for msg in client.get_chat_history(source_group, limit=1000):
        messages.append(msg)

    for msg in reversed(messages):  # oldest → newest
        try:
            await msg.copy(chat_id=backup_group)
        except Exception as e:
            print("Skip message:", e)

    await message.reply("✅ Backup finished. Now syncing new messages...")

    # Enable continuous syncing
    active_syncs.add((source_group, backup_group))


# Forward/copy new messages after backup
@app.on_message(filters.chat(list(GROUP_MAPPING.values())))
async def forward_new(client, message):
    for (source, backup) in active_syncs:
        if message.chat.id == source:
            try:
                await message.forward(chat_id=backup)
            except Exception as e:
                print("Error copying:", e)


app.run()