import discord
import pickle
from datetime import datetime, timedelta

token = "INSERT TOKEN HERE"

class Item:
    def __init__(self,name="",desc="",weight="",wearable=False,key=""):
        self.name = name
        self.desc = desc
        self.weight = weight
        self.wearable = wearable
        self.key = key

class RoomObject:
    def __init__(self,name="",desc="",storage=0,items=[],state="OPEN",key=""):
        self.name = name
        self.desc = desc
        self.storage = storage
        self.items = items
        self.state = state
        self.key = key

class Player:
    def __init__(self,id=0,name="",room="",items=[],clothes=[]):
        self.id = id
        self.name = name
        self.room = room
        self.items = items
        self.clothes = clothes

class Room:
    def __init__(self,id="",name="",items=[],objects=[],doors=[]):
        self.id = id
        self.name = name
        self.items = items
        self.objects = objects
        self.doors = doors

class Door:
    def __init__(self,room1="",room2="",state="OPEN",key=""):
        self.room1 = room1
        self.room2 = room2
        self.state = state
        self.key = key

# Create or load players and rooms dictionaries
try:
    players_in = open("players.pickle","rb")
    players = pickle.load(players_in)
except:
    players = {}
    players_out = open("players.pickle","wb")
    pickle.dump(players, players_out)
    players_out.close()
try:
    rooms_in = open("rooms.pickle","rb")
    rooms = pickle.load(rooms_in)
except:
    rooms = {}
    rooms_out = open("rooms.pickle","wb")
    pickle.dump(rooms, rooms_out)
    rooms_out.close()

carrylimit = 10
wearlimit = 15

# Save
def save():
    players_out = open("players.pickle","wb")
    pickle.dump(players, players_out)
    players_out.close()
    rooms_out = open("rooms.pickle","wb")
    pickle.dump(rooms, rooms_out)
    rooms_out.close()

# Convert author into player name
def playername(author):
    name = ""
    for player in players.values():
        if player.id == author.id:
            name = player.name
    return name

# Convert channel into room name
def roomname(channel):
    name = ""
    for room in rooms.values():
        if room.id == channel.id:
            name = room.name
    return name

# Get string of names from a list of things
def getthingnamestring(thingslist):
    namestring = ""
    if len(thingslist) >= 1:
        namestring = f"`{thingslist[0].name}`"
        if len(thingslist) >= 2:
            for thing in thingslist[1:]:
                namestring += f" `{thing.name}`"
    return namestring

# Get string of names from a list of things
def getstringnamestring(stringslist):
    namestring = ""
    if len(stringslist) >= 1:
        namestring = f"`{stringslist[0]}`"
        if len(stringslist) >= 2:
            for string in stringslist[1:]:
                namestring += f" `{string}`"
    return namestring

# Get a list of things in a list with a specific name
def getmatchingitems(thingslist, name):
    matching_things = []
    for thing in thingslist:
        if thing.name == name:
            matching_things.append(thing)
    return matching_things

# Get the total weight of all items in a list
def gettotalweight(itemlist):
    weight = 0
    for item in itemlist:
        weight += item.weight
    return weight

# Get a list of rooms connected via doors to the current room with a given state
def getdoorroomlist(doorlist, current_room, state="ANY"):
    roomlist = []
    for door in doorlist:
        if door.state == state or state == "ANY":
            if door.room1 == current_room:
                roomlist.append(door.room2)
            else:
                roomlist.append(door.room1)
    return roomlist

# Find a specific door in a list of doors
def finddoor(doorlist, room1, room2):
    for door in doorlist:
        if door.room1 == room1 and door.room2 == room2:
            return door
        elif door.room1 == room2 and door.room2 == room1:
            return door
    return None

client = discord.Client()

@client.event
async def on_ready():
    print(f"Connected as {client.user}")

