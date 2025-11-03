import random
from collections.abc import Sequence

from key_presets import letters
import json

file = open("captchas.json", "r", encoding="utf-8")
list_captcha: dict[str, list] = json.load(file)
file.close()

def distance(str1: str, str2: str|Sequence[str]):
    if isinstance(str2, (list, tuple)):
        l = []
        print(f"Чекаю капчей: ", end=" ")
        for tmp in str2:
            e = distance(str1, tmp)
            print(f"{str1} и {tmp} - {e}")
            l.append(e)
        return min(l)
    #clean from junk
    junk = ['!', '(', ')', '_', '-', '+', '=', '/', '\\', "'"]
    for piece in junk:
        str1.replace(piece, "")
        str2.replace(piece, "")

    #we need to economy processing power, so just check with 1-hole
    if len(str1) - 1 == len(str2):
        for i in range(len(str1) + 1):
            newstr = str1[0:i] + str1[i+1:]
            if newstr == str2:
                return 1
    elif len(str1) == len(str2) - 1:
        for i in range(len(str2) + 1):
            newstr = str2[0:i] + str2[i+1:]
            if newstr == str1:
                return 1
    elif len(str1) == len(str2):
        dist = 0
        for i in range(len(str1)):
            if str1[i] != str2[i]:
                let = str1[i]
                try:
                    if str2[i] in letters[let].keys():
                        dist += 1
                    else:
                        dist += 3
                except KeyError:
                    return 15556
        return dist
    return 15556


def generate_captcha() -> (str, list[str]):
    emojis = tuple(list_captcha.keys())
    print(emojis)
    chosen = random.choice(emojis)
    answers = list_captcha[chosen]
    print(chosen, answers)
    return chosen, answers



def generate_key_error_map():
    uwu1 = [['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
           ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
           ['z', 'x', 'c', 'v', 'b', 'n', 'm']]
    uwu2 = [['й', 'ц', 'у', 'к', 'е', 'н', 'г', 'ш', 'щ', 'з', 'х', 'ъ'],
            ['ф', 'ы', 'в', 'а', 'п', 'р', 'о', 'л', 'д', 'ж', 'э'],
            ['я', 'ч', 'с', 'м', 'и', 'т', 'ь', 'б', 'ю']]


    pleni = uwu2

    for numrow, row in enumerate(pleni):
        for numkey, key in enumerate(row):
            neighbors = {}

            if numkey + 2 <= len(row): #right
                neighbors[row[numkey+1]] = 1
            if numkey - 1 >= 0: #left
                neighbors[row[numkey-1]] = 1
            if numrow - 1 >= 0: #up
                neighbors[pleni[numrow - 1][numkey]] = 1
            if numrow + 1 <= 2: #down
                try:
                    neighbors[pleni[numrow + 1][numkey]] = 1
                except IndexError:
                    ...

            if numrow - 1 >= 0 and numkey + 2 <= len(row): # up + right
                neighbors[pleni[numrow - 1][numkey + 1]] = 1
            if numrow - 1 >= 0 and numkey - 1 >= 0: # up + left
                neighbors[pleni[numrow - 1][numkey - 1]] = 1
            if numrow + 1 <= 2 and numkey - 1 >= 0: # down + left
                try:
                    neighbors[pleni[numrow + 1][numkey - 1]] = 1
                except IndexError:
                    ...
            # down + right
            try:
                neighbors[pleni[numrow + 1][numkey + 1]] = 1
            except IndexError:
                ...

            neighbors["else"] = 3
            print(f"'{key}' : {neighbors},")
#end of function

async def async_range(start: int, stop: int, step: int):
    while start < stop:
        yield start
        start += step


print(distance("дельфини", ["дельфин", "dolphin"]))