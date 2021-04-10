Automatically add your Markdown flashcards to [Anki](https://apps.ankiweb.net/).

## Installation

- Install [AnkiConnect](https://github.com/FooSoft/anki-connect) plugin
- Install **inka**: `python3 -m pip install inka --upgrade`

## What is this?

**inka** automatically adds cards from your *markdown* notes to [Anki](https://apps.ankiweb.net/). This allows you to
write cards in the same file with your notes, or write your notes as cards.

Cards are created using plain *markdown* syntax:

```markdown
1. Question?

> Answer

2. Another question?

Second line of question.

> Answer
> With Image
>
> ![](path/to/another/image.png)
```

Every question starts with number followed by period (e.g. `1.`, `2.`) and every line of the answer starts with `>`.

> Only basic (front/back) cards are supported.

## Features

- Cards are automatically added to your Anki deck
- Specify a deck and tags for cards
- Add images to cards
- [Synchronization of changes with Anki](https://github.com/lazy-void/inka/wiki/Synchronization-with-Anki)
- [Configuration via config file](https://github.com/lazy-void/inka/wiki/Config)
- [Code highlight](https://github.com/lazy-void/inka/wiki/Code-highlight)
- [MathJax support](https://github.com/lazy-void/inka/wiki/Mathjax)

## Usage

### Creating cards

In order for the program to be able to separate cards from all the rest of the text in the file, you need to enclose
them between two `---`:

```markdown
---

Deck: Default

Tags: learning life-questions

1. What is the answer to the Ultimate Question of Life, the Universe, and Everything?

> 42

2. If it looks like a duck, swims like a duck, and quacks like a duck, then what is it?

> It is a duck!
> ![duck](duck_image.png)

---
```

> :warning: This means that you can't use the `---` syntax anywhere else in the file for **inka** to work properly.

You can create any number of such sections in the file.

Inside the section, you can specify the name of the deck to which the cards will be added, and tags for the cards. If
deck name isn't specified, then the one from the [config](https://github.com/lazy-void/inka/wiki/Config) is
used (`Default` by default). The deck name is written after `Deck:`, and tags for all cards after `Tags:` with spaces
between each tag.

### Adding cards to Anki

Add cards from the file:

```commandline
inka collect path/to/cards.md
```

Or from all *markdown* files in a directory:

```commandline
inka collect path/to/directory
```

You can also pass multiple paths at once:

```commandline
inka collect path/to/cards.md path/to/folder
```

More info on the [documentation page](https://github.com/lazy-void/inka/wiki/Adding-cards-to-Anki)
