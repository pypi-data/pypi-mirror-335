#!/usr/bin/env python3

import discord
from discord.ext import commands
from discord import app_commands

from dungeondice.lib import dice
from dungeondice.discord import templates


class Roll(commands.Cog):

    def __init__(self):
        self.diceparser = dice.Parser()

    @commands.command(
        name='roll',
        aliases=['r'],
        description='roll',
        brief='Roll some dice.',
        help='''Roll dice in a format like "2x2d20(poison)+d8(piercing)-4"

Rolls consist of multiple layers. The parser first cuts up rollstrings
into multiple 'groups' of 'sets' by parsing all the x and , modifiers.
The 'x' being a multiplier that creates multiple of the same rollgroups.
The ',' being a separator that allows you to create multiple different
groups in one go.
Everything behind the 'x' modifier is treated as part of the multiplier
until terminated by a ','.

Examples:
2xd20+d10:     Roll d20+d10 twice. Returning two different groups with
                their own totals.
d20,d20:       Roll a d20 twice. Returning two different groups with their
                own totals. In this case it being the total of 1 dice.
2xd20+d10,d10: Roll d20+d10 twice, roll d10 once. Returning three different
                groups with their own totals.
''',
    )
    async def roll(
        self,
        ctx,
        dicestring: dice.rollstring,
        *, message: str = ''
    ):
        """Uses the diceparser to roll dice."""
        await ctx.send(
            templates.dicerolls(
                ctx.author.display_name,
                self.diceparser.parse(dicestring),
                message
            )
        )

    @commands.command(
        name='rollprivate',
        aliases=['rp'],
        description='roll privately, but let others know you are rolling.',
        brief='Roll some dice without exposing the results to others.',
        help='''Roll privately. But let others know you are doing so.

Works exactly like normal rolling. But let's you hide the result.
Reults are posted in DM. Use slashcommands (/rp) if you want to see
hidden messages in the channel you're rolling in.
''',
    )
    async def rollprivate(
        self,
        ctx,
        dicestring: dice.rollstring,
        *, message: str = ''
    ):
        """Uses the diceparser to roll dice."""
        await ctx.author.send(
            templates.dicerolls(
                ctx.author.display_name,
                self.diceparser.parse(dicestring),
                message,
            )
        )
        await ctx.send(
            templates.privatemessage(
                ctx.author.display_name,
                message,
            )
        )

    @commands.command(
        name='rollinvisible',
        aliases=['ri'],
        description='roll invisibly, do not let others know you are rolling.',
        brief='Roll some dice without exposing the results to others.',
        help='''Roll privately. do not let others know you are doing so.

Works exactly like normal rolling. But let's you hide the result.
Reults are posted in DM. Use slashcommands (/ri) if you want to see
hidden messages in the channel you're rolling in.
''',
    )
    async def rollinvisible(
        self,
        ctx,
        dicestring: dice.rollstring,
        *, message: str = ''
    ):
        """Uses the diceparser to roll dice."""
        await ctx.author.send(
            templates.dicerolls(
                ctx.author.display_name,
                self.diceparser.parse(dicestring),
                message,
            )
        )

    @app_commands.command(
        name='r',
        description='roll, but with a slashcommand.',
    )
    async def r(
        self,
        interaction: discord.Interaction,
        message: str,
    ):
        """Uses the diceparser to roll dice."""
        dicestring, *rest = message.split(maxsplit=1)
        message = rest[0] if rest else ''

        await interaction.response.send_message(
            templates.dicerolls(
                interaction.user.display_name,
                self.diceparser.parse(dicestring),
                message,
            ),
        )

    @app_commands.command(
        name='rp',
        description='roll privately, but let others know you are rolling.',
    )
    async def rp(
        self,
        interaction: discord.Interaction,
        message: str,
    ):
        """Uses the diceparser to roll dice."""
        dicestring, *rest = message.split(maxsplit=1)
        message = rest[0] if rest else ''

        await interaction.response.send_message(
            templates.dicerolls(
                interaction.user.display_name,
                self.diceparser.parse(dicestring),
                message,
            ),
            ephemeral=True,
        )
        await interaction.followup.send(
            templates.privatemessage(
                interaction.user.display_name,
                message,
            )
        )

    @app_commands.command(
        name='ri',
        description='roll invisibly, do not let others know you are rolling.',
    )
    async def ri(
        self,
        interaction: discord.Interaction,
        message: str,
    ):
        """Uses the diceparser to roll dice."""
        dicestring, *rest = message.split(maxsplit=1)
        message = rest[0] if rest else ''

        await interaction.response.send_message(
            templates.dicerolls(
                interaction.user.display_name,
                self.diceparser.parse(dicestring),
                message,
            ),
            ephemeral=True,
        )

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Invalid dicestring.')
        else:
            print(error)
            await ctx.send('Uncaught error while rolling.')
