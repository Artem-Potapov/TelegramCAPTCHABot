import os
import json
script_directory = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
#make sure code doesn't fail because of terminal issues


if not os.path.exists(f"{script_directory}/captchas.json"):
    file = open(f"{script_directory}/captchas.json", "w+", encoding="utf-8")
    truncate_file = False
    captchas = {}
else:
    file = open(f"{script_directory}/captchas.json", "r+", encoding="utf-8")
    truncate_file = True
    captchas: dict[str, list] = json.load(file)


mode = int(input("1 for creating captchas\n2 for editing captchas\n3 to list all captchas\n>>>"))
if mode == 1:
    while True:
        emj = input("Insert the emoji:\n>>>").strip().replace("\n", "")
        if emj.lower() == "" or emj.lower() == "end" or emj.lower() == "stop" or emj.lower() == "стоп":
            break

        stop = False
        if emj in captchas.keys():
            print("Warning: emoji exists!")
            print(f"Current answers: {captchas[emj]}")
            ovw = input("If you want to still overwrite, enter in 'ovw'\n>>>").strip()
            if ovw.lower() != "ovw":
                stop = True
                break

        if stop:
            continue
        captchas[emj] = []

        stopper = True
        while stopper:
            desc = input("Insert answers:\n>>>").strip().replace("\n", "")
            if desc == "":
                stopper = False
            desc = desc.split()
            for i in desc:
                if i.lower() == "stop" or i.lower() == "end" or i.lower() == "стоп":
                    stopper = False
                    break
                captchas[emj].append(i)

        cont = False if emj.lower() == "end" or emj.lower() == "стоп" else True

    if truncate_file:
        file.seek(0)
        file.truncate(0)
    json.dump(captchas, file, indent=2, ensure_ascii=False)
file.close()
