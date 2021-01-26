Automatically add your Markdown flashcards to Anki.

## Installation

- Install [AnkiConnect](https://github.com/FooSoft/anki-connect)
- Install **inka**: `python3 -m pip install inka --upgrade`

## What is this?

**Inka** automatically adds cards from your *Markdown* notes to [Anki](https://apps.ankiweb.net/). This allows you to write cards in the same file with your notes, or write your notes as cards.

You create cards using *Markdown* syntax:

```markdown
1. Question?

> Answer

2. Another question?

![](path/to/image.png)

> Answer
> With Image
>
> ![](path/to/another/image.png)
```

Every question starts with number followed by period (e.g. `1.`, `2.`) and every answer starts with `>`.

> Only basic (question-answer) cards are supported.

## Features

- Cards are automatically added to your Anki deck
- Specify a deck and tags for cards
- Add images to cards

## Usage

### Creating cards

In order for the program to be able to separate cards from all the rest of the text in the file, you need to enclose them between two `---`: 

```markdown
---

Deck: Default 

Tags: learning life-questions

1. What is the answer to the Ultimate Question of Life, the Universe, and Everything?

> 42

2. If it walks like a duck and it quacks like a duck, then what is it? 

> It is a duck!

---
```

> This means that you can't use the `---` syntax anywhere else in the file for **inka** to work properly. 

You can create any number of such blocks in the file.

Inside the block, it is necessary to specify the name of the deck to which the cards will be added, and also (optionally) you can specify tags for the cards.
The deck name is written after `Deck:`, and tags for all cards after `Tags:` with spaces between each tag. 

### Adding cards to Anki

Start **Anki** and use this command in your terminal:

```commandline
inka path/to/file/with_cards.md
```

You can specify several files at once:

```commandline
inka path/to/file/with_cards.md path/to/another/cards.md
```
