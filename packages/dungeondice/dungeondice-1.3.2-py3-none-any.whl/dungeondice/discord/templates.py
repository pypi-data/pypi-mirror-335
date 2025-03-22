#!/usr/bin/env python3
from dungeondice.lib import dice


def dicerolls(author: str, rollgroups: list[dice.Rollgroup], comment: str):
    comment = "__{}__".format(comment) if comment else comment
    out = ''

    for rg in rollgroups:
        out += '''\
---------------------------------
> {}
**Total: {}**
_Details: {}_
---------------------------------
'''.format(rg.rollstring, rg.total, rg.rollsets)

    return '''\
**{}** rolled {}
{}
'''.format(author, comment, out)


def privatemessage(author: str, message: str):
    message = "__{}__".format(message) if message else message

    return "**{}** rolled {}".format(
        author, message
    )