@client.event
async def on_message(message):

    # Check if the message is a valid command
    if (len(str(message.content)) > 0) and (str(message.content)[0] == "!"):
        # Split the command string into components
        command = str(message.content[1:]).split(" ")
        # Get the author and the channel of the ccmmand
        author = message.author
        channel = message.channel
        # Get whether the user can use admin commands
        admin = "Host" in [str(role) for role in author.roles]

        #########################
        #    PLAYER COMMANDS    #
        #########################

        # Clothes Command
        # !clothes
        if command[0] == "clothes":
            if playername(author) in players.keys():
                try:
                    # Define Variables
                    player = players[playername(author)]
                    itemstring = getthingnamestring(player.clothes)
                    # Run Command
                    if itemstring == "":
                        await channel.send("You are currently not wearing any clothes. :thinking:")
                    else:
                        await channel.send(f"You are currently wearing these clothes:\n{itemstring}")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!clothes`.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Contents Command
        # !contents <object> [num]
        elif command[0] == "contents":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room_name = player.room
                        room = rooms[room_name]
                        object_name = command[1]
                        object_num = 1
                        if len(command) >= 3:
                            object_num = int(command[2])
                        matching_objects = getmatchingitems(room.objects, object_name)
                        # Run Command
                        if len(matching_objects) > 0:
                            if object_num > 0 and object_num <= len(matching_objects):
                                # Define Variables
                                object = matching_objects[object_num-1]
                                itemstring = getthingnamestring(object.items)
                                # Run Command
                                if object.state == "OPEN":
                                    if itemstring == "":
                                        await channel.send(f"There are no items in the `{object.name}`.")
                                    else:
                                        await channel.send(f"The following items are in the `{object.name}`:\n{itemstring}")
                                elif object.state == "LOCKED":
                                    await channel.send(f"The `{object_name}` is locked.")
                                else:
                                    await channel.send(f"The `{object_name}` cannot store any items.")
                            else:
                                await channel.send(f"There are `{len(matching_objects)}` objects here called `{object_name}`, so `[num]` must be specified between `1` and `{len(matching_objects)}`.")
                        else:
                            await channel.send(f"There are no objects here called `{object_name}`.")
                    except:
                        await channel.send("Incorrect command format. The correct format is: `!contents <object> [num]`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Desc Command
        # !desc
        elif command[0] == "desc":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    # Define Variables
                    dest_room = rooms[player.room]
                    dest_channel = client.get_channel(id=rooms[dest_room.name].id)
                    await channel.send(dest_channel.topic)
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Doors Command
        # !doors
        elif command[0] == "doors":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    # Define Variables
                    room = rooms[player.room]
                    room_list = getdoorroomlist(room.doors, room.name, state="OPEN")
                    locked_room_list = getdoorroomlist(room.doors, room.name, state="LOCKED")
                    room_names_string = getthingnamestring([rooms[name] for name in room_list])
                    locked_room_names_string = getthingnamestring([rooms[name] for name in locked_room_list])
                    # Run Command
                    reply = ""
                    if room_names_string == "":
                        reply = "You cannot move anywhere from here."
                    else:
                        reply = f"You can move to the following rooms from here:\n{room_names_string}"
                    if locked_room_names_string != "":
                        reply += f"\nThe doors to the following rooms are locked:\n{locked_room_names_string}"
                    await channel.send(reply)
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Drop Command
        # !drop <item> [num]
        elif command[0] == "drop":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        item_name = command[1]
                        item_num = 1
                        if len(command) >= 3:
                            item_num = int(command[2])
                        matching_items = getmatchingitems(player.items, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                # Run Command
                                room.items.append(item)
                                player.items.remove(item)
                                save()
                                await channel.send(f"You have dropped the `{item_name}`.")
                            else:
                                await channel.send(f"You are holding `{len(matching_items)}` items called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"You are not holding any items called `{item_name}`.")
                    except:
                        await channel.send("Incorrect command format. The correct format is: `!drop <item> [num]`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Drop In Command
        # !dropin <object> [num] <item> [num]
        elif command[0] == "dropin":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        object_name = command[1]
                        try:
                            object_num = int(command[2])
                            item_name = command[3]
                            item_num = 1
                            if len(command) >= 5:
                                item_num = int(command[4])
                        except:
                            object_num = 1
                            item_name = command[2]
                            item_num = 1
                            if len(command) >= 4:
                                item_num = int(command[3])
                        matching_objects = getmatchingitems(room.objects, object_name)
                        matching_items = getmatchingitems(player.items, item_name)
                        # Run Command
                        if len(matching_objects) > 0:
                            if object_num > 0 and object_num <= len(matching_objects):
                                if len(matching_items) > 0:
                                    if item_num > 0 and item_num <= len(matching_items):
                                        # Define Variables
                                        object = matching_objects[object_num-1]
                                        item = matching_items[item_num-1]
                                        weight = gettotalweight(object.items)
                                        # Run Command
                                        if object.state == "OPEN":
                                            if (weight + item.weight) <= object.storage:
                                                object.items.append(item)
                                                player.items.remove(item)
                                                save()
                                                await channel.send(f"You have dropped the `{item_name}` into the `{object.name}`.")
                                            else:
                                                await channel.send(f"You cannot put the `{item.name}` in the `{object.name}` because there is not enough space.")
                                        elif object.state == "LOCKED":
                                            await channel.send(f"The `{object_name}` is locked.")
                                        else:
                                            await channel.send(f"The `{object_name}` cannot store any items.")
                                    else:
                                        await channel.send(f"You are holding `{len(matching_items)}` items called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                                else:
                                    await channel.send(f"You are not holding any items called `{item_name}`.")
                            else:
                                await channel.send(f"There are `{len(matching_objects)}` objects here called `{object_name}`, so `[num]` must be specified between `1` and `{len(matching_objects)}`.")
                        else:
                            await channel.send(f"There are no objects here called `{object_name}`.")
                    except:
                        await channel.send("Incorrect command format. The correct format is: `!dropin <object> [num] <item> [num]`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Goto Command
        # !goto <room>
        elif command[0] == "goto":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        dest_room_name = command[1]
                        room_list = getdoorroomlist(room.doors, room.name, state="OPEN")
                        locked_room_list = getdoorroomlist(room.doors, room.name, state="LOCKED")
                        # Run Command
                        if dest_room_name in room_list:
                            # Define Variables
                            player_id = client.get_user(id=player.id)
                            dest_channel = client.get_channel(id=rooms[dest_room_name].id)
                            overwrite = discord.PermissionOverwrite()
                            # Run Command
                            overwrite.read_messages = None
                            await channel.set_permissions(player_id, overwrite=overwrite)
                            overwrite.read_messages = True
                            await dest_channel.set_permissions(player_id, overwrite=overwrite)
                            players[playername(author)].room = dest_room_name
                            save()
                            await channel.send(f"`{player.name}` has exited to the `{dest_room_name}`.")
                            await dest_channel.send(f"`{player.name}` has entered from the `{room.name}`.")
                        elif dest_room_name in locked_room_list:
                            await channel.send(f"The door to the `{dest_room_name}` is locked.")
                        else:
                            await channel.send(f"There is no room called `{dest_room_name}` which you can get to from here.")
                    except:
                        await channel.send("Incorrect command format. The correct format is: `!goto <room>`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Help Command
        # !help
        elif command[0] == "help":
            if playername(author) in players.keys():
                await channel.send(
                    "`!clothes`\n" \
                    "`!contents <object> [num]`\n" \
                    "`!desc`\n" \
                    "`!doors`\n" \
                    "`!drop <item> [num]`\n" \
                    "`!dropin <object> [num] <item> [num]`\n" \
                    "`!goto <room>`\n" \
                    "`!help`\n" \
                    "`!inv`\n" \
                    "`!items`\n" \
                    "`!lockdoor <door> <item> [num]`\n" \
                    "`!lockobject <object> [num] <item> [num]`\n" \
                    "`!lookclothes <item> [num]`\n" \
                    "`!lookin <object> [num] <item> [num]`\n" \
                    "`!lookinv <item> [num]`\n" \
                    "`!lookitem <item> [num]`\n" \
                    "`!lookobject <object> [num]`\n" \
                    "`!lookplayer <player>`\n" \
                    "`!objects`\n" \
                    "`!take <item> [num]`\n" \
                    "`!takefrom <object> [num] <item> [num]`\n" \
                    "`!takewear <item> [num]`\n" \
                    "`!time`\n" \
                    "`!undress <item> [num]`\n" \
                    "`!undressdrop <item> [num]`\n" \
                    "`!unlockdoor <door> <item> [num]`\n" \
                    "`!unlockobject <object> [num] <item> [num]`\n" \
                    "`!wear <item> [num]`"
                )
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Inv Command
        # !inv
        elif command[0] == "inv":
            if playername(author) in players.keys():
                try:
                    # Define Variables
                    player = players[playername(author)]
                    itemstring = getthingnamestring(player.items)
                    # Perform Command
                    if itemstring == "":
                        await channel.send("You are currently not holding anything.")
                    else:
                        await channel.send(f"You are currently holding these items:\n{itemstring}")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!inv`.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Items Command
        # !items
        elif command[0] == "items":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        itemstring = getthingnamestring(room.items)
                        # Perform Command
                        if itemstring == "":
                            await channel.send("There are no items here.")
                        else:
                            await channel.send(f"The following items are here:\n{itemstring}")
                    except:
                        await channel.send("Incorrect command format. The correct format is: `!items`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Lock Door Command
        # !lockdoor <door> <item> [num]
        elif command[0] == "lockdoor":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        door_name = command[1]
                        item_name = command[2]
                        item_num = 1
                        if len(command) >= 4:
                            item_num = int(command[3])
                        door = finddoor(room.doors, room.name, door_name)
                        # Run Command
                        if not door is None:
                            if door.state == "OPEN":
                                # Define Variables
                                matching_items = getmatchingitems(player.items, item_name)
                                # Run Command
                                if len(matching_items) > 0:
                                    if item_num > 0 and item_num <= len(matching_items):
                                        # Define Variables
                                        item = matching_items[item_num-1]
                                        # Run Command
                                        if item.key == door.key and item.key != "":
                                            door.state = "LOCKED"
                                            save()
                                            await channel.send(f"You have successfully locked the door to room `{door_name}`.")
                                        else:
                                            await channel.send(f"The `{item_name}` cannot be used to lock the door to room `{door_name}`.")
                                    else:
                                        await channel.send(f"You are holding `{len(matching_items)}` items called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                                else:
                                    await channel.send(f"You are not holding any items called `{item_name}`.")
                            elif door.state == "LOCKED":
                                await channel.send(f"The door leading to `{door_name}` is already locked.")
                            else:
                                await channel.send(f"There is not a door here leading to room `{door_name}`.")
                        else:
                            await channel.send(f"There is not a door here leading to room `{door_name}`.")
                    except:
                        await channel.send("Incorrect command format. The correct format is: `!lockdoor <door> <item> [num]`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Lock Object Command
        # !lockobject <object> [num] <item> [num]
        elif command[0] == "lockobject":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        object_name = command[1]
                        try:
                            object_num = int(command[2])
                            item_name = command[3]
                            item_num = 1
                            if len(command) >= 5:
                                item_num = int(command[4])
                        except:
                            object_num = 1
                            item_name = command[2]
                            item_num = 1
                            if len(command) >= 4:
                                item_num = int(command[3])
                        matching_objects = getmatchingitems(room.objects, object_name)
                        # Run Command
                        if len(matching_objects) > 0:
                            if object_num > 0 and object_num <= len(matching_objects):
                                # Define Variables
                                object = matching_objects[object_num-1]
                                matching_items = getmatchingitems(player.items, item_name)
                                # Run Command
                                if object.state == "OPEN":
                                    if len(matching_items) > 0:
                                        if item_num > 0 and item_num <= len(matching_items):
                                            # Define Variables
                                            item = matching_items[item_num-1]
                                            # Run Command
                                            if item.key == object.key and item.key != "":
                                                object.state = "LOCKED"
                                                save()
                                                await channel.send(f"You have successfully locked the`{object_name}`.")
                                            else:
                                                await channel.send(f"The `{item_name}` cannot be used to lock the `{object_name}`.")
                                        else:
                                            await channel.send(f"You are holding `{len(matching_items)}` items called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                                    else:
                                        await channel.send(f"You are not holding any items called `{item_name}`.")
                                elif object.state == "LOCKED":
                                    await channel.send(f"The object `{object_name}` is already locked.")
                                else:
                                    await channel.send(f"The `{object_name}` cannot store any items.")
                            else:
                                await channel.send(f"There are `{len(matching_objects)}` objects here called `{object_name}`, so `[num]` must be specified between `1` and `{len(matching_objects)}`.")
                        else:
                            await channel.send(f"There are no objects here called `{object_name}`.")
                    except:
                        await channel.send("Incorrect command format. The correct format is: `!lockobject <object> [num] <item> [num]`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Look Clothes Command
        # !lookclothes <item> [num]
        elif command[0] == "lookclothes":
            if playername(author) in players.keys():
                try:
                    # Define Variables
                    player = players[playername(author)]
                    item_name = command[1]
                    item_num = 1
                    if len(command) >= 3:
                        item_num = int(command[2])
                    matching_items = getmatchingitems(player.clothes, item_name)
                    # Run Command
                    if len(matching_items) > 0:
                        if item_num > 0 and item_num <= len(matching_items):
                            # Define Variables
                            item = matching_items[item_num-1]
                            # Run Command
                            await channel.send(f"Item Name: `{item.name}`\nWeight: `{item.weight}` Wearable: `{item.wearable}`\n{item.desc}")
                        else:
                            await channel.send(f"You are wearing `{len(matching_items)}` items of clothing called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                    else:
                        await channel.send(f"You are not wearing any clothes called `{command[1]}`.")
                except:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Look In Command
        # !lookin <object> [num] <item> [num]
        elif command[0] == "lookin":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        object_name = command[1]
                        try:
                            object_num = int(command[2])
                            item_name = command[3]
                            item_num = 1
                            if len(command) >= 5:
                                item_num = int(command[4])
                        except:
                            object_num = 1
                            item_name = command[2]
                            item_num = 1
                            if len(command) >= 4:
                                item_num = int(command[3])
                        matching_objects = getmatchingitems(room.objects, object_name)
                        # Run Command
                        if len(matching_objects) > 0:
                            if object_num > 0 and object_num <= len(matching_objects):
                                # Define Variables
                                object = matching_objects[object_num-1]
                                matching_items = getmatchingitems(object.items, item_name)
                                # Run Command
                                if object.state == "OPEN":
                                    if len(matching_items) > 0:
                                        if item_num > 0 and item_num <= len(matching_items):
                                            # Define Variables
                                            item = matching_items[item_num-1]
                                            # Run Command
                                            await channel.send(f"Item Name: `{item.name}`\nWeight: `{item.weight}` Wearable: `{item.wearable}`\n{item.desc}")
                                        else:
                                            await channel.send(f"There are `{len(matching_items)}` items in the `{object_name}` called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                                    else:
                                        await channel.send(f"There are no items in the `{object_name}` called `{item_name}`.")
                                elif object.state == "LOCKED":
                                    await channel.send(f"The `{object_name}` is locked.")
                                else:
                                    await channel.send(f"The `{object_name}` cannot store any items.")
                            else:
                                await channel.send(f"There are `{len(matching_objects)}` objects here called `{object_name}`, so `[num]` must be specified between `1` and `{len(matching_objects)}`.")
                        else:
                            await channel.send(f"There are no objects here called `{object_name}`.")
                    except:
                        await channel.send("Incorrect command format. The correct format is: `!lookin <object> [num] <item> [num]`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Look Inv Command
        # !lookinv <item> [num]
        elif command[0] == "lookinv":
            if playername(author) in players.keys():
                try:
                    # Define Variables
                    player = players[playername(author)]
                    item_name = command[1]
                    item_num = 1
                    if len(command) >= 3:
                        item_num = int(command[2])
                    matching_items = getmatchingitems(player.items, item_name)
                    # Run Command
                    if len(matching_items) > 0:
                        if item_num > 0 and item_num <= len(matching_items):
                            # Define Variables
                            item = matching_items[item_num-1]
                            # Run Command
                            await channel.send(f"Item Name: `{item.name}`\nWeight: `{item.weight}` Wearable: `{item.wearable}`\n{item.desc}")
                        else:
                            await channel.send(f"You are holding `{len(matching_items)}` items called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                    else:
                        await channel.send(f"You are not holding any items called `{command[1]}`.")
                except:
                    await channel.send("Invalid command format. The correct format is: `!lookinv <item> [num]`.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Look Item Command
        # !lookitem <item> [num]
        elif command[0] == "lookitem":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        item_name = command[1]
                        item_num = 1
                        if len(command) >= 3:
                            item_num = int(command[2])
                        matching_items = getmatchingitems(room.items, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                # Run Command
                                await channel.send(f"Item Name: `{item.name}`\nWeight: `{item.weight}` Wearable: `{item.wearable}`\n{item.desc}")
                            else:
                                await channel.send(f"There are `{len(matching_items)}` items here called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"There are no items here called `{command[1]}`.")
                    except:
                        await channel.send("Invalid command format. The correct format is: `!lookitem <item> [num]`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Look Object Command
        # !lookobject <object> [num]
        elif command[0] == "lookobject":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        object_name = command[1]
                        object_num = 1
                        if len(command) >= 3:
                            object_num = int(command[2])
                        matching_objects = getmatchingitems(room.objects, object_name)
                        # Run Command
                        if len(matching_objects) > 0:
                            if object_num > 0 and object_num <= len(matching_objects):
                                # Define Variables
                                object = matching_objects[object_num-1]
                                # Run Command
                                await channel.send(f"Object Name: `{object.name}`\nStorage: `{object.storage}` State: `{object.state}`\n{object.desc}")
                            else:
                                await channel.send(f"There are `{len(matching_objects)}` objects here called `{object_name}`, so `[num]` must be specified between `1` and `{len(matching_objects)}`.")
                        else:
                            await channel.send(f"There are no objects here called `{command[1]}`.")
                    except:
                        await channel.send("Invalid command format. The correct format is: `!lookobject <object> [num]`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Look Player Command
        # !lookplayer <player>
        elif command[0] == "lookplayer":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        target_player_name = command[1]
                        # Run Command
                        if target_player_name in players.keys():
                            # Define Variables
                            target_player = players[target_player_name]
                            itemstring = getthingnamestring(target_player.clothes)
                            # Run Command
                            if room.name == target_player.room:
                                if itemstring == "":
                                    await channel.send(f"`{target_player_name}` is currently not wearing any clothes. :thinking:")
                                else:
                                    await channel.send(f"`{target_player_name}` is currently wearing these clothes:\n{itemstring}")
                            else:
                                await channel.send(f"There are no players here called `{target_player_name}`.")
                        else:
                            await channel.send(f"There are no players here called `{target_player_name}`.")
                    except:
                        await channel.send("Invalid command format. The correct format is: `!lookplayer <player>`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Objects Command
        # !objects
        elif command[0] == "objects":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        objectstring = getthingnamestring(room.objects)
                        # Perform Command
                        if objectstring == "":
                            await channel.send("There are no objects here.")
                        else:
                            await channel.send(f"The following objects are here:\n{objectstring}")
                    except:
                        await channel.send("Incorrect command format. The correct format is: `!objects`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Take Command
        # !take <item> [num]
        elif command[0] == "take":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        item_name = command[1]
                        item_num = 1
                        if len(command) >= 3:
                            item_num = int(command[2])
                        matching_items = getmatchingitems(room.items, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                weight = gettotalweight(player.items)
                                # Run Command
                                if weight + item.weight <= carrylimit:
                                    player.items.append(item)
                                    room.items.remove(item)
                                    save()
                                    await channel.send(f"You are now holding the `{item_name}`.")
                                else:
                                    await channel.send(f"You cannot take the `{item_name}` because you would be holding too much.")
                            else:
                                await channel.send(f"There are `{len(matching_items)}` items here called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"There are no items here called `{matching_items}`.")
                    except:
                        await channel.send("Incorrect command format. The correct format is: `!take <item> [num]`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Take From Command
        # !takefrom <object> [num] <item> [num]
        elif command[0] == "takefrom":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        object_name = command[1]
                        try:
                            object_num = int(command[2])
                            item_name = command[3]
                            item_num = 1
                            if len(command) >= 5:
                                item_num = int(command[4])
                        except:
                            object_num = 1
                            item_name = command[2]
                            item_num = 1
                            if len(command) >= 4:
                                item_num = int(command[3])
                        matching_objects = getmatchingitems(room.objects, object_name)
                        # Run Command
                        if len(matching_objects) > 0:
                            if object_num > 0 and object_num <= len(matching_objects):
                                # Define Variables
                                object = matching_objects[object_num-1]
                                matching_items = getmatchingitems(object.items, item_name)
                                # Run Command
                                if object.state == "OPEN":
                                    if len(matching_items) > 0:
                                        if item_num > 0 and item_num <= len(matching_items):
                                            # Define Variables
                                            item = matching_items[item_num-1]
                                            weight = gettotalweight(player.items)
                                            # Run Command
                                            if (weight + item.weight) <= carrylimit:
                                                player.items.append(item)
                                                object.items.remove(item)
                                                save()
                                                await channel.send(f"You have taken the `{item_name}` from the `{object.name}`.")
                                            else:
                                                await channel.send(f"You cannot take the `{item.name}` from the `{object.name}` because you would be carrying too much.")
                                        else:
                                            await channel.send(f"There are `{len(matching_items)}` items in the `{object_name}` called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                                    else:
                                        await channel.send(f"There are no items in the `{object_name}` called `{item_name}`.")
                                elif object.state == "LOCKED":
                                    await channel.senf(f"The `{object_name}` is locked.")
                                else:
                                    await channel.send(f"The `{object_name}` cannot store any items.")
                            else:
                                await channel.send(f"There are `{len(matching_objects)}` objects here called `{object_name}`, so `[num]` must be specified between `1` and `{len(matching_objects)}`.")
                        else:
                            await channel.send(f"There are no objects here called `{object_name}`.")
                    except:
                        await channel.send("Incorrect command format. The correct format is: `!takefrom <object> [num] <item> [num]`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Take Wear Command
        # !takewear <item> [num]
        elif command[0] == "takewear":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        item_name = command[1]
                        item_num = 1
                        if len(command) >= 3:
                            item_num = int(command[2])
                        matching_items = getmatchingitems(room.items, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                weight = gettotalweight(player.clothes)
                                # Run Command
                                if item.wearable:
                                    if weight + item.weight <= wearlimit:
                                        player.clothes.append(item)
                                        room.items.remove(item)
                                        save()
                                        await channel.send(f"You are now wearing the `{item_name}`.")
                                    else:
                                        await channel.send(f"You cannot wear the `{item_name}` because you would be wearing too much.")
                                else:
                                    await channel.send(f"The `{item_name}` is not wearable.")
                            else:
                                await channel.send(f"There are `{len(matching_items)}` items here called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"There are no items here called `{matching_items}`.")
                    except:
                        await channel.send("Incorrect command format. The correct format is: `!takewear <item> [num]`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Time Command
        # !time
        elif command[0] == "time":
            if playername(author) in players.keys():
                now = datetime.now() - timedelta(hours=2)
                current_time = now.strftime("%H:%M")
                await channel.send(f"The current time is `{current_time}`.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Undress Command
        # !undress <item> [num]
        elif command[0] == "undress":
            if playername(author) in players.keys():
                try:
                    # Define Variables
                    player = players[playername(author)]
                    item_name = command[1]
                    item_num = 1
                    if len(command) >= 3:
                        item_num = int(command[2])
                    matching_items = getmatchingitems(player.clothes, item_name)
                    # Run Command
                    if len(matching_items) > 0:
                        if item_num > 0 and item_num <= len(matching_items):
                            # Define Variables
                            item = matching_items[item_num-1]
                            weight = gettotalweight(player.items)
                            # Run Command
                            if (weight + item.weight) <= carrylimit:
                                player.items.append(item)
                                player.clothes.remove(item)
                                save()
                                await channel.send(f"You have taken off the `{item_name}`.")
                            else:
                                await channel.send(f"You cannot take off the `{item_name}` because you would be holding too much.")
                        else:
                            await channel.send(f"You are wearing `{len(matching_items)}` items of clothing called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                    else:
                        await channel.send(f"You are not wearing any items of clothing called `{item_name}`.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!undress <item> [num]`.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Undress Drop Command
        # !undressdrop <item> [num]
        elif command[0] == "undressdrop":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        item_name = command[1]
                        item_num = 1
                        if len(command) >= 3:
                            item_num = int(command[2])
                        matching_items = getmatchingitems(player.clothes, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                # Run Command
                                room.items.append(item)
                                player.clothes.remove(item)
                                save()
                                await channel.send(f"You have taken off and dropped the `{item_name}`.")
                            else:
                                await channel.send(f"You are wearing `{len(matching_items)}` items of clothing called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"You are not wearing any items of clothing called `{item_name}`.")
                    except:
                        await channel.send("Incorrect command format. The correct format is: `!undressdrop <item> [num]`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Unlock Door Command
        # !unlockdoor <door> <item> [num]
        elif command[0] == "unlockdoor":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        door_name = command[1]
                        item_name = command[2]
                        item_num = 1
                        if len(command) >= 4:
                            item_num = int(command[3])
                        door = finddoor(room.doors, room.name, door_name)
                        # Run Command
                        if not door is None:
                            if door.state == "LOCKED":
                                # Define Variables
                                matching_items = getmatchingitems(player.items, item_name)
                                # Run Command
                                if len(matching_items) > 0:
                                    if item_num > 0 and item_num <= len(matching_items):
                                        # Define Variables
                                        item = matching_items[item_num-1]
                                        # Run Command
                                        if item.key == door.key and item.key != "":
                                            door.state = "OPEN"
                                            save()
                                            await channel.send(f"You have successfully unlocked the door to room `{door_name}`.")
                                        else:
                                            await channel.send(f"The `{item_name}` cannot be used to unlock the door to room `{door_name}`.")
                                    else:
                                        await channel.send(f"You are holding `{len(matching_items)}` items called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                                else:
                                    await channel.send(f"You are not holding any items called `{command[1]}`.")
                            elif door.state == "OPEN":
                                await channel.send(f"The door leading to `{door_name}` is already open.")
                            else:
                                await channel.send(f"There is not a door here leading to room `{door_name}`.")
                        else:
                            await channel.send(f"There is not a door here leading to room `{door_name}`.")
                    except:
                        await channel.send("Incorrect command format. The correct format is: `!unlockdoor <door> <item> [num]`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Unlock Object Command
        # !unlockobject <object> [num] <item> [num]
        elif command[0] == "unlockobject":
            if playername(author) in players.keys():
                # Define Variables
                player = players[playername(author)]
                # Run Command
                if player.room in rooms.keys():
                    try:
                        # Define Variables
                        room = rooms[player.room]
                        object_name = command[1]
                        try:
                            object_num = int(command[2])
                            item_name = command[3]
                            item_num = 1
                            if len(command) >= 5:
                                item_num = int(command[4])
                        except:
                            object_num = 1
                            item_name = command[2]
                            item_num = 1
                            if len(command) >= 4:
                                item_num = int(command[3])
                        matching_objects = getmatchingitems(room.objects, object_name)
                        # Run Command
                        if len(matching_objects) > 0:
                            if object_num > 0 and object_num <= len(matching_objects):
                                # Define Variables
                                object = matching_objects[object_num-1]
                                matching_items = getmatchingitems(player.items, item_name)
                                # Run Command
                                if object.state == "LOCKED":
                                    if len(matching_items) > 0:
                                        if item_num > 0 and item_num <= len(matching_items):
                                            # Define Variables
                                            item = matching_items[item_num-1]
                                            # Run Command
                                            if item.key == object.key and item.key != "":
                                                object.state = "OPEN"
                                                save()
                                                await channel.send(f"You have successfully unlocked the`{object_name}`.")
                                            else:
                                                await channel.send(f"The `{item_name}` cannot be used to unlock the `{object_name}`.")
                                        else:
                                            await channel.send(f"You are holding `{len(matching_items)}` items called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                                    else:
                                        await channel.send(f"You are not holding any items called `{item_name}`.")
                                elif object.state == "OPEN":
                                    await channel.send(f"The objcet `{object_name}` is already open.")
                                else:
                                    await channel.send(f"The `{object_name}` cannot store any items.")
                            else:
                                await channel.send(f"There are `{len(matching_objects)}` objects here called `{object_name}`, so `[num]` must be specified between `1` and `{len(matching_objects)}`.")
                        else:
                            await channel.send(f"There are no objects here called `{object_name}`.")
                    except:
                        await channel.send("Incorrect command format. The correct format is: `!unlockobject <object> [num] <item> [num]`.")
                else:
                    await channel.send("You are not in a valid room. Please contact a host if you believe this is a mistake.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        # Wear Command
        # !wear <item> [num]
        elif command[0] == "wear":
            if playername(author) in players.keys():
                try:
                    # Define Variables
                    player = players[playername(author)]
                    item_name = command[1]
                    item_num = 1
                    if len(command) >= 3:
                        item_num = int(command[2])
                    matching_items = getmatchingitems(player.items, item_name)
                    # Run Command
                    if len(matching_items) > 0:
                        if item_num > 0 and item_num <= len(matching_items):
                            # Define Variables
                            item = matching_items[item_num-1]
                            weight = gettotalweight(player.items)
                            # Run Command
                            if item.wearable:
                                if (weight + item.weight) <= wearlimit:
                                    player.clothes.append(item)
                                    player.items.remove(item)
                                    save()
                                    await channel.send(f"You are now wearing the `{item_name}`.")
                                else:
                                    await channel.send(f"You cannot wear the `{item_name}` because you would be wearing too much.")
                            else:
                                await channel.send(f"The `{item_name}` is not wearable.")
                        else:
                            await channel.send(f"You are holding `{len(matching_items)}` items called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                    else:
                        await channel.send(f"You are not holding any items called `{item_name}`.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!wear <item> [num]`.")
            else:
                await channel.send("You are not a valid player. Please contact a host if you believe this is a mistake.")

        #########################
        #    ADMIN COMMANDS     #
        #########################

        # Add Door Command
        # !adddoor <room1> <room2> [state]
        elif command[0] == "adddoor":
            if admin:
                try:
                    # Define Variables
                    room1_name = command[1]
                    room2_name = command[2]
                    state = "OPEN"
                    if len(command) >= 4:
                        state = command[3].upper()
                    # Run Command
                    if state in ["OPEN", "LOCKED", "HIDDEN"]:
                        if room1_name in rooms.keys():
                            if room2_name in rooms.keys():
                                if room1_name != room2_name:
                                    # Define Variables
                                    room1 = rooms[room1_name]
                                    room2 = rooms[room2_name]
                                    if finddoor(room1.doors, room1_name, room2_name) is None:
                                        door = Door(room1=room1_name, room2=room2_name, state=state)
                                        room1.doors.append(door)
                                        room2.doors.append(door)
                                        save()
                                        await channel.send(f"Door between `{room1_name}` and `{room2_name}` with state `{state}` added successfully.")
                                    else:
                                        await channel.send(f"There is already a door between rooms `{room1_name}` and `{room2_name}`.")
                                else:
                                    await channel.send("Invalid paramater. `<room2>` cannot be the same as `<room1>`.")
                            else:
                                await channel.send("Invalid parameter. `<room2>` must be the name of a room.")
                        else:
                            await channel.send("Invalid parameter. `<room1>` must be the name of a room.")
                    else:
                        await channel.send("Invalid parameter. `<state>` must be either `open`, `locked` or `hidden`.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!adddoor <room1> <room2> [state]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Add Object Item Command
        # !addobjectitem <room> <object> [num] <item> <weight> <wearable> [desc]
        elif command[0] == "addobjectitem":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    object_name = command[2]
                    try:
                        object_num = int(command[3])
                        item_name = command[4]
                        item_weight = float(command[5])
                        item_wearable = False
                        if command[6] in ["true", "false"]:
                            if command[6] == "true":
                                item_wearable = True
                        else:
                            await channel.send("Invalid parameter. `<wearable>` must be either `true` or `false`. Defaulting to `false`.")
                        description = ""
                        if len(command) >= 8:
                            description = " ".join(command[7:])
                    except:
                        object_num = 1
                        item_name = command[3]
                        item_weight = float(command[4])
                        item_wearable = False
                        if command[5] in ["true", "false"]:
                            if command[5] == "true":
                                item_wearable = True
                        else:
                            await channel.send("Invalid parameter. `<wearable>` must be either `true` or `false`. Defaulting to `false`.")
                        description = ""
                        if len(command) >= 7:
                            description = " ".join(command[6:])
                    # Run Command
                    if room_name in rooms.keys():
                        # Define Variables
                        room = rooms[room_name]
                        matching_objects = getmatchingitems(room.objects, object_name)
                        # Run Command
                        if len(matching_objects) > 0:
                            if object_num > 0 and object_num <= len(matching_objects):
                                # Define Variables
                                object = matching_objects[object_num-1]
                                # Run Command
                                item = Item(name=item_name, weight=item_weight, wearable=item_wearable, desc=description)
                                object.items.append(item)
                                save()
                                await channel.send(f"Item `{item_name}` added to object `{object_name}` successfully.")
                            else:
                                await channel.send(f"There are `{len(matching_objects)}` objects in room `{room_name}` called `{object_name}`, so `[num]` must be specified between `1` and `{len(matching_objects)}`.")
                        else:
                            await channel.send(f"There are no objects in room `{room_name}` called `{object_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!addobjectitem <room> <object> [num] <item> <weight> <wearable> [desc]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Add Player Command
        # !addplayer <name> <id>
        elif command[0] == "addplayer":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    player_id = int(command[2])
                    # Run Command
                    if not player_name in players.keys():
                        players[player_name] = Player(id=player_id, name=player_name, room="", items=[], clothes=[])
                        save()
                        await channel.send(f"Player `{player_name}` added successfully.")
                    else:
                        await channel.send(f"There is already a player called `{player_name}`.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!addplayer <name> <id>`.")
            else:
               await channel.send("You do not have permission to perform this command.")

        # Add Player Clothes Command
        # !addplayerclothes <player> <item> <weight> <wearable> [desc]
        elif command[0] == "addplayerclothes":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    item_name = command[2]
                    item_weight = float(command[3])
                    item_wearable = True
                    if command[4] in ["true", "false"]:
                        if command[4] == "false":
                            item_wearable = False
                    else:
                        await channel.send("Invalid parameter. `<wearable>` must be either `true` or `false`. Defaulting to `true`.")
                    description = ""
                    if len(command) >= 6:
                        description = " ".join(command[5:])
                    # Run Command
                    if player_name in players.keys():
                        # Define Variables
                        player = players[player_name]
                        # Run Command
                        item = Item(name=item_name, weight=item_weight, wearable=item_wearable, desc=description)
                        player.clothes.append(item)
                        save()
                        await channel.send(f"Item `{item_name}` added to `{player_name}`'s clothes successfully.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!addplayerclothes <player> <item> <weight> <wearable> [desc]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Add Player Item Command
        # !addplayeritem <player> <item> <weight> <wearable> [desc]
        elif command[0] == "addplayeritem":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    item_name = command[2]
                    item_weight = float(command[3])
                    item_wearable = False
                    if command[4] in ["true", "false"]:
                        if command[4] == "true":
                            item_wearable = True
                    else:
                        await channel.send("Invalid parameter. `<wearable>` must be either `true` or `false`. Defaulting to `false`.")
                    description = ""
                    if len(command) >= 6:
                        description = " ".join(command[5:])
                    # Run Command
                    if player_name in players.keys():
                        # Define Variables
                        player = players[player_name]
                        # Run Command
                        item = Item(name=item_name, weight=item_weight, wearable=item_wearable, desc=description)
                        player.items.append(item)
                        save()
                        await channel.send(f"Item `{item_name}` added to `{player_name}`'s items successfully.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!addplayeritem <player> <item> <weight> <wearable> [desc]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Add Room Command
        # !addroom <name> <id>
        elif command[0] == "addroom":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    room_id = int(command[2])
                    # Run Command
                    if not room_name in rooms.keys():
                        rooms[room_name] = Room(id=room_id, name=room_name, items=[], objects=[], doors=[])
                        save()
                        await channel.send(f"Room `{room_name}` added successfully.")
                    else:
                        await channel.send(f"There is already a room called `{room_name}`.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!addroom <name> <id>`.")
            else:
               await channel.send("You do not have permission to perform this command.")

        # Add Room Item Command
        # !addroomitem <room> <item> <weight> <wearable> [desc]
        elif command[0] == "addroomitem":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    item_name = command[2]
                    item_weight = float(command[3])
                    item_wearable = False
                    if command[4] in ["true", "false"]:
                        if command[4] == "true":
                            item_wearable = True
                    else:
                        await channel.send("Invalid parameter. `<wearable>` must be either `true` or `false`. Defaulting to `false`.")
                    description = ""
                    if len(command) >= 6:
                        description = " ".join(command[5:])
                    # Run Command
                    if room_name in rooms.keys():
                        # Define Variables
                        room = rooms[room_name]
                        # Run Command
                        item = Item(name=item_name, weight=item_weight, wearable=item_wearable, desc=description)
                        room.items.append(item)
                        save()
                        await channel.send(f"Item `{item_name}` added to room `{room_name}` successfully.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!addroomitem <room> <item> <weight> <wearable> [desc]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Add Room Object Command
        # !addroomobject <room> <object> <storage> <state> [desc]
        elif command[0] == "addroomobject":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    object_name = command[2]
                    object_storage = int(command[3])
                    object_state = command[4].upper()
                    description = ""
                    if len(command) >= 6:
                        description = " ".join(command[5:])
                    # Run Command
                    if room_name in rooms.keys():
                        if object_state in ["OPEN", "LOCKED", "NONE"]:
                            # Define Variables
                            room = rooms[room_name]
                            # Run Command
                            object = RoomObject(name=object_name, storage=object_storage, state=object_state, desc=description, items=[])
                            room.objects.append(object)
                            save()
                            await channel.send(f"Object `{object_name}` added to room `{room_name}` successfully.")
                        else:
                            await channel.send("Invalid paramter. `<state>` must be either `open`, `locked` or `none`.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!addroomobject <room> <object> <storage> <state> [desc]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Admin Help Command
        # !adminhelp
        elif command[0] == "adminhelp":
            if admin:
                await channel.send(
                    "`!adddoor <room1> <room2> [state]`\n" \
                    "`!addobjectitem <room> <object> [num] <item> <weight> <wearable> [desc]`\n" \
                    "`!addplayer <name> <id>`\n" \
                    "`!addplayerclothes <player> <item> <weight> <wearable> [desc]`\n" \
                    "`!addplayeritem <player> <item> <weight> <wearable> [desc]`\n" \
                    "`!addroom <name> <id>`\n" \
                    "`!addroomitem <room> <item> <weight> <wearable> [desc]`\n" \
                    "`!addroomobject <room> <object> <storage> <state> [desc]`\n" \
                    "`!adminhelp`\n" \
                    "`!deldoor <room1> <room2>`\n" \
                    "`!delobjectitem <room> <object> [num] <item> [num]`\n" \
                    "`!delplayer <player>`\n" \
                    "`!delplayerclothes <player> <item> [num]`\n" \
                    "`!delplayeritem <player> <item> [num]`\n" \
                    "`!delroom <room>`\n" \
                    "`!delroomitem <room> <item> [num]`\n" \
                    "`!delroomobject <room> <object> [num]`\n" \
                    "`!drag <player> <room>`\n" \
                    "`!dragall <room>`\n" \
                    "`!editdoor <room1> <room2> <attribute> <value>`\n" \
                    "`!editobjectitem <room> <object> [num] <item> [num] <attribute> <value>`\n" \
                    "`!editplayerclothes <player> <item> [num] <attribute> <value>`\n" \
                    "`!editplayeritem <player> <item> [num] <attribute> <value>`\n" \
                    "`!editplayername <player> <name>`\n" \
                    "`!editroom <room> <attribute> <value>`\n" \
                    "`!editroomitem <room> <item> [num] <attribute> <value>`\n" \
                    "`!editroomobject <room> <object> [num] <attribute> <value>`\n" \
                    "`!forcedrop <player> <item> [num]`\n" \
                    "`!forcetake <player> <item> [num]`\n" \
                    "`!forcetakewear <player> <item> [num]`\n" \
                    "`!forceundress <player> <item> [num]`\n" \
                    "`!forceundressdrop <player> <item> [num]`\n" \
                    "`!forcewear <player> <item> [num]`\n" \
                    "`!listobjectitems <room> <object> [num]`\n" \
                    "`!listplayerclothes <player>`\n" \
                    "`!listplayeritems <player>`\n" \
                    "`!listplayers`\n" \
                    "`!listroomdoors <room> [state]`\n" \
                    "`!listroomitems <room>`\n" \
                    "`!listroomobjects <room>`\n" \
                    "`!listrooms`\n" \
                    "`!seeobjectitem <room> <object> [num] <item> [num]`\n" \
                    "`!seeplayerclothes <player> <item> [num]`\n" \
                    "`!seeplayeritem <player> <item> [num]`\n" \
                    "`!seedoor <room1> <room2>`\n" \
                    "`!seeroomitem <room> <item> [num]`\n" \
                    "`!seeroomobject <room> <object> [num]`"
                )
            else:
                await channel.send("You do not have permission to perform this command.")

        # Delete Door Command
        # !deldoor <room1> <room2>
        elif command[0] == "deldoor":
            if admin:
                try:
                    # Define Variables
                    room1_name = command[1]
                    room2_name = command[2]
                    # Run Command
                    if room1_name in rooms.keys():
                        if room2_name in rooms.keys():
                            try:
                                # Define Variables
                                room1 = rooms[room1_name]
                                room2 = rooms[room2_name]
                                door = finddoor(room1.doors, room1_name, room2_name)
                                # Run Command
                                room1.doors.remove(door)
                                room2.doors.remove(door)
                                save()
                                await channel.send(f"The door between `{room1_name}` and `{room2_name}` has been removed.")
                            except:
                                await channel.send(f"There is no door between `{room1_name}` and `{room2_name}`.")
                        else:
                            await channel.send("Invalid parameter. `<room2>` must be the name of a room.")
                    else:
                        await channel.send("Invalid parameter. `<room1>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!deldoor <room1> <room2>`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Delete Object Item Command
        # !delobjectitem <room> <object> [num] <item> [num]
        elif command[0] == "delobjectitem":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    object_name = command[2]
                    try:
                        object_num = int(command[3])
                        item_name = command[4]
                        item_num = 1
                        if len(command) >= 6:
                            item_num = int(command[5])
                    except:
                        object_num = 1
                        item_name = command[3]
                        item_num = 1
                        if len(command) >= 5:
                            item_num = int(command[4])
                    # Run Command
                    if room_name in rooms.keys():
                        # Define Variables
                        room = rooms[room_name]
                        matching_objects = getmatchingitems(room.objects, object_name)
                        # Run Command
                        if len(matching_objects) > 0:
                            if object_num > 0 and object_num <= len(matching_objects):
                                # Define Variables
                                object = matching_objects[object_num-1]
                                matching_items = getmatchingitems(object.items, item_name)
                                # Run Command
                                if len(matching_items) > 0:
                                    if item_num > 0 and item_num <= len(matching_items):
                                        # Define Variables
                                        item = matching_items[item_num-1]
                                        # Run Command
                                        object.items.remove(item)
                                        save()
                                        await channel.send(f"Successfully deleted the `{item_name}` from the `{object_name}`.")
                                    else:
                                        await channel.send(f"There are `{len(matching_items)}` items in the `{object_name}` called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                                else:
                                    await channel.send(f"There are no items in the `{object_name}` called `{item_name}`.")
                            else:
                                await channel.send(f"There are `{len(matching_objects)}` objects in room `{room_name}` called `{object_name}`, so `[num]` must be specified between `1` and `{len(matching_objects)}`.")
                        else:
                            await channel.send(f"There are no objects in room `{room_name}` called `{object_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!delobjectitem <room> <object> [num] <item> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Delete Player Command
        # !delplayer <player>
        elif command[0] == "delplayer":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    # Run Command
                    if player_name in players.keys():
                        players.pop(player_name)
                        save()
                        await channel.send(f"Player `{player_name}` removed successfully.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!delplayer <player>`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Delete Player Clothes Command
        # !delplayerclothes <player> <item> [num]
        elif command[0] == "delplayerclothes":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    item_name = command[2]
                    item_num = 1
                    if len(command) >= 4:
                        item_num = int(command[3])
                    # Run Command
                    if player_name in players.keys():
                        # Define Variables
                        player = players[player_name]
                        matching_items = getmatchingitems(player.clothes, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                # Run Command
                                player.clothes.remove(item)
                                save()
                                await channel.send(f"Item `{item_name}` removed from `{player_name}`'s clothes successfully.")
                            else:
                                await channel.send(f"`{player_name}` is wearing `{len(matching_items)}` items of clothing called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"`{player_name}` is not wearing any items of clothing called `{item_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!delplayerclothes <player> <item> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Delete Player Item Command
        # !delplayeritem <player> <item> [num]
        elif command[0] == "delplayeritem":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    item_name = command[2]
                    item_num = 1
                    if len(command) >= 4:
                        item_num = int(command[3])
                    # Run Command
                    if player_name in players.keys():
                        # Define Variables
                        player = players[player_name]
                        matching_items = getmatchingitems(player.items, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                # Run Command
                                player.items.remove(item)
                                save()
                                await channel.send(f"Item `{item_name}` removed from `{player_name}`'s items successfully.")
                            else:
                                await channel.send(f"`{player_name}` is holding `{len(matching_items)}` items called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"`{player_name}` is not holding any items called `{item_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!delplayeritem <player> <item> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Delete Room Command
        # !delroom <room>
        elif command[0] == "delroom":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    # Run Command
                    if room_name in rooms.keys():
                        # Define Variables
                        room = rooms[room_name]
                        # Run Command
                        for door in room.doors:
                            other_room = door.room1
                            if door.room1 == room_name:
                                other_room = door.room2
                            rooms[other_room].doors.remove(door)
                        rooms.pop(room_name)
                        save()
                        await channel.send(f"Room `{room_name}` removed successfully.\nPlease note that deleting rooms can cause issues if players are still in the deleted room.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!delroom <room>`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Delete Room Item Command
        # !delroomitem <room> <item> [num]
        elif command[0] == "delroomitem":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    item_name = command[2]
                    item_num = 1
                    if len(command) >= 4:
                        item_num = int(command[3])
                    # Run Command
                    if room_name in rooms.keys():
                        # Define Variables
                        room = rooms[room_name]
                        matching_items = getmatchingitems(room.items, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                # Run Command
                                room.items.remove(item)
                                save()
                                await channel.send(f"Item `{item_name}` removed from room `{room_name}` successfully.")
                            else:
                                await channel.send(f"There are `{len(matching_items)}` items in room `{room_name}` called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"There are no items in room `{room_name}` called `{item_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!delroomitem <room> <item> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Delete Room Object Command
        # !delroomobject <room> <object> [num]
        elif command[0] == "delroomobject":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    object_name = command[2]
                    object_num = 1
                    if len(command) >= 4:
                        object_num = int(command[3])
                    # Run Command
                    if room_name in rooms.keys():
                        # Define Variables
                        room = rooms[room_name]
                        matching_objects = getmatchingitems(room.objects, object_name)
                        # Run Command
                        if len(matching_objects) > 0:
                            if object_num > 0 and object_num <= len(matching_objects):
                                # Define Variables
                                object = matching_objects[object_num-1]
                                # Run Command
                                room.objects.remove(object)
                                save()
                                await channel.send(f"Object `{object_name}` removed from room `{room_name}` successfully.")
                            else:
                                await channel.send(f"There are `{len(matching_objects)}` objects in room `{room_name}` called `{object_name}`, so `[num]` must be specified between `1` and `{len(matching_objects)}`.")
                        else:
                            await channel.send(f"There are no objects in room `{room_name}` called `{object_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!delroomobject <room> <object> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Drag Command
        # !drag <player> <room>
        elif command[0] == "drag":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    room_name = command[2]
                    # Run Command
                    if player_name in players.keys():
                        if room_name in rooms.keys():
                            # Define Variables
                            player = players[player_name]
                            dest_room = rooms[room_name]
                            player_id = client.get_user(id=player.id)
                            dest_channel = client.get_channel(id=dest_room.id)
                            current_room_name = player.room
                            overwrite = discord.PermissionOverwrite()
                            # Run Command
                            overwrite.read_messages = None
                            if current_room_name in rooms.keys():
                                current_room = rooms[current_room_name]
                                current_channel = client.get_channel(id=current_room.id)
                                await current_channel.set_permissions(player_id, overwrite=overwrite)
                            overwrite.read_messages = True
                            await dest_channel.set_permissions(player_id, overwrite=overwrite)
                            player.room = dest_room.name
                            save()
                            await message.channel.send(f"Dragged `{player_name}` to `{room_name}` successfully.")
                        else:
                            await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!drag <player> <room>`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Drag All Command
        # !dragall <room>
        elif command[0] == "dragall":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    # Run Command
                    if room_name in rooms.keys():
                        for player_name in players.keys():
                            # Define Variables
                            player = players[player_name]
                            dest_room = rooms[room_name]
                            player_id = client.get_user(id=player.id)
                            dest_channel = client.get_channel(id=dest_room.id)
                            current_room_name = player.room
                            overwrite = discord.PermissionOverwrite()
                            # Run Command
                            overwrite.read_messages = None
                            if current_room_name in rooms.keys():
                                current_room = rooms[current_room_name]
                                current_channel = client.get_channel(id=current_room.id)
                                await current_channel.set_permissions(player_id, overwrite=overwrite)
                            overwrite.read_messages = True
                            await dest_channel.set_permissions(player_id, overwrite=overwrite)
                            player.room = dest_room.name
                            save()
                        await message.channel.send(f"Dragged everyone to `{room_name}` successfully.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!dragall <room>`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Edit Door Command
        # !editdoor <room1> <room2> <attribute> <value>
        elif command[0] == "editdoor":
            if admin:
                try:
                    # Define Variables
                    room1_name = command[1]
                    room2_name = command[2]
                    attribute = command[3]
                    value = command[4]
                    # Run Command
                    if room1_name in rooms.keys():
                        if room2_name in rooms.keys():
                            try:
                                # Define Variables
                                room1 = rooms[room1_name]
                                door = finddoor(room1.doors, room1_name, room2_name)
                                if attribute == "state":
                                    if value in ["open", "locked", "hidden"]:
                                        # Run Command
                                        door.state = value.upper()
                                        save()
                                        await channel.send(f"The state of the door between `{room1_name}` and `{room2_name}` has been changed to `{value.upper()}`.")
                                    else:
                                        await channel.send(f"When `<attribute>` is `state`, `<value>` must be `open`, `locked` or `hidden`.")
                                elif attribute == "key":
                                    if value == "none":
                                        door.key = ""
                                        save()
                                        await channel.send(f"Key for door between rooms `{room1_name}` and `{room2_name}` removed successfully.")
                                    else:
                                        door.key = value
                                        save()
                                        await channel.send(f"Key for door between rooms `{room1_name}` and `{room2_name}` changed to `{value}` successfully.")
                                else:
                                    await channel.send("Invalid parameter. `<attribute>` must be either `state` or `key`.")
                            except:
                                await channel.send(f"There is no door between `{room1_name}` and `{room2_name}`.")
                        else:
                            await channel.send("Invalid parameter. `<room2>` must be the name of a room.")
                    else:
                        await channel.send("Invalid parameter. `<room1>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!editdoor <room1> <room2> <attribute> <value>`.")
            else:
                await channel.send("Incorrect command format. The correct format is: `!editdoor <room1> <room2> <state>`.")

        # Edit Object Item Command
        # !editobjectitem <room> <object> [num] <item> [num] <attribute> <value>
        elif command[0] == "editobjectitem":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    object_name = command[2]
                    try:
                        object_num = int(command[3])
                        item_name = command[4]
                        try:
                            item_num = int(command[5])
                            attribute = command[6]
                            value_list = command[7:]
                        except:
                            item_num = 1
                            attribute = command[5]
                            value_list = command[6:]
                    except:
                        object_num = 1
                        item_name = command[3]
                        try:
                            item_num = int(command[4])
                            attribute = command[5]
                            value_list = command[6:]
                        except:
                            item_num = 1
                            attribute = command[4]
                            value_list = command[5:]
                    # Run Command
                    if room_name in rooms.keys():
                        # Define Variables
                        room = rooms[room_name]
                        matching_objects = getmatchingitems(room.objects, object_name)
                        # Run Command
                        if len(matching_objects) > 0:
                            if object_num > 0 and object_num <= len(matching_objects):
                                # Define Variables
                                object = matching_objects[object_num-1]
                                matching_items = getmatchingitems(object.items, item_name)
                                # Run Command
                                if len(matching_items) > 0:
                                    if item_num > 0 and item_num <= len(matching_items):
                                        # Define Variables
                                        item = matching_items[item_num-1]
                                        # Run Command
                                        if attribute == "name":
                                            item.name = value_list[0]
                                            save()
                                            await channel.send(f"Item `{item_name}`'s name successfully changed to `{value_list[0]}`")
                                        elif attribute == "weight":
                                            try:
                                                value = float(value_list[0])
                                                item.weight = value
                                                save()
                                                await channel.send(f"Item `{item_name}`'s weight successfully changed to `{value_list[0]}`")
                                            except:
                                                await channel.send("Invalid parameter. When `<attribute>` is `weight`, `<value>` must be a number.")
                                        elif attribute == "wearable":
                                            value = value_list[0]
                                            if value in ["true", "false"]:
                                                wearable = True
                                                if value == "false":
                                                    wearable = False
                                                item.wearable = wearable
                                                save()
                                                await channel.send(f"Item `{item_name}`'s wearble value successfully changed to `{value_list[0]}`")
                                            else:
                                                await channel.send("Invalid parameter. When `<attribute>` is `wearable`, `<value>` must be `true` or `false`.")
                                        elif attribute == "desc":
                                            description = " ".join(value_list)
                                            item.desc = description
                                            save()
                                            await channel.send(f"Item `{item_name}`'s description successfully changed to:\n{description}")
                                        elif attribute == "key":
                                            if value_list[0] == "none":
                                                item.key = ""
                                                save()
                                                await channel.send(f"Item `{item_name}`'s key value removed successfully.")
                                            else:
                                                item.key = value_list[0]
                                                save()
                                                await channel.send(f"Item `{item_name}`'s key value successfully changed to `{value_list[0]}`.")
                                        else:
                                            await channel.send("Invalid parameter. `<attribute>` must be either `name`, `weight`, `wearable`, `desc` or `key`.")
                                    else:
                                        await channel.send(f"There are `{len(matching_items)}` items in the `{object_name}` called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                                else:
                                    await channel.send(f"There are no items in the `{object_name}` called `{item_name}`.")
                            else:
                                await channel.send(f"There are `{len(matching_objects)}` objects in room `{room_name}` called `{object_name}`, so `[num]` must be specified between `1` and `{len(matching_objects)}`.")
                        else:
                            await channel.send(f"There are no objects in room `{room_name}` called `{object_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!editobjectitem <room> <object> [num] <item> [num] <attribute> <value>`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Edit Player Clothes Command
        # !editplayerclothes <player> <item> [num] <attribute> <value>
        elif command[0] == "editplayerclothes":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    item_name = command[2]
                    try:
                        item_num = int(command[3])
                        attribute = command[4]
                        value_list = command[5:]
                    except:
                        item_num = 1
                        attribute = command[3]
                        value_list = command[4:]
                    # Run Command
                    if player_name in players.keys():
                        # Define Variables
                        player = players[player_name]
                        matching_items = getmatchingitems(player.clothes, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                # Run Command
                                if attribute == "name":
                                    item.name = value_list[0]
                                    save()
                                    await channel.send(f"Item `{item_name}`'s name successfully changed to `{value_list[0]}`")
                                elif attribute == "weight":
                                    try:
                                        value = float(value_list[0])
                                        item.weight = value
                                        save()
                                        await channel.send(f"Item `{item_name}`'s weight successfully changed to `{value_list[0]}`")
                                    except:
                                        await channel.send("Invalid parameter. When `<attribute>` is `weight`, `<value>` must be a number.")
                                elif attribute == "wearable":
                                    value = value_list[0]
                                    if value in ["true", "false"]:
                                        wearable = True
                                        if value == "false":
                                            wearable = False
                                        item.wearable = wearable
                                        save()
                                        await channel.send(f"Item `{item_name}`'s wearble value successfully changed to `{value_list[0]}`")
                                    else:
                                        await channel.send("Invalid parameter. When `<attribute>` is `wearable`, `<value>` must be `true` or `false`.")
                                elif attribute == "desc":
                                    description = " ".join(value_list)
                                    item.desc = description
                                    save()
                                    await channel.send(f"Item `{item_name}`'s description successfully changed to:\n{description}")
                                elif attribute == "key":
                                    if value_list[0] == "none":
                                        item.key = ""
                                        save()
                                        await channel.send(f"Item `{item_name}`'s key value removed successfully.")
                                    else:
                                        item.key = value_list[0]
                                        save()
                                        await channel.send(f"Item `{item_name}`'s key value successfully changed to `{value_list[0]}`.")
                                else:
                                    await channel.send("Invalid parameter. `<attribute>` must be either `name`, `weight`, `wearable`, `desc` or `key`.")
                            else:
                                await channel.send(f"`{player_name}` is wearing `{len(matching_items)}` items of clothing called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"`{player_name}` is not wearing any items of clothing called `{item_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!editplayerclothes <player> <item> [num] <attribute> <value>`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Edit Player Item Command
        # !editplayeritem <player> <item> [num] <attribute> <value>
        elif command[0] == "editplayeritem":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    item_name = command[2]
                    try:
                        item_num = int(command[3])
                        attribute = command[4]
                        value_list = command[5:]
                    except:
                        item_num = 1
                        attribute = command[3]
                        value_list = command[4:]
                    # Run Command
                    if player_name in players.keys():
                        # Define Variables
                        player = players[player_name]
                        matching_items = getmatchingitems(player.items, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                # Run Command
                                if attribute == "name":
                                    item.name = value_list[0]
                                    save()
                                    await channel.send(f"Item `{item_name}`'s name successfully changed to `{value_list[0]}`")
                                elif attribute == "weight":
                                    try:
                                        value = float(value_list[0])
                                        item.weight = value
                                        save()
                                        await channel.send(f"Item `{item_name}`'s weight successfully changed to `{value_list[0]}`")
                                    except:
                                        await channel.send("Invalid parameter. When `<attribute>` is `weight`, `<value>` must be a number.")
                                elif attribute == "wearable":
                                    value = value_list[0]
                                    if value in ["true", "false"]:
                                        wearable = True
                                        if value == "false":
                                            wearable = False
                                        item.wearable = wearable
                                        save()
                                        await channel.send(f"Item `{item_name}`'s wearble value successfully changed to `{value_list[0]}`")
                                    else:
                                        await channel.send("Invalid parameter. When `<attribute>` is `wearable`, `<value>` must be `true` or `false`.")
                                elif attribute == "desc":
                                    description = " ".join(value_list)
                                    item.desc = description
                                    save()
                                    await channel.send(f"Item `{item_name}`'s description successfully changed to:\n{description}")
                                elif attribute == "key":
                                    if value_list[0] == "none":
                                        item.key = ""
                                        save()
                                        await channel.send(f"Item `{item_name}`'s key value removed successfully.")
                                    else:
                                        item.key = value_list[0]
                                        save()
                                        await channel.send(f"Item `{item_name}`'s key value successfully changed to `{value_list[0]}`.")
                                else:
                                    await channel.send("Invalid parameter. `<attribute>` must be either `name`, `weight`, `wearable`, `desc` or `key`.")
                            else:
                                await channel.send(f"`{player_name}` is holding `{len(matching_items)}` items called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"`{player_name}` is not holding any items called `{item_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!delplayeritem <player> <item> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Edit Player Name Command
        # !editplayername <player> <name>
        elif command[0] == "editplayername":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    new_name = command[2]
                    # Run Command
                    if player_name in players.keys():
                        if not new_name in players.keys():
                            # Define Variables
                            player = players[player_name]
                            # Run Command
                            player.name = new_name
                            players[new_name] = player
                            players.pop(player_name)
                            await channel.send(f"`{command[1]}`'s name successfully changed to `{command[2]}`.")
                            save()
                        else:
                            await channel.send("There is already a player called `<name>`.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!editplayername <player> <name>`")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Edit Room
        # !editroom <room> <attribute> <value>
        elif command[0] == "editroom":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    attribute = command[2]
                    value = command[3]
                    # Run Command
                    if room_name in rooms.keys():
                        # Define Variables
                        room = rooms[room_name]
                        # Run Command
                        if attribute == "name":
                            if not value in rooms.keys():
                                for door in room.doors:
                                    if door.room1 == room_name:
                                        door.room1 = value
                                    if door.room2 == room_name:
                                        door.room2 = value
                                room.name = value
                                rooms[value] = room
                                rooms.pop(room_name)
                                save()
                                await channel.send(f"Room `{room_name}`'s name changed to `{value}` successfully.")
                            else:
                                await channel.send(f"There is already a room called `{value}`.")
                        elif attribute == "id":
                            try:
                                room.id = int(value)
                                save()
                                await channel.send(f"Room `{room_name}`'s id changed to `{value}` successfully.")
                            except ValueError:
                                await channel.send("Invalid parameter. When `<attribute>` is `id`, `<value>` must be an integer.")
                        else:
                            await channel.send("Invalid parameter. `<attribute>` must be either `name` or `id`.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!editroom <room> <attribute> <value>`")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Edit Room Item Command
        # !editroomitem <room> <item> [num] <attribute> <value>
        elif command[0] == "editroomitem":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    item_name = command[2]
                    try:
                        item_num = int(command[3])
                        attribute = command[4]
                        value_list = command[5:]
                    except:
                        item_num = 1
                        attribute = command[3]
                        value_list = command[4:]
                    # Run Command
                    if room_name in rooms.keys():
                        # Define Variables
                        room = rooms[room_name]
                        matching_items = getmatchingitems(room.items, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                # Run Command
                                if attribute == "name":
                                    item.name = value_list[0]
                                    save()
                                    await channel.send(f"Item `{item_name}`'s name successfully changed to `{value_list[0]}`")
                                elif attribute == "weight":
                                    try:
                                        value = float(value_list[0])
                                        item.weight = value
                                        save()
                                        await channel.send(f"Item `{item_name}`'s weight successfully changed to `{value_list[0]}`")
                                    except:
                                        await channel.send("Invalid parameter. When `<attribute>` is `weight`, `<value>` must be a number.")
                                elif attribute == "wearable":
                                    value = value_list[0]
                                    if value in ["true", "false"]:
                                        wearable = True
                                        if value == "false":
                                            wearable = False
                                        item.wearable = wearable
                                        save()
                                        await channel.send(f"Item `{item_name}`'s wearble value successfully changed to `{value_list[0]}`")
                                    else:
                                        await channel.send("Invalid parameter. When `<attribute>` is `wearable`, `<value>` must be `true` or `false`.")
                                elif attribute == "desc":
                                    description = " ".join(value_list)
                                    item.desc = description
                                    save()
                                    await channel.send(f"Item `{item_name}`'s description successfully changed to:\n{description}")
                                elif attribute == "key":
                                    if value_list[0] == "none":
                                        item.key = ""
                                        save()
                                        await channel.send(f"Item `{item_name}`'s key value removed successfully.")
                                    else:
                                        item.key = value_list[0]
                                        save()
                                        await channel.send(f"Item `{item_name}`'s key value successfully changed to `{value_list[0]}`.")
                                else:
                                    await channel.send("Invalid parameter. `<attribute>` must be either `name`, `weight`, `wearable`, `desc` or `key`.")
                            else:
                                await channel.send(f"There are `{len(matching_items)}` items in room `{room_name}` called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"There are no items in room `{room_name}` called `{item_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!editroomitem <room> <item> [num] <attribute> <value>`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Edit Room Object Command
        # !editroomobject <room> <object> [num] <attribute> <value>
        elif command[0] == "editroomobject":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    object_name = command[2]
                    try:
                        object_num = int(command[3])
                        attribute = command[4]
                        value_list = command[5:]
                    except:
                        object_num = 1
                        attribute = command[3]
                        value_list = command[4:]
                    # Run Command
                    if room_name in rooms.keys():
                        # Define Variables
                        room = rooms[room_name]
                        matching_objects = getmatchingitems(room.objects, object_name)
                        # Run Command
                        if len(matching_objects) > 0:
                            if object_num > 0 and object_num <= len(matching_objects):
                                # Define Variables
                                object = matching_objects[object_num-1]
                                # Run Command
                                if attribute == "name":
                                    object.name = value_list[0]
                                    save()
                                    await channel.send(f"Object `{object_name}`'s name has successfully been changed to `{value_list[0]}`.")
                                elif attribute == "storage":
                                    try:
                                        object.storage = int(value_list[0])
                                        save()
                                        await channel.send(f"Object `{object_name}`'s storage space has successfully been changed to `{value_list[0]}`.")
                                    except:
                                        await channel.send("Invalid parameter. When `<attribute>` is `storage`, `<value>` must be a number.")
                                elif attribute == "desc":
                                    description = " ".join(value_list)
                                    object.desc = description
                                    await channel.send(f"Object `{object_name}`'s description has successfully been changed to:\n{object.desc}")
                                    save()
                                elif attribute == "state":
                                    state = value_list[0].upper()
                                    if state in ["OPEN", "LOCKED", "NONE"]:
                                        object.state = state
                                        save()
                                        await channel.send(f"Object `{object_name}`'s state has successfully been changed to `{state}`.")
                                    else:
                                        await channel.send("Invalid parameter. When `<attribute>` is `state`, `<value>` must be either `OPEN`, `LOCKED` or `NONE`.")
                                elif attribute == "key":
                                    if value_list[0] == "none":
                                        object.key = ""
                                        save()
                                        await channel.send(f"Item `{object_name}`'s key value removed successfully.")
                                    else:
                                        object.key = value_list[0]
                                        save()
                                        await channel.send(f"Item `{object_name}`'s key value successfully changed to `{value_list[0]}`.")
                                else:
                                    await channel.send("Invalid parameter. `<attribute>` must be either `name`, `storage`, `desc`, `state` or `key`.")
                            else:
                                await channel.send(f"There are `{len(matching_objects)}` objects in room `{room_name}` called `{object_name}`, so `[num]` must be specified between `1` and `{len(matching_objects)}`.")
                        else:
                            await channel.send(f"There are no objects in room `{room_name}` called `{object_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!delroomobject <room> <object> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Force Drop Command
        # !forcedrop <player> <item> [num]
        elif command[0] == "forcedrop":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    item_name = command[2]
                    item_num = 1
                    if len(command) >= 4:
                        item_num = int(command[3])
                    # Run Command
                    if player_name in players.keys():
                        # Define Variables
                        player = players[player_name]
                        room_name = player.room
                        matching_items = getmatchingitems(player.items, item_name)
                        # Run Command
                        if room_name in rooms.keys():
                            if len(matching_items) > 0:
                                if item_num > 0 and item_num <= len(matching_items):
                                    # Define Variables
                                    room = rooms[room_name]
                                    item = matching_items[item_num-1]
                                    # Run Command
                                    room.items.append(item)
                                    player.items.remove(item)
                                    save()
                                    await channel.send(f"`{player_name}` has dropped the `{item_name}`.")
                                else:
                                    await channel.send(f"`{player_name}` is holding `{len(matching_items)}` items called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                            else:
                                await channel.send(f"`{player_name}` is not holding any items called `{item_name}`.")
                        else:
                            await channel.send(f"Error: Player `{player_name}` is not in a valid room.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!forcedrop <player> <item> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Force Take Command
        # !forcetake <player> <item> [num]
        elif command[0] == "forcetake":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    item_name = command[2]
                    item_num = 1
                    if len(command) >= 4:
                        item_num = int(command[3])
                    # Run Command
                    if player_name in players.keys():
                        # Define Variables
                        player = players[player_name]
                        room_name = player.room
                        # Run Command
                        if room_name in rooms.keys():
                            # Define Variables
                            room = rooms[room_name]
                            matching_items = getmatchingitems(room.items, item_name)
                            # Run Command
                            if len(matching_items) > 0:
                                if item_num > 0 and item_num <= len(matching_items):
                                    # Define Variables
                                    item = matching_items[item_num-1]
                                    # Run Command
                                    player.items.append(item)
                                    room.items.remove(item)
                                    save()
                                    await channel.send(f"`{player_name}` has taken the `{item_name}`.")
                                else:
                                    await channel.send(f"There are `{len(matching_items)}` items in the `{room_name}` called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                            else:
                                await channel.send(f"There are no items items in the `{room_name}` called `{item_name}`.")
                        else:
                            await channel.send(f"Error: Player `{player_name}` is not in a valid room.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!forcetake <player> <item> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Force Take Wear Command
        # !forcetakewear <player> <item> [num]
        elif command[0] == "forcetakewear":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    item_name = command[2]
                    item_num = 1
                    if len(command) >= 4:
                        item_num = int(command[3])
                    # Run Command
                    if player_name in players.keys():
                        # Define Variables
                        player = players[player_name]
                        room_name = player.room
                        # Run Command
                        if room_name in rooms.keys():
                            # Define Variables
                            room = rooms[room_name]
                            matching_items = getmatchingitems(room.items, item_name)
                            # Run Command
                            if len(matching_items) > 0:
                                if item_num > 0 and item_num <= len(matching_items):
                                    # Define Variables
                                    item = matching_items[item_num-1]
                                    # Run Command
                                    player.clothes.append(item)
                                    room.items.remove(item)
                                    save()
                                    await channel.send(f"`{player_name}` has taken and worn the `{item_name}`.")
                                else:
                                    await channel.send(f"There are `{len(matching_items)}` items in the `{room_name}` called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                            else:
                                await channel.send(f"There are no items items in the `{room_name}` called `{item_name}`.")
                        else:
                            await channel.send(f"Error: Player `{player_name}` is not in a valid room.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!forcetakewear <player> <item> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Force Undress Command
        # !forceundress <player> <item> [num]
        elif command[0] == "forceundress":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    item_name = command[2]
                    item_num = 1
                    if len(command) >= 4:
                        item_num = int(command[3])
                    # Run Command
                    if player_name in players.keys():
                        # Define Variables
                        player = players[player_name]
                        matching_items = getmatchingitems(player.clothes, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                # Run Command
                                player.items.append(item)
                                player.clothes.remove(item)
                                save()
                                await channel.send(f"`{player_name}` has taken off the `{item_name}`.")
                            else:
                                await channel.send(f"`{player_name}` is wearing `{len(matching_items)}` items of clothing called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"`{player_name}` is not wearing any items of clothing called `{item_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!forceundress <player> <item> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Force Undress Drop Command
        # !forceundressdrop <player> <item> [num]
        elif command[0] == "forceundressdrop":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    item_name = command[2]
                    item_num = 1
                    if len(command) >= 4:
                        item_num = int(command[3])
                    # Run Command
                    if player_name in players.keys():
                        # Define Variables
                        player = players[player_name]
                        room_name = player.room
                        matching_items = getmatchingitems(player.clothes, item_name)
                        # Run Command
                        if room_name in rooms.keys():
                            if len(matching_items) > 0:
                                if item_num > 0 and item_num <= len(matching_items):
                                    # Define Variables
                                    room = rooms[room_name]
                                    item = matching_items[item_num-1]
                                    # Run Command
                                    room.items.append(item)
                                    player.clothes.remove(item)
                                    save()
                                    await channel.send(f"`{player_name}` has taken off and dropped the `{item_name}`.")
                                else:
                                    await channel.send(f"`{player_name}` is wearing `{len(matching_items)}` items of clothing called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                            else:
                                await channel.send(f"`{player_name}` is not wearing any items of clothing called `{item_name}`.")
                        else:
                            await channel.send(f"Error: Player `{player_name}` is not in a valid room.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!forceundressdrop <player> <item> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # Force Wear Command
        # !forcewear <player> <item> [num]
        elif command[0] == "forcewear":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    item_name = command[2]
                    item_num = 1
                    if len(command) >= 4:
                        item_num = int(command[3])
                    # Run Command
                    if player_name in players.keys():
                        # Define Variables
                        player = players[player_name]
                        matching_items = getmatchingitems(player.items, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                # Run Command
                                player.clothes.append(item)
                                player.items.remove(item)
                                save()
                                await channel.send(f"`{player_name}` is now wearing the `{item_name}`.")
                            else:
                                await channel.send(f"`{player_name}` is holding `{len(matching_items)}` items called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"`{player_name}` is not holding any items called `{item_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!forcewear <player> <item> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # List Object Items Command
        # !listobjectitems <room> <object> [num]
        elif command[0] == "listobjectitems":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    object_name = command[2]
                    object_num = 1
                    if len(command) >= 4:
                        object_num = int(command[3])
                    # Run Command
                    if room_name in rooms.keys():
                        # Define Variables
                        room = rooms[room_name]
                        matching_objects = getmatchingitems(room.objects, object_name)
                        # Run Command
                        if len(matching_objects) > 0:
                            if object_num > 0 and object_num <= len(matching_objects):
                                # Define Variables
                                object = matching_objects[object_num-1]
                                itemstring = getthingnamestring(object.items)
                                # Run Command
                                if itemstring == "":
                                    await channel.send(f"There are no items in the `{object.name}`.")
                                else:
                                    await channel.send(f"The following items are in the `{object.name}`:\n{itemstring}")
                            else:
                                await channel.send(f"There are `{len(matching_objects)}` objects in room `{room_name}` called `{object_name}`, so `[num]` must be specified between `1` and `{len(matching_objects)}`.")
                        else:
                            await channel.send(f"There are no objects in room `{room_name}` called `{object_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!listobjectitems <room> <object> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # List Player Clothes Command
        # !listplayerclothes <player>
        elif command[0] == "listplayerclothes":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    # Run Command
                    if player_name in players.keys():
                        player = players[player_name]
                        itemstring = getthingnamestring(player.clothes)
                        # Run Command
                        if itemstring == "":
                            await channel.send(f"`{player_name}` is currently not wearing any clothes. :thinking:")
                        else:
                            await channel.send(f"`{player_name}` is currently wearing these clothes:\n{itemstring}")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!listplayerclothes <player>`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # List Player Items Command
        # !listplayeritems <player>
        elif command[0] == "listplayeritems":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    # Run Command
                    if player_name in players.keys():
                        player = players[player_name]
                        itemstring = getthingnamestring(player.items)
                        # Run Command
                        if itemstring == "":
                            await channel.send(f"`{player_name}` is currently not holding any items.")
                        else:
                            await channel.send(f"`{player_name}` is currently holding these items:\n{itemstring}")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a player.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!listplayeritems <player>`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # List Players Command
        # !listplayers
        elif command[0] == "listplayers":
            if admin:
                try:
                    # Run Command
                    if len(players) >= 1:
                        playerlist = []
                        for player in players.keys():
                            playerlist.append(player)
                        playerstring = f"`{playerlist[0]}`"
                        for player in playerlist[1:]:
                            playerstring += f", `{player}`"
                        await channel.send(f"The players are:\n{playerstring}")
                    else:
                        await channel.send("There are no players.")
                except:
                    await channel.send("Invalid command format. The correct format is: `!listplayers`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # List Room Doors Command
        # !listroomdoors <room> [state]
        elif command[0] == "listroomdoors":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    state = "ANY"
                    if len(command) >= 3:
                        state = command[2].upper()
                    # Run Command
                    if room_name in rooms.keys():
                        if state in ("ANY", "OPEN", "LOCKED", "HIDDEN"):
                            # Define Paramaters
                            room = rooms[room_name]
                            room_list = getdoorroomlist(room.doors, room.name, state=state)
                            room_names_string = getstringnamestring(room_list)
                            # Run Command
                            if room_names_string == "":
                                await channel.send(f"There are no rooms connected to room `{room_name}` with state `{state}`.")
                            else:
                                await channel.send(f"The following rooms are connected to room `{room_name}` with state `{state}`:\n{room_names_string}")
                        else:
                            await channel.send(f"Invalid parameter. `<state>` must either be `open`, `locked`, `hidden` or `any`.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!listroomdoors <room> [state]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # List Room Items Command
        # !listroomitems <room>
        elif command[0] == "listroomitems":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    # Run Command
                    if room_name in rooms.keys():
                        room = rooms[room_name]
                        itemstring = getthingnamestring(room.items)
                        # Run Command
                        if itemstring == "":
                            await channel.send(f"There are no items in room `{room_name}`.")
                        else:
                            await channel.send(f"The following objects are in room `{room_name}`:\n{itemstring}")
                    else:
                        await channel.send(f"Invalid paramater. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!listroomitems <room>`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # List Room Objects Command
        # !listroomobjects <room>
        elif command[0] == "listroomobjects":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    # Run Command
                    if room_name in rooms.keys():
                        room = rooms[room_name]
                        objectstring = getthingnamestring(room.objects)
                        # Run Command
                        if objectstring == "":
                            await channel.send(f"There are no objects in room `{room_name}`.")
                        else:
                            await channel.send(f"The following objects are in room `{room_name}`:\n{objectstring}")
                    else:
                        await channel.send(f"Invalid paramater. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!listroomobjects <room>`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # List Rooms Command
        # !listrooms
        elif command[0] == "listrooms":
            if admin:
                if len(rooms) >= 1:
                    roomlist = []
                    for room in rooms.keys():
                        roomlist.append(room)
                    roomstring = f"`{roomlist[0]}`"
                    for room in roomlist[1:]:
                        roomstring += f", `{room}`"
                    await channel.send(f"The rooms are:\n{roomstring}")
                else:
                    await channel.send("There are no rooms.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # See Object Item Command
        # !seeobjectitem <room> <object> [num] <item> [num]
        elif command[0] == "seeobjectitem":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    object_name = command[2]
                    try:
                        object_num = int(command[3])
                        item_name = command[4]
                        item_num = 1
                        if len(command) >= 6:
                            item_num = int(command[5])
                    except:
                        object_num = 1
                        item_name = command[3]
                        item_num = 1
                        if len(command) >= 5:
                            item_num = int(command[4])
                    if room_name in rooms.keys():
                        room = rooms[room_name]
                        matching_objects = getmatchingitems(room.objects, object_name)
                        # Run Command
                        if len(matching_objects) > 0:
                            if object_num > 0 and object_num <= len(matching_objects):
                                # Define Variables
                                object = matching_objects[object_num-1]
                                matching_items = getmatchingitems(object.items, item_name)
                                # Run Command
                                if len(matching_items) > 0:
                                    if item_num > 0 and item_num <= len(matching_items):
                                        # Define Variables
                                        item = matching_items[item_num-1]
                                        # Run Command
                                        await channel.send(f"Item Name: `{item.name}`\nWeight: `{item.weight}` Wearable: `{item.wearable}` Key: `{item.key}` \n{item.desc}")
                                    else:
                                        await channel.send(f"There are `{len(matching_items)}` items in the `{object_name}` called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                                else:
                                    await channel.send(f"You are no items in the `{object_name}` called `{item_name}`.")
                            else:
                                await channel.send(f"There are `{len(matching_objects)}` objects here called `{object_name}`, so `[num]` must be specified between `1` and `{len(matching_objects)}`.")
                        else:
                            await channel.send(f"There are no objects in room `{room_name}` called `{object_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Incorrect command format. The correct format is: `!seeobjectitem <room> <object> [num] <item> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # See Player Clothes Command
        # !seeplayerclothes <player> <item> [num]
        elif command[0] == "seeplayerclothes":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    item_name = command[2]
                    item_num = 1
                    if len(command) >= 4:
                        item_num = int(command[3])
                    # Run Command
                    if player_name in players.keys():
                        # Define Variables
                        player = players[player_name]
                        matching_items = getmatchingitems(player.clothes, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                # Run Command
                                await channel.send(f"Item Name: `{item.name}`\nWeight: `{item.weight}` Wearable: `{item.wearable}` Key: `{item.key}` \n{item.desc}")
                            else:
                                await channel.send(f"`{player_name}` is wearing `{len(matching_items)}` items of clothing called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"`{player_name}` is not wearing any clothes called `{item_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a room.")
                except:
                    await channel.send("Invalid command format. The correct format is: `!seeplayerclothes <player> <item> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # See Player Item Command
        # !seeplayeritem <player> <item> [num]
        elif command[0] == "seeplayeritem":
            if admin:
                try:
                    # Define Variables
                    player_name = command[1]
                    item_name = command[2]
                    item_num = 1
                    if len(command) >= 4:
                        item_num = int(command[3])
                    # Run Command
                    if player_name in players.keys():
                        # Define Variables
                        player = players[player_name]
                        matching_items = getmatchingitems(player.items, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                # Run Command
                                await channel.send(f"Item Name: `{item.name}`\nWeight: `{item.weight}` Wearable: `{item.wearable}` Key: `{item.key}` \n{item.desc}")
                            else:
                                await channel.send(f"`{player_name}` is holding `{len(matching_items)}` items called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"`{player_name}` is not holding any items called `{item_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<player>` must be the name of a room.")
                except:
                    await channel.send("Invalid command format. The correct format is: `!seeplayeritem <player> <item> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # See Door
        # !seedoor <room1> <room2>
        elif command[0] == "seedoor":
            if admin:
                try:
                    # Define Variables
                    room1_name = command[1]
                    room2_name = command[2]
                    # Run Command
                    if room1_name in rooms.keys():
                        if room2_name in rooms.keys():
                            try:
                                # Define Variables
                                room1 = rooms[room1_name]
                                door = finddoor(room1.doors, room1_name, room2_name)
                                await channel.send(f"Door between `{room1_name}` and `{room2_name}`:\nState: `{door.state}` Key:`{door.key}`")
                            except:
                                await channel.send(f"There is no door between rooms `{room1_name}` and `{room2_name}`.")
                        else:
                            await channel.send("Invalid parameter. `<room2>` must be the name of a room.")
                    else:
                        await channel.send("Invalid parameter. `<room1>` must be the name of a room.")
                except:
                    await channel.send("Invalid command format. The correct format is: `!seedoor <room1> <room2>`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # See Room Item Command
        # !seeroomitem <room> <item> [num]
        elif command[0] == "seeroomitem":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    item_name = command[2]
                    item_num = 1
                    if len(command) >= 4:
                        item_num = int(command[3])
                    # Run Command
                    if room_name in rooms.keys():
                        # Define Variables
                        room = rooms[room_name]
                        matching_items = getmatchingitems(room.items, item_name)
                        # Run Command
                        if len(matching_items) > 0:
                            if item_num > 0 and item_num <= len(matching_items):
                                # Define Variables
                                item = matching_items[item_num-1]
                                # Run Command
                                await channel.send(f"Item Name: `{item.name}` \nWeight: `{item.weight}` Wearable: `{item.wearable}` Key: `{item.key}` \n{item.desc}")
                            else:
                                await channel.send(f"There are `{len(matching_items)}` items in room `{room_name}` called `{item_name}`, so `[num]` must be specified between `1` and `{len(matching_items)}`.")
                        else:
                            await channel.send(f"There are not any items in room `{room_name}` called `{item_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Invalid command format. The correct format is: `!seeroomitem <room> <item> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        # See Room Object Command
        # !seeroomobject <room> <object> [num]
        elif command[0] == "seeroomobject":
            if admin:
                try:
                    # Define Variables
                    room_name = command[1]
                    object_name = command[2]
                    object_num = 1
                    if len(command) >= 4:
                        object_num = int(command[3])
                    # Run Command
                    if room_name in rooms.keys():
                        # Define Variables
                        room = rooms[room_name]
                        matching_objects = getmatchingitems(room.objects, object_name)
                        # Run Command
                        if len(matching_objects) > 0:
                            if object_num > 0 and object_num <= len(matching_objects):
                                # Define Variables
                                object = matching_objects[object_num-1]
                                # Run Command
                                await channel.send(f"Object Name: `{object.name}`\nStorage: `{object.storage}` State: `{object.state}` Key: `{object.key}` \n{object.desc}")
                            else:
                                await channel.send(f"There are `{len(matching_objects)}` objects in room `{room_name}` called `{object_name}`, so `[num]` must be specified between `1` and `{len(matching_objects)}`.")
                        else:
                            await channel.send(f"There are not any objects in room `{room_name}` called `{object_name}`.")
                    else:
                        await channel.send("Invalid parameter. `<room>` must be the name of a room.")
                except:
                    await channel.send("Invalid command format. The correct format is: `!seeroomobject <room> <object> [num]`.")
            else:
                await channel.send("You do not have permission to perform this command.")

        #########################
        #    SECRET COMMANDS    #
        #########################

        elif command[0] == "meow":
            await channel.send("meow!")

        elif command[0] == "fingers":
            await channel.send("*You wiggle your fingers at DiscordBotRP. DiscordBotRP sees the wiggly fingers and approaches for a head massage. It is very cute.*")

        elif command[0] == "piperoom":
            await channel.send("Congratulations! You have found the pipe room! Just kidding. **You will never find the pipe room.**")

        elif command[0] == "secret":
            await channel.send("Look behind the bookshelf in the kitchen.")

        elif command[0] == "leo":
            await channel.send("*DiscordBotRP runs away!*")

        elif command[0] == "unique":
            await channel.send("https://www.youtube.com/TheUniqueImpact")

        elif command[0] == "mastermind":
            await channel.send("Oh, so you want to know who the mastermind is, huh? Well, I'm not gonna tell you! I've heard that `!greggory` knows who it is though...")

        elif command[0] == "greggory":
            await channel.send("Whaaat? The mastermind? Naaah, you've got the wrong guy! It's `!greggory2` who knows that!")

        elif command[0] == "greggory2":
            await channel.send("Hello weary traveller. My name is Greggory 2. I heard you were on a mighty quest for the mastermind. Well, you have come to the right place! The mastermind lurks not far from here, just within the walls of the `!castle`.")

        elif command[0] == "castle":
            await channel.send("Your mastermind is in another castle.")

        elif command[0] == "anothercastle":
            await channel.send("Nope.")

        elif command[0] == "clara":
            await channel.send("https://www.youtube.com/watch?v=rY-FJvRqK0E")

        elif command[0] == "dave":
            await channel.send("https://youtu.be/TVo8lW6Hxow")

        elif command[0] == "command":
            await channel.send("Yes this is a command.")

        elif command[0] == "jacob":
            await channel.send("Alright Jacob. That's enough. You can stop looking for secret commands now.")

        elif command[0] == "queso":
            await channel.send(":Queso: :Queso: :Queso: :Queso: :Queso: :Queso: :Queso: :Queso: :Queso:")

        elif command[0] == "nibbles":
            await channel.send("Hey that's me!")

        elif command[0] == "monokuma":
            await channel.send("Puhuhu!")

        elif command[0] == "dream":
            await channel.send("Tehehe!")

        elif command[0] == "code":
            await channel.send("The super secret special awesome code is `M-I-C-R-O-W-A-V-E`.")

        elif command[0] == "sleep":
            await channel.send("*Purple gas fills the room. You fall asleep.*")

        elif command[0] == "wake":
            await channel.send("*A strange feeling comes over you as you wake up.*")

        elif command[0] == "joke":
            await channel.send("What do you call a joke without a punchline?")

        elif command[0] == "traitor":
            await channel.send("The traitor is.... you!")

        # Command not known
        else:
            await channel.send("Unknown command. Use `!help` for a list of valid commands, and `!adminhelp` for a list of valid admin commands.")

        await message.delete()

client.run(token)