[![Upload Python Package](https://github.com/jwizzle/dungeondice/actions/workflows/python-publish.yml/badge.svg)](https://github.com/jwizzle/dungeondice/actions/workflows/python-publish.yml)

# Dungeondice

This is a discord bot that aims to become a feature-rich yet easy to use option for rolling dice for TTRPG's online.
I aim to keep the logic of the bot detached from discord integration. So the python package is re-usable in other places.

## Features

- Roll dice in a discord channel
- Roll privately, either telling others you rolled or not. To simulate the feeling of hearing your DM's dice go behind a screen
- Supports both discord slashcommands for features like ephemeral messages, or regular !commands that feel more responsive
- Roll multiple sets in one go `2x2d20`
- Add hints to your dice `d10(piercing)+d8(poison)`
- Add hints to your complete roll `d8(poison) For damage`
- Create complex rolls like `2x2d20(poison)+d8(piercing)-4` to get two total results
```
---------------------------------
2d20(poison)+d8(piercing)-4
Total: 35
Details: [[16, 17]33poison, [6]6piercing, [4]4]
---------------------------------
---------------------------------
2d20(poison)+d8(piercing)-4
Total: 19
Details: [[10, 11]21poison, [2]2piercing, [4]4]
---------------------------------
```

## Installation

```
$ pip install dungeondice
$ DISCORD_TOKEN="$TOKEN" dungeondice
```

## Usage

Run the bot, see the `.help` command for more details.

## Roadmap/TODO

- Start using discord views for nicer layout?
- Templating of rolls per player/discord channel
