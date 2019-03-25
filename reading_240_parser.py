from collections import defaultdict

from utils import process_exam_token, read_txt, read_json
UUNRELATED_TEXT = ['微信公众号：张巍⽼老老师', '真经GRE', '阅读机经240篇', '旗舰版']

class Reading240Parser():
    def __init__(self, input_path, file_name, ignore_path, ignore_name, nlp):
        self.input_path = input_path
        self.file_name = file_name
        self.ignore_path = ignore_path
        self.ignore_name = ignore_name
        self.nlp = nlp

    def run(self):
        exam_db, ignore_token_list = self.read_data()
        questions = self.into_question(exam_db)
        tokens_by_part = self.into_tokens(questions, ignore_token_list)
        token_frequency = self.into_frequency(tokens_by_part)

        return token_frequency

    def read_data(self):
        exam_db = read_txt(self.input_path, self.file_name)
        ignore_word_list = read_json(self.ignore_path, self.ignore_name)

        return exam_db, ignore_word_list

    def into_question(self, exam_db):
        '''group list of questions by section'''
        question_by_passages = {}
        passage_questions = []
        passage = []
        passage_head = None
        question = None
        options = []
        for idx, line in enumerate(exam_db):
            if line and line not in UUNRELATED_TEXT:
                # start retrieving data for each section
                if line.lower().startswith("passage"):
                    if passage_head and (passage_questions or question):
                        passage_questions.append({
                            "title": question,
                            "options": options
                        })
                        question_by_passages[passage_head] = {
                            "passage": passage,
                            "questions": passage_questions
                        }
                    # clean sections and question from the previous section
                    passage_questions = []
                    passage_head = line
                    question = None
                    options = []
                    passage = []
                # retrieve question
                elif len(line) > 2:
                    ## question title
                    if (line[0].isdigit() and line[1] == ".") or (line[0:2].isdigit() and line[2] == "."):
                        if question:
                            passage_questions.append({
                                "title": question,
                                "options": options
                            })
                        question = line
                        options = []
                    ## question options
                    elif line[0:2] in ["A.", "B.", "C.", "D.", "E.", "F.", "G.", "H.", "I.", "G.", "K.", "L.", "Ⅰ.", "Ⅱ.", "Ⅲ.", "Ⅳ."]:
                        options.append(line)
                    else:
                        passage.append(line)
            # if idx > 2000:
            #     break
        # # check missing passages
        # set(list(range(240))).difference(set([int(k[8:]) for k in question_by_passages.keys()]))

        return question_by_passages

    def into_tokens(self, questions, ignore_token_list):
        '''group list of words by question part(title, option)'''
        word_list_by_part = {
            "title": [],
            "options": []
        }
        for passage_head, passage_data in questions.items():
            word_list_by_part["title"].extend(
                process_exam_token(" ".join(passage_data["passage"]), self.nlp, ignore_token_list)
            )

            for question in passage_data["questions"]:
                word_list_by_part["title"].extend(
                    process_exam_token(question["title"], self.nlp, ignore_token_list))
                for option in question["options"]:
                    word_list_by_part["options"].extend(process_exam_token(option, self.nlp, ignore_token_list))

        return word_list_by_part

    def into_frequency(self, tokens_by_part):
        '''word frequency by question part'''
        word_freq_by_part_all = {
            "title": defaultdict(int),
            "options": defaultdict(int)
        }
        for part_type, word_list in tokens_by_part.items():
            for word in word_list:
                word_freq_by_part_all[part_type][word] += 1

        for part_type, word_freq in word_freq_by_part_all.items():
            word_freq_by_part_all[part_type] = dict(sorted([(key, freq) for key, freq in word_freq.items()],
                                                      key=lambda x: x[1], reverse=True))

        return word_freq_by_part_all