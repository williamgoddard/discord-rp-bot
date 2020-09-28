Discord RP Bot
Written by Stephen Goddard (2020)

This bot performs several utility functions for text-based roleplay in the Discord messaging app. This includes tracking players' current rooms, and updating
permissions to text channels to allow them to only see the room they are currently in, as well as inventory and item management. The bot makes use of the
Discord botting API. In order for it to function correctly, a Discord Application must be created, and invited to a Discord server. The associated token for
that application is needed on line 5. Details on how to do this can be found at the following link:

https://discordpy.readthedocs.io/en/latest/discord.html

Upon running the bot, it should function on the server it has been invited to. There are two types of commands you can run with the bot - player commands and
admin commands. In order for a user to be able to use player commands, they must be listed as a player with the bot. This can be done using the !addplayer
command. In order for a user to use admin commands, they must have a role on the discord server titled "Host". A list of player commands can be seen by typing
!help, and a list of admin commands can be seen by typing !adminhelp.
