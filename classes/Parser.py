import re

from classes.Card import Card


class Parser:

    def __init__(self, file_path):
        self.file_path = file_path

    def collect_cards(self):
        note_string = self.get_note_string()

        question_sections = self.get_question_sections(note_string)

        cards = []
        for section in question_sections:
            cards.extend(self.get_cards_from_section(section))

        return cards

    def get_cards_from_section(self, section):
        tags = self.get_tags_from_section(section)
        deck_name = self.get_deck_name_from_section(section)

        questions = re.findall(r'^\d+\..+?(?=^>)',
                               section,
                               re.DOTALL | re.MULTILINE)
        # Clean questions from whitespace at the start and the end of string
        questions = list(map(lambda q: re.sub(r'\d+\.', '', q, 1).strip(), questions))

        answers = re.findall(r'(?:>.*?\n)+',
                             section,
                             re.DOTALL | re.MULTILINE)

        # Clean (remove '>' and unnecessary whitespace) answer strings
        answers = list(map(self.clean_answer_string, answers))

        if len(questions) != len(answers):
            raise ValueError(f'Different number of questions and answers in section:\n{section}')

        cards = []
        for question, answer in zip(questions, answers):
            cards.append(Card(question, answer, tags, deck_name))

        return cards

    def get_tags_from_section(self, section):
        match = re.search(r'(?<=^Tags:).*?$',
                          section,
                          re.MULTILINE)
        if not match:
            return []

        tags = match.group().strip().split()
        return tags

    def get_deck_name_from_section(self, section):
        match = re.search(r'(?<=^Deck:).*?$',
                          section,
                          re.MULTILINE)

        if not match or not match.group().strip():
            raise ValueError(f"Couldn't find deck name in:\n{section}")

        deck_name = match.group().strip()
        return deck_name

    def clean_answer_string(self, answer):
        lines = answer.splitlines()
        # Remove first char ('>') and whitespace at the start
        # and the end of each line
        lines = map(lambda l: l[1:].strip(), lines)

        return '\n'.join(lines)

    def get_question_sections(self, note_string):
        return re.findall(r'^---$.+?^---$',
                          note_string,
                          re.MULTILINE | re.DOTALL)

    def get_note_string(self):
        with open(self.file_path, 'r') as note:
            note_string = note.read()

        return note_string
