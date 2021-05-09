# inka

<a href="https://www.buymeacoffee.com/lazyvoid" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" width="170px" height="46px"></a>

[![Downloads](https://pepy.tech/badge/inka)](https://pepy.tech/project/inka)
[![PyPi](https://img.shields.io/pypi/v/inka)](https://pypi.org/project/inka)
[![Tests CI](https://img.shields.io/github/workflow/status/lazy-void/inka/Tests/main)](https://github.com/lazy-void/inka/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Codecov](https://codecov.io/gh/lazy-void/inka/branch/main/graph/badge.svg?token=9wW5SJ9uLL)](https://codecov.io/gh/lazy-void/inka)

Automatically add your Markdown flashcards to [Anki](https://apps.ankiweb.net/).

- [Installation](#installation)
    - [Requirements](#requirements)
- [Why](#why)
- [Features](#features)
- [Usage](#usage)
    - [Creating Cards](#creating-cards)
    - [Adding Cards to Anki](#adding-cards-to-anki)

## Installation

`python3 -m pip install inka --upgrade`

### Requirements

- [Python](https://www.python.org/) >= 3.7
- [AnkiConnect](https://github.com/FooSoft/anki-connect) plugin

## Why

I've been using Anki for a long time, and at some point my notes turned into just lists of question/answer pairs, from
which I then created Anki cards. The process of creating flashcards in Anki took a long time, so I decided to write a
Python script to automate it. With more and more features added, the script has evolved into the command-line tool you
can see now.

**inka** allows you to use full power of Markdown when creating flashcards. The program is also extensively tested.

## Features

- Cards are automatically added to your Anki deck
- [Basic and Cloze note types support](https://github.com/lazy-void/inka/wiki/Creating-cards#frontback-notes)
- [Synchronization of changes with Anki](https://github.com/lazy-void/inka/wiki/Synchronization-with-Anki)
- [Configuration via config file](https://github.com/lazy-void/inka/wiki/Config)
- [Images support](https://github.com/lazy-void/inka/wiki/Creating-cards#images)
- [MathJax support](https://github.com/lazy-void/inka/wiki/Mathjax)
- [Code highlight](https://github.com/lazy-void/inka/wiki/Code-highlight)
- [Hashing (for better performance)](https://github.com/lazy-void/inka/wiki/Hashing)

## Usage

### Creating Cards

In order for the program to be able to separate cards from all the rest of the text in the file, you need to enclose
them between two `---`:

```markdown
---

Deck: Life Questions

Tags: learning life-questions

1. What is the answer to the Ultimate Question of Life, the Universe, and Everything?

> 42

2. If it {looks like a duck, swims like a duck, and quacks like a duck}, then it is a {duck}.

---
```

You can create any number of such sections in the file.

> :warning: This means that you should avoid using the `---` syntax anywhere else in the file for **inka** to work correctly.
> There are exceptions, and you can read about them in [documentation](https://github.com/lazy-void/inka/wiki/Creating-cards#i-want-to-use-----for-other-purposes).

Inside the section, you can specify the name of the deck to which the cards will be added, and tags for the cards. If
deck name isn't specified, then the one from the [config](https://github.com/lazy-void/inka/wiki/Config) is
used (`Default` by default). The deck name is written after `Deck:`, and tags for all cards after `Tags:` with spaces
between each tag.

Two types of notes are supported:

- **Front/Back**: every question starts with number followed by period (e.g. `1.`, `2.` - Markdown ordered list syntax)
  and every line of the answer starts with `>` (Markdown quote syntax). Question and answer can span multiple lines.
- **Cloze**: same as Front/Back notes, Cloze notes start with number followed by period (Markdown ordered list syntax).
  **inka** supports three versions of syntax for cloze deletions:
    - Anki syntax: `{{c1::hidden text}}`
    - Short explicit syntax: `{1::hidden text}` or `{c1::hidden text}`
    - Short implicit syntax: `{hidden text}`

More info and examples on the [creating cards](https://github.com/lazy-void/inka/wiki/Creating-cards) documentation
page.

### Adding Cards to Anki

**inka** will create custom note types for **Front/Back** and **Cloze** notes. If you want to use different ones, you
can change note types in the [config](https://github.com/lazy-void/inka/wiki/Config).

Add cards from the file:

```commandline
inka collect path/to/cards.md
```

Or from all *Markdown* files in a directory:

```commandline
inka collect path/to/directory
```

You can also pass multiple paths at once:

```commandline
inka collect path/to/cards.md path/to/folder
```

You can find more information on the [documentation page](https://github.com/lazy-void/inka/wiki/Adding-cards-to-Anki).
