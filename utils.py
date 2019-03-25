import json
import os
import pprint

def process_exam_token(text, nlp, ignore_tokens):
    doc = nlp(text)
    valid_token = []
    for toc in doc:
        toc_lemma = toc.lemma_ if toc.lemma_ != '-PRON-' else toc.lower_
        if not toc.is_punct and toc_lemma not in ignore_tokens and not toc.is_digit:
            valid_token.append(toc.lower_)

    return valid_token


def output_pprint(data, output_path, file_name):
    with open(os.path.join(output_path, file_name), "w") as ostr:
        pprint.pprint(data, ostr)


def output_json(data, output_path, file_name):
    with open(os.path.join(output_path, file_name), "w") as ostr:
        json.dump(data, ostr)

def read_txt(input_path, file_name):
    with open(os.path.join(input_path, file_name), "r") as istr:
        return [l.strip() for l in istr.readlines()]

def read_json(input_path, file_name):
    with open(os.path.join(input_path, file_name), "r") as istr:
        return json.load(istr)