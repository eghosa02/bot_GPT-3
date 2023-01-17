import os
import openai
import discord
from discord import app_commands
from discord.ext import commands
import time
import random
import sqlite3
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from io import BytesIO
#from alive import keep
import UI
import asyncio

openai.api_key = "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"

client = commands.Bot(command_prefix='>', intents=discord.Intents.all())
client.eresie = ["dannazione","**AAAAAAAAAAAAAAAAAAAAAAAAAAA**","el puerto rico", "santo crispino", "paeya", "coccoricò", "sant'Armadillo"]
client.timeout = 10

def updateList(users:list, table:str):
    for id in users[4]:
        if users[1][users[4].index(id)] != -1:
            users[2][users[4].index(id)] += int(time.time()- users[1][users[4].index(id)])
            users[1][users[4].index(id)] = time.time()
            try:
                conn = sqlite3.connect('database.db')
                conn.row_factory = sqlite3.Row
                conn.executescript(f"UPDATE {table} SET actualDelay={users[1][users[4].index(id)]}, actualTime={users[2][users[4].index(id)]} WHERE identify='{id}'")
                conn.commit()
                conn.close()
            except:
                pass

def putIn(member:int, users:list, guild_id:int, table:str):
    users[0].append(member)         
    users[1].append(-1)             
    users[2].append(0)  
    users[3].append(guild_id)  
    if len(users[4])>0:
        users[4].append(users[4][len(users[4])-1]+1)       
    else:
        users[4].append(1)
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        conn.execute(f'INSERT INTO {table}(usernameId, actualDelay, actualTime, serverId, identify) VALUES (?,?,?,?,?)', (member, -1, 0, guild_id,users[4][len(users[4])-1],))
        conn.commit()
        conn.close()
    except:
        pass

def getAllChannels():
    channels = []
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        accounts = conn.execute('SELECT * FROM channels').fetchall()
        for i in accounts:
            channels.append(i["channelId"])
        conn.close()
    except:
        pass
    return channels

def getAllUsers(table:str):
    users = [[],[],[],[],[]]
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        accounts = conn.execute(f'SELECT * FROM {table}').fetchall()
        for i in accounts:
            users[0].append(i["usernameId"])
            users[1].append(i["actualDelay"])
            users[2].append(i["actualTime"])
            users[3].append(i["serverId"])
            users[4].append(i["identify"])
        conn.close()
    except:
        pass
    return users

def updateTime(actualTime, actualDelay, id, guild_id, table:str):
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        conn.executescript(f"UPDATE {table} SET actualTime={actualTime}, actualDelay={actualDelay} WHERE usernameId='{id}' AND serverId='{guild_id}'")
        conn.commit()
        conn.close()
    except:
        pass

@client.event
async def on_ready():
    client.loop.create_task(updating())
    try:
        await client.tree.sync()
    except Exception as e:
        print(e)
    print('ready')

