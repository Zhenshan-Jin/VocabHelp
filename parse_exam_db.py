import spacy
import json
import pprint
from collections import defaultdict
import os

def process_exam_token(text, nlp, ignore_tokens):
    doc = nlp(text)
    valid_token = []
    for toc in doc:
        toc_lemma = toc.lemma_ if toc.lemma_ != '-PRON-' else toc.lower_
        if not toc.is_punct and toc_lemma not in ignore_tokens and not toc.is_digit:
            valid_token.append(toc.lower_)

    return valid_token

nlp = spacy.load("en_core_web_sm")

exam_file_path = "data/to_text/by_difficulty_1.txt"
with open(exam_file_path, "r") as istr:
    exam_db = [l.strip() for l in istr.readlines()]
ignore_token_path = "data/ignore_words.json"
with open(ignore_token_path, "r") as istr:
    ignore_token_list = json.load(istr)

# group list of questions by section
exam_by_section = {}
sections = []
section_head = None
question = None
options = []
processed_line = []
for idx, line in enumerate(exam_db):
    if line:
        # start retrieving data for each section
        if line.startswith("section"):
            if section_head and sections:
                sections.append({
                    "title": question,
                    "options": options
                })
                exam_by_section[section_head] = sections
            # clean sections and question from the previous section
            sections = []
            section_head = line
            question = None
            options = []
        # retrieve question
        elif len(line) > 2:
            ## question title
            if (line[0].isdigit() and line[1] == ".") or (line[0:2].isdigit() and line[2] == "."):
                if question:
                    sections.append({
                        "title": question,
                        "options": options
                    })
                question = line
                options = []
            ## question options
            if line[0:2] in ["A.", "B.", "C.", "D.", "E.", "F.", "G.", "H.", "I.", "G.", "K.", "L."]:
                options.append(line)
    processed_line.append(line)

# group list of words by sections and question part(title, option)
word_list_by_section_type = {}
previous_type = "easy"
word_list_by_part = {
    "title": [],
    "options": []
}
for section_title, section_questions in exam_by_section.items():
    section_type = section_title.split(" ")[-1]
    if section_type not in ["hard", "median", "easy"]:
        section_type = "unknown"
    if section_type != previous_type:
        # question types are repeated in the exam
        if previous_type in word_list_by_section_type:
            for part_type, word_list in word_list_by_part.items():
                word_list_by_section_type[previous_type][part_type].extend(word_list)
        else:
            word_list_by_section_type[previous_type] = word_list_by_part

        word_list_by_part = {
            "title": [],
            "options": []
        }
        previous_type = section_type
    else:
        for question in section_questions:
            word_list_by_part["title"].extend(process_exam_token(question["title"], nlp, ignore_token_list))
            for option in question["options"]:
                word_list_by_part["options"].extend(process_exam_token(option, nlp, ignore_token_list))
word_list_by_section_type[previous_type] = word_list_by_part

# word frequency by sections and question part & only by sections
word_freq_by_section_type = {}
word_freq_by_by_part_all = {
    "title": defaultdict(int),
    "options": defaultdict(int)
}
for section_type, word_list_by_part in word_list_by_section_type.items():
    word_freq_by_part = {}
    for part_type, word_list in word_list_by_part.items():
        word_freq_dict = defaultdict(int)
        for word in word_list:
            word_freq_dict[word] += 1
            word_freq_by_by_part_all[part_type][word] += 1
        word_freq_by_part[part_type] = sorted([(key, freq) for key, freq in word_freq_dict.items()], key=lambda x: x[1], reverse=True)
    word_freq_by_section_type[section_type] = word_freq_by_part

for part_type, word_freq in word_freq_by_by_part_all.items():
    word_freq_by_by_part_all[part_type] = sorted([(key, freq) for key, freq in word_freq.items()], key=lambda x: x[1], reverse=True)

# output data
output_path = "data/output"
with open(os.path.join(output_path, "word_freq_by_section_type.txt"), "w") as ostr:
    pprint.pprint(word_freq_by_section_type, ostr)
with open(os.path.join(output_path, "word_freq_by_part.txt"), "w") as ostr:
    pprint.pprint(word_freq_by_by_part_all, ostr)

with open(os.path.join(output_path, "word_freq_by_section_type.json"), "w") as ostr:
    json.dump(word_freq_by_section_type, ostr)
with open(os.path.join(output_path, "word_freq_by_part.json"), "w") as ostr:
    json.dump(word_freq_by_by_part_all, ostr)