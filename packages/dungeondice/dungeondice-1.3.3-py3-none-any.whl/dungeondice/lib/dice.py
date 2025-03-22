#!/usr/bin/env python3
import re
import random

# The dicequant and rollstring_re are used together for initial parsing of
# rollstrings. They decide whether the complete rollstring is something
# We will try handling at all.
# The set_finder is slightly different, to facillitate finding different
# sets within a group of dice.
# See the "Parser()" for more info on this.
dicequant = r'[+\-,x]?\d*(d\d+)?(kl?\d*)?(\(\w+\))?'
set_finder = r'([+\-,x]?\d*d?\d+k?l?\d*\(?\w*\)?)'
rollstring_re = re.compile(r"({dicequant})*".format(
    dicequant=dicequant
))


class rollstring(str):
    def __new__(cls, value):
        if not rollstring_re.fullmatch(value):
            raise ValueError("Not a valid diceroll.")
        return super().__new__(cls, value)


class Rollset():
    """Represent one single set of rolled dice (2d20k1)

    A set contains one or more dice. Or a single integer for flat bonusses.
    Use 'k' or 'kl' to keep the highest or lowest rolls within a set.
    """

    def __init__(self, dicestring, quant, dice, keep, keep_highest, negative,
                 comment=''):
        self.rollstring = dicestring
        self.quant = quant
        self.dice = dice
        self.keep_amount = keep
        self.keep_highest = keep_highest
        self.rolled_dice = []
        self.total = None
        self.comment = comment
        self.negative = negative

    def roll(self, fumble=None):
        """Roll this group."""
        plusminus = '-' if self.negative else '+'

        if self.quant == 0:
            self.rolled_dice = [int(self.rollstring)]
            self.total = int(self.rollstring)
            self.comment = "{}{}{}".format(plusminus, self.total, self.comment)
        else:
            if not fumble:
                rolled_dice = [
                    random.randint(1, self.dice) for i in range(0, self.quant)
                ]
            else:
                rolled_dice = [
                    fumble for i in range(0, self.quant)
                ]
            rolled_dice.sort(reverse=self.keep_highest)

            self.rolled_dice = rolled_dice
            self.total = sum(self.rolled_dice[:self.keep_amount])
            self.comment = "{}{}{}".format(plusminus, self.total, self.comment)

    @classmethod
    def from_string(cls, dicestring, negative):
        """Create a rollgroup from a string."""
        commentmatch = re.search(r'\(\w+\)', dicestring)
        if commentmatch:
            comment = commentmatch.group()
            dicestring = dicestring.replace(comment, '')
            comment = comment.replace('(', '').replace(')', '')
        else:
            comment = ''

        if dicestring.isdigit():
            return cls(
                dicestring, 0, 0, 0, False, negative, comment=comment
            )

        highest = False
        quant, rest = dicestring.split('d')
        quant = 1 if not quant else int(quant)

        if 'kl' in rest:
            dice, keep = rest.split('kl')
            dice = int(dice)
            keep = int(keep)
        elif 'k' in rest:
            dice, keep = rest.split('k')
            dice = int(dice)
            keep = int(keep)
            highest = True
        else:
            keep = int(quant)
            dice = int(rest)

        return cls(
            dicestring, quant, dice, keep, highest, negative, comment=comment
        )

    def __repr__(self):
        if len(self.rolled_dice) > 100:
            rolled_dice = "[Lots of dice]"
        else:
            rolled_dice = self.rolled_dice

        if self.quant != self.keep_amount:
            keepstr = 'k' if self.keep_highest else 'kl'
            keepstr += str(self.keep_amount)
        else:
            keepstr = ''

        return "{}{}**{}**".format(
            rolled_dice, keepstr, self.comment)

    def __eq__(self, other):
        if (
            self.quant == other.quant and
            self.dice == other.dice and
            self.keep_amount == other.keep_amount and
            self.keep_highest == other.keep_highest
        ):
            return True
        else:
            return False


class Rollgroup():
    """Represent one group of rolled dice (2d20k1+4+d20)

    A group contains one or more sets of dice, or integers. With either
    + or - modifiers to signal whether they add or substract from the total.
    """

    def __init__(self, dicestring, additions, substractions, rollsets):
        self.rollstring = dicestring
        self.additions = additions
        self.substractions = substractions
        self.rollsets = rollsets
        self.total = None

    def roll(self, fumble=None):
        """Roll this group."""
        for rollset in self.additions:
            rollset.roll(fumble=fumble)
        for rollset in self.substractions:
            rollset.roll(fumble=fumble)

        self.total = sum(
            [i.total for i in self.additions]
        ) - sum([i.total for i in self.substractions])

    @classmethod
    def from_string(cls, dicestring):
        """Create a rollgroup from a string."""
        substractions = []
        additions = []
        rollsets = []

        for set_dicestring in re.findall(set_finder, dicestring):
            negative = False

            if set_dicestring[0] == '-':
                negative = True
                set_dicestring = set_dicestring[1:]
            elif set_dicestring[0] == '+':
                set_dicestring = set_dicestring[1:]

            new_rollset = Rollset.from_string(set_dicestring, negative)
            rollsets.append(new_rollset)

            if negative:
                substractions.append(new_rollset)
            else:
                additions.append(new_rollset)

        return cls(dicestring, additions, substractions, rollsets)

    def __repr__(self):
        return self.rollstring

    def __eq__(self, other):
        return self.rollstring == other.rollstring


class Parser():
    """Take in rollstrings, and shit out rolled dice

    The parser should only be concerned with dice. Not with how we want
    to present those to whatever application will be used to implement
    this module.

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
    """

    def handle_multiplier(self, dicestring):
        """Split a string like '2x2d20' into multiple rollgroups."""
        if 'x' not in dicestring:
            return [Rollgroup.from_string(dicestring)]

        quant, dice = dicestring.split('x')
        return [Rollgroup.from_string(dice) for i in range(0, int(quant))]

    def create_rollgroups(self, dicestring):
        """Create groups of dice to roll."""
        rollgroup_list = [
            self.handle_multiplier(i) for i in dicestring.split(',')
        ]
        return [i for g in rollgroup_list for i in g]

    def parse(self, dicestring: str):
        """Parse a rollstring and roll the dice."""
        dicestring = rollstring(dicestring)

        rollgroups = self.create_rollgroups(dicestring)
        for group in rollgroups:
            group.roll()

        return rollgroups
