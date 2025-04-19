import discord
import os
from dotenv import load_dotenv
from ai import ask_openai
from database import ConversationDatabase
import re

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)
db = ConversationDatabase()

BOT_NAME = None

def match_command(text):
    # Detecta "limpar chat/memória" de várias formas escritas diferentes
    patterns = [
        r"limp(a|e|ar)?( o)? (chat|mem(ó|o)ria|hist(ó|o)rico)?",
        r"esquece(r)?( o)?( chat|mem(ó|o)ria|hist(ó|o)rico)?",
        r"apaga(r)?( o)? (hist(ó|o)rico|mem(ó|o)ria|chat)?"
    ]
    for pattern in patterns:
        if re.search(pattern, text.lower()):
            return "clear"
    return None

def is_message_to_bot(message: discord.Message):
    # Só responde se for mencionado ou chamado pelo nome
    return (
        message.author != client.user and (
            message.content.lower().startswith(BOT_NAME.lower()) or
            client.user.mentioned_in(message)
        )
    )

@client.event
async def on_ready():
    global BOT_NAME
    BOT_NAME = client.user.display_name
    print(f'Bot {client.user.name} conectado com sucesso.')

@client.event
async def on_message(message):
    if not is_message_to_bot(message):
        return

    user_input = (
        message.content.replace(f"<@{client.user.id}>", "")
        .replace(BOT_NAME or "", "")
        .strip()
    )

    cmd = match_command(user_input)
    if cmd == "clear":
        db.clear_context(guild_id=str(message.guild.id))
        await message.channel.send("Memória (contexto) deste servidor foi limpa com sucesso! 🧹")
        return

    # Recupera o contexto longo por guild
    context = db.get_context(guild_id=str(message.guild.id), token_limit=7000)
    context.append({"role": "user", "content": user_input})

    # Pede resposta ao GPT
    response = await ask_openai(context)

    # Salva o diálogo por guild, marcando role
    db.save_message(guild_id=str(message.guild.id), message=user_input, role="user")
    db.save_message(guild_id=str(message.guild.id), message=response, role="assistant")

    # Responde no canal
    if response.startswith("Ocorreu um erro:"):
        await message.channel.send("Desculpe, houve um erro ao conversar com o GPT.")
    else:
        await message.channel.send(response[:2000])

if __name__ == "__main__":
    client.run(os.getenv("DISCORD_TOKEN"))