@client.event
async def on_command_error(ctx, error):
    await ctx.send(f"{random.choice(client.eresie)}, {error}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if not message.guild:
        print(message.author.display_name+':', message.content)
        try:
            response = openai.Completion.create(model="text-davinci-003", prompt=message.content, temperature=0, max_tokens=2048)
            await message.channel.send(response['choices'][0]['text'])
        except:
            pass
    await client.process_commands(message)

@client.event
async def on_voice_state_update(member, before, after):
    camChannels = getAllChannels()
    users = getAllUsers("accounts")
    disconnected = before.channel is not None and after.channel is None
    isWebcamOn = before.self_video is False and after.self_video is True
    isWebcamOff = before.self_video is True and after.self_video is False
    isInList = member.id in users[0] and member.guild.id in users[3]
    de = None

    if disconnected:
        de = before.channel.id
    else:
        de = after.channel.id

    if de in camChannels:
        if not isInList:
            putIn(member.id, users, member.guild.id, "accounts")
        if isWebcamOn:
            users[1][users[0].index(member.id)] = time.time()
            try:
                conn = sqlite3.connect('database.db')
                conn.row_factory = sqlite3.Row
                conn.executescript(f"UPDATE accounts SET actualDelay={users[1][users[0].index(member.id)]} WHERE usernameId='{member.id}' AND serverId='{member.guild.id}'")#MOD
                conn.commit()
                conn.close()
            except:
                pass
        elif disconnected or isWebcamOff:
            if users[1][users[0].index(member.id)]!=-1:
                users[2][users[0].index(member.id)] += int(time.time() - users[1][users[0].index(member.id)])
                users[1][users[0].index(member.id)] = -1
                actualTime = users[2][users[0].index(member.id)]
                actualDelay = users[1][users[0].index(member.id)]
                updateTime(actualTime,actualDelay,member.id, member.guild.id, "accounts")
#####################################################################
    
    generalUsers  = getAllUsers("accounts_2")

    if not (member.id in generalUsers[0] and member.guild.id in generalUsers[3]):
            putIn(member.id, generalUsers, member.guild.id, "accounts_2")
    if before.channel is None and after.channel is not None:
        generalUsers[1][generalUsers[0].index(member.id)] = time.time()
        try:
            conn = sqlite3.connect('database.db')
            conn.row_factory = sqlite3.Row
            conn.executescript(f"UPDATE accounts_2 SET actualDelay={generalUsers[1][generalUsers[0].index(member.id)]} WHERE usernameId='{member.id}' AND serverId='{member.guild.id}'")#MOD
            conn.commit()
            conn.close()
        except:
            pass
    elif before.channel is not None and after.channel is None:
        if generalUsers[1][generalUsers[0].index(member.id)] != -1:
            generalUsers[2][generalUsers[0].index(member.id)] += int(time.time() - generalUsers[1][generalUsers[0].index(member.id)])
            generalUsers[1][generalUsers[0].index(member.id)] = -1
            actualTime = generalUsers[2][generalUsers[0].index(member.id)]
            actualDelay = generalUsers[1][generalUsers[0].index(member.id)]
            updateTime(actualTime,actualDelay,member.id, member.guild.id, "accounts_2")
            #print(f"{generalUsers[2][generalUsers[0].index(member.id)]} secondi")###############################################################################################################################################################

async def updating():
    while True:
        users = getAllUsers("accounts")
        generlausers = getAllUsers("accounts_2")
        updateList(users, "accounts")
        updateList(generlausers, "accounts_2")
        await asyncio.sleep(10)

@client.command()
async def setChannel(ctx, *,channelsids:str):
    channelsid = channelsids.split(" ")
    camChannels = getAllChannels()
    for channelid in channelsid:
        if not int(channelid) in camChannels:
            conn = sqlite3.connect('database.db')
            conn.row_factory = sqlite3.Row
            conn.execute('INSERT INTO channels(channelId) VALUES (?)', (channelid,))
            conn.commit()
    conn.close()

@client.command()
async def getTime(ctx, mode:str):

    if mode.lower() == "general":
        users:list = getAllUsers("accounts_2")
    else:
        users:list = getAllUsers("accounts")

    if ctx.author.id in users[0]:
        if ctx.guild.id == users[3][users[0].index(ctx.author.id)]:
            times = ""
            if users[1][users[0].index(ctx.author.id)] == -1:
                ore = int(users[2][users[0].index(ctx.author.id)]/3600)
                min = int(users[2][users[0].index(ctx.author.id)]/60)
                sec = int(users[2][users[0].index(ctx.author.id)])
                if ore != 0:
                    times = f"{ore} ore"
                elif ore == 0 and min != 0:
                    times = f"{min} minuti"
                elif ore == 0 and min == 0 and sec != 0:
                    times = f"{sec} secondi"
            else:
                ore = int(((int(time.time() - users[1][users[0].index(ctx.author.id)]))+users[2][users[0].index(ctx.author.id)])/3600)
                min = int(((int(time.time() - users[1][users[0].index(ctx.author.id)]))+users[2][users[0].index(ctx.author.id)])/60)
                sec = int(((int(time.time() - users[1][users[0].index(ctx.author.id)]))+users[2][users[0].index(ctx.author.id)]))
                if ore != 0:
                    times = f"{ore} ore"
                elif ore == 0 and min != 0:
                    times = f"{min} minuti"
                elif ore == 0 and min == 0 and sec != 0:
                    times = f"{min} secondi"

            res = 128
            name = ctx.author.display_name
            s = Image.open("nero.jpg")
            x,y = s.size
            font = ImageFont.truetype("arial.ttf", size=20)
            ImageDraw.Draw(s).text(xy=(50,50),text=name,fill=(255, 255, 255), font=font)
            ImageDraw.Draw(s).text(xy=(50,100),text=times,fill=(255, 255, 255), font=font)
            s.save("sis.png")
            u = Image.open("sis.png")
            a = Image.open(BytesIO(await ctx.author.display_avatar.read())).resize((res,res)).convert('RGB')
            npp = np.array(a)
            h, w = a.size
            alpha = Image.new('L', a.size, 0)
            draw = ImageDraw.Draw(alpha)
            draw.pieslice([0, 0, h, w], 0, 360, fill=255)
            nalpha = np.array(alpha)
            npp = np.dstack((npp, nalpha))
            Image.fromarray(npp).save('ico.png')
            a = Image.open("ico.png")
            u.paste(a, (int((x / 2) - (res / 2)), int(((y / 2) - (res / 2)))), a)
            u.save("benvenuto.png")
            file = discord.File("benvenuto.png")
            await ctx.send(file=file)
            os.remove('sis.png')
            os.remove('ico.png')
            os.remove('benvenuto.png')
        else:
            await ctx.send("non sei in classifica in questo server")
    else:
        await ctx.send("non sei presente")

@client.command()
async def getClassify(ctx, mode:str):
    mod = None
    if mode.lower() == "general":
        users:list = getAllUsers("accounts_2")
        mod = False
    else:
        users:list = getAllUsers("accounts")
        mod = True

    top:dict = {}
    if mod:
        updateList(users, "accounts")
    else:
        updateList(users, "accounts_2")

    #print(users)###############################################################################################################################################################

    for i in users[0]:
        top[i] = users[2][users[0].index(i)]
    top = sorted(top.items(), key=lambda x:x[1], reverse=True)[:5]
    print(top)
    count = 1
    if ctx.guild.id in users[3]:
        id_ref = users[3][users[3].index(ctx.guild.id)]
        for i in top:
            if users[3][users[0].index(i[0])] == id_ref:
                ore = int(i[1]/3600)
                min = int(i[1]/60)
                sec = i[1]
                if ore != 0:
                    times = f"{ore} ore"
                elif ore == 0 and min != 0:
                    times = f"{min} minuti"
                elif ore == 0 and min == 0:
                    times = f"{sec} secondi"
                if ore>=100:
                    await ctx.send(f"{count}° con {times} <@{i[0]}>, HAI VINTO TUTTO E GLI ALTRI SONO MERDE")
                    break
                else:
                    await ctx.send(f"{count}° con {times} <@{i[0]}>")
                count += 1
    else:
        await ctx.send("nessuna lista nel seguente server")

@client.tree.command(name="say")
@app_commands.describe(sentence="ask me something")
async def say(interaction:discord.interactions, sentence:str):
    await interaction.response.defer()
    view = UI.UI(timeout=client.timeout)
    response = openai.Completion.create(model="text-davinci-003", prompt=sentence, temperature=0, max_tokens=2048)
    message = interaction.followup
    mention = interaction.user.mention
    msg = await message.send(mention+': '+sentence+'\n'+response['choices'][0]['text'], view = view)
    await view.wait()
    if view.reg:
        await message.edit_message(msg.id, view=view)
        await re_say(message, sentence, msg.id, mention)
    else:
        for i in view.children:
            i.disabled = True
        await message.edit_message(msg.id, view=view)

async def re_say(message, sentence:str, id:int, mention):
    view = UI.UI(timeout=client.timeout)
    response = openai.Completion.create(model="text-davinci-003", prompt=sentence, temperature=0, max_tokens=2048)
    await message.edit_message(id, content=mention+': '+sentence+'\n'+response['choices'][0]['text'], view=view)
    await view.wait()
    if view.reg: 
        await message.edit_message(id, view=view)
        await re_say(message, sentence, id, mention)
    else:
        for i in view.children:
            i.disabled = True
        await message.edit_message(id, view=view)

@client.tree.command(name="image")
@app_commands.describe(prompt="ask me something to draw")
async def image(interaction:discord.interactions, prompt:str):
    await interaction.response.defer()
    view = UI.UI(timeout=client.timeout)
    response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    message = interaction.followup
    mention = interaction.user.mention
    msg = await message.send(mention+': '+prompt+'\n'+response['data'][0]['url'], view=view)
    await view.wait()
    if view.reg:
        await message.edit_message(msg.id, view=view)
        await re_image(message, prompt, msg.id, mention)
    else:
        for i in view.children:
            i.disabled = True
        await message.edit_message(msg.id, view=view)

async def re_image(message, prompt:str, id:int, mention):
    view = UI.UI(timeout=client.timeout)
    response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    await message.edit_message(id, content=mention+': '+prompt+'\n'+response['data'][0]['url'], view=view)
    await view.wait()
    if view.reg: 
        await message.edit_message(id, view=view)
        await re_image(message, prompt, id, mention)
    else:
        for i in view.children:
            i.disabled = True
        await message.edit_message(id, view=view)#textModelSubmit()

@client.command()
async def delete(ctx, n:int):
    await ctx.channel.purge(limit=n)

#keep()

client.run('ODczMzQ5NzczODA0MDQ0MzE4.GKhBcn.IExjE413s8qf31IhbhcYhBrSNzaM0XHhbkz2MU')