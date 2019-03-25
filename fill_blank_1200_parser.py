from collections import defaultdict

from utils import process_exam_token, read_txt, read_json

class FillBlank1200Parser():
    def __init__(self, input_path, file_name, ignore_path, ignore_name, nlp):
        self.input_path = input_path
        self.file_name = file_name
        self.ignore_path = ignore_path
        self.ignore_name = ignore_name
        self.nlp = nlp

    def run(self):
        exam_db, ignore_token_list = self.read_data()
        question_by_sections = self.into_question(exam_db)
        word_list_by_section_type = self.into_tokens(question_by_sections, ignore_token_list)
        word_freq_by_section_type, word_freq_by_part_all = self.into_frequency(word_list_by_section_type)

        return word_freq_by_part_all

    def read_data(self):
        exam_db = read_txt(self.input_path, self.file_name)
        ignore_word_list = read_json(self.ignore_path, self.ignore_name)

        return exam_db, ignore_word_list

    def into_question(self, exam_db):
        '''group list of questions by section'''
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

            # if idx > 2000:
            #     break
        return exam_by_section


    def into_tokens(self, exam_by_section, ignore_token_list):
        '''group list of words by sections and question part(title, option)'''
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
                    word_list_by_part["title"].extend(process_exam_token(question["title"], self.nlp, ignore_token_list))
                    for option in question["options"]:
                        word_list_by_part["options"].extend(process_exam_token(option, self.nlp, ignore_token_list))
        word_list_by_section_type[previous_type] = word_list_by_part

        return word_list_by_section_type

    def into_frequency(self, word_list_by_section_type):
        '''word frequency by sections and question part & only by sections'''
        word_freq_by_section_type = {}
        word_freq_by_part_all = {
            "title": defaultdict(int),
            "options": defaultdict(int)
        }
        for section_type, word_list_by_part in word_list_by_section_type.items():
            word_freq_by_part = {}
            for part_type, word_list in word_list_by_part.items():
                word_freq_dict = defaultdict(int)
                for word in word_list:
                    word_freq_dict[word] += 1
                    word_freq_by_part_all[part_type][word] += 1
                word_freq_by_part[part_type] = sorted([(key, freq) for key, freq in word_freq_dict.items()],
                                                      key=lambda x: x[1], reverse=True)
            word_freq_by_section_type[section_type] = word_freq_by_part

        for part_type, word_freq in word_freq_by_part_all.items():
            word_freq_by_part_all[part_type] = dict(sorted([(key, freq) for key, freq in word_freq.items()],
                                                         key=lambda x: x[1], reverse=True))

        return word_freq_by_section_type, word_freq_by_part_all