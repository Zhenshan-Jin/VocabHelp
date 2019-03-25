import spacy
import csv
import os

from fill_blank_1200_parser import FillBlank1200Parser
from reading_240_parser import Reading240Parser

nlp = spacy.load("en_core_web_sm")


def fill_blank_1200():
    file_path = "data/to_text"
    file_name = "GRE填空机经1200题.txt"
    ignore_path = "data"
    ignore_name = "ignore_words.json"

    parser = FillBlank1200Parser(
        input_path=file_path,
        file_name=file_name,
        ignore_path=ignore_path,
        ignore_name=ignore_name,
        nlp=nlp
    )

    return parser.run()

def reading_240():
    file_path = "data/to_text"
    file_name = "GRE阅读机经240篇.txt"
    ignore_path = "data"
    ignore_name = "ignore_words.json"

    parser = Reading240Parser(
        input_path=file_path,
        file_name=file_name,
        ignore_path=ignore_path,
        ignore_name=ignore_name,
        nlp=nlp
    )

    return parser.run()

def merge(fb_1200_freq, r_240_freq):
    output_path = "data/output"
    file_name = "word_freq.csv"

    word_freq = {}
    for word, freq in fb_1200_freq["options"].items():
        word_freq[word] = {
            "filling_1200_title": fb_1200_freq["title"].get(word, 0),
            "filling_1200_option": freq,
            "reading_240_title": r_240_freq["title"].get(word, 0),
            "reading_240_option": r_240_freq["options"].get(word, 0)
        }

    with open(os.path.join(output_path, file_name), mode='w') as ostr:
        csv_writer = csv.writer(ostr, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(["word text", '1200_title', '1200_option', '240_title', '240_option'])

        for word, freq_data in word_freq.items():
            csv_writer.writerow([word, freq_data["filling_1200_title"], freq_data["filling_1200_option"],
                                 freq_data["reading_240_title"], freq_data["reading_240_option"]])


if __name__=="__main__":
    fb_1200_freq = fill_blank_1200()
    r_240_freq = reading_240()

    merge(fb_1200_freq, r_240_freq)

