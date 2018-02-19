# dach-support

This is the code for a Discord / Steem Bot, making it possible for a community to control a voting bot in Steem using Discord.
In the end this shall provide this service to the german community, currently organized within the D-A-CH Discord Server.

The pure Discord side of the bot is finished, now I will start integrating the Steem parts.


## Setup Instructions

You have to have Python 3.6 installed on your computer, as well es discord and steempy. This is done quite easy using pip3 install -U steempy and pip3 install -U discord


Installing steempy sometimes poses a problem because of the toml package that is expected in version 0.9.3.1 but has 0.9.3, this can be changed in /usr/local/lib/python3.6/dist-packages/steem-0.18.3...../METADATA.
Search the respective line and change the value to 0.9.3

