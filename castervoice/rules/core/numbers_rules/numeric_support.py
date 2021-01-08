import re

from text_to_num import text2num
from text_to_num import alpha2digit

from castervoice.lib import settings
from castervoice.lib.actions import Text

def word_number(wn):
    numbers_to_words = {
        0: "zero",
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five",
        6: "six",
        7: "seven",
        8: "eight",
        9: "nine"
    }
    Text(numbers_to_words[int(wn)]).execute()


def numbers_list_1_to_9():
    result = ["one", "torque", "traio", "fairn", "faif", "six", "seven", "eigen", "nine"]
    if not settings.SETTINGS["miscellaneous"]["integer_remap_opt_in"]:
        result[1] = "two"
        result[2] = "three"
        result[3] = "four"
        result[4] = "five"
        result[7] = "eight"
    return result

def numbers_map_1_to_9():
    result = {}
    l = numbers_list_1_to_9()
    for i in range(0, len(l)):
        result[l[i]] = i + 1
    return result

def words_to_num(numdict):
    print("Raw:{} ".format(numdict)) 
    text_list = numdict.replace(r"\number", "").split() # Remove substring "\number" from DPI formatting
    transform_dict = {'one': '1', 'and': '', 'dot':'.', 'oh': 'zero', 'nintey': 'ninety'}
    try:
        #Simple: words to numbers `five hundred sixty three`
        numb = text2num(numdict, "en") 
        print("text2num:{} ".format(numdict)) 
    except ValueError:
        # Reduces complex dictation down to just numerics as a single number 
        for index, word in enumerate(text_list):
            if word in transform_dict.keys():
                text_list[index] = transform_dict[word]
        text = ' '.join(map(str, text_list))
        print("PreProcessed:{} ".format(text)) 
        numb =''.join(re.findall(r"[\d./\-\+]", alpha2digit(text, "en")))
    print("Final: {}".format(numb))
    Text(str(numb)).execute()
