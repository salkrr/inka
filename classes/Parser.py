from classes.Card import Card
import re


class Parser:
    __tags_prefix = "Tags:"
    __source_prefix = "Source:"
    __question_prefix = ""
    __answer_prefix = ">"

    def __init__(self, file_path):
        self.file_path = file_path

    def collect_cards(self):
        cards_list = []

        # Get all lines from note
        lines_list = self.get_file_lines()

        # Get tags and source
        tags = self.get_tags(lines_list)
        source = self.get_source(lines_list)

        # Forward and backward sides of a card
        forward = ""
        backward = ""

        # We use this boolean to track what last we parsed: question or answer
        previous_is_answer = True

        # This one is needed to correctly add first card
        first_card = True
        for line in lines_list:
            line = line.strip()

            # Skip if line is empty
            if line == "":
                continue

            # Skip line if it's a heading
            if line[0] == "#":
                continue

            # Skip line if it's tags or source
            if line.startswith(self.__tags_prefix) or \
                    line.startswith(self.__source_prefix):
                continue

            # Getting question or answer prefix from the line
            prefix_match = re.match("(\\d+\\.)|(>)", line)

            if previous_is_answer:
                # If there's no prefix than that means
                # that something is wrong with file formatting
                if prefix_match is None:
                    self.print_error_message(line)
                    return

                prefix = line[:prefix_match.regs[0][1]]
                cleaned_line = line[prefix_match.regs[0][1]:].strip()
                # We firstly check if there's continuation for an answer
                if prefix == self.__answer_prefix:
                    backward += "\n" + cleaned_line

                # else it's a new question
                else:
                    # So we should create new card and add it to the list
                    if not first_card:
                        cards_list.append(Card(forward, backward, source, tags))
                    else:
                        first_card = False

                    # And set new forward value
                    forward = cleaned_line
                    previous_is_answer = False
            else:
                # No prefix means that this is the question's line
                if prefix_match is None:
                    forward += "\n" + line
                    continue

                prefix = line[:prefix_match.regs[0][1]]
                cleaned_line = line[prefix_match.regs[0][1]:].strip()
                # If we have answer prefix then it's a first line
                # of the answer for the question we had before
                if prefix == self.__answer_prefix:
                    backward = cleaned_line
                    previous_is_answer = True

                # Question prefix means that we have next question
                # before we got answer to the previous
                else:
                    self.print_error_message(line)

        # Append card if it's the last or the only one in the note
        if forward != "" and previous_is_answer:
            cards_list.append(Card(forward, backward, source, tags))

        return cards_list

    def get_file_lines(self):
        with open(self.file_path, 'r') as note:
            all_lines = list(
                map(lambda l: l.strip(), note.readlines()))

        return all_lines

    def get_tags(self, lines):
        tags = []
        for line in lines:
            # Skip empty lines
            if line.strip() == "":
                continue

            # Get tags
            if line.startswith(self.__tags_prefix):
                tags = line.replace(self.__tags_prefix, "").strip().split(" ")
                break

        return tags

    def get_source(self, lines):
        source = ""
        for line in lines:
            # Skip empty lines
            if line.strip() == "":
                continue

            # Get source
            if line.startswith(self.__source_prefix):
                source = line.replace(self.__source_prefix, "").strip()
                break

        return source

    def print_error_message(self, line_with_error):
        print(f"Something wrong in formatting near line: {line_with_error}")
        print("Closing...")
