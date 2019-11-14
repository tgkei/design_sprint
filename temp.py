import numpy as np
from math import inf
from pathlib import Path
import imageio
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976
import heapq

ground_truth = {
    "1": "SPRING",
    "2": "AUTUMN",
    "3": "Winter",
    "4": "AUTUMN",
    "5": "SUMMER",
    "6": "SPRING",
    "7": "WINTER",
    "8": "WINTER",
    "9": "WINTER",
    "10": "WINTER"
}
seasons= ["spring","summer","autumn","winter"]
types=["hair","eye"]

results={
    ("blue","blonde"),
    ("","brunette")
}

# ##http://www.inven.co.kr/board/heroes/2028/28035

eye_labels = dict()
hair_labels = dict()

eye_dic = dict()
hair_dic = dict()
skin_dic = dict()

def calc_lab(img_dir):
    rgb_img = imageio.imread(img_dir)

    Red = []
    Green = []
    Blue = []
    for x in rgb_img:
        for y in x:
            Red.append(y[0])
            Green.append(y[1])
            Blue.append(y[2])
    
    R_avg = sum(Red) / len(Red)
    G_avg = sum(Green) / len(Green)
    B_avg = sum(Blue) / len(Blue)

    if R_avg <0 or R_avg>255 or G_avg < 0 or G_avg>255 or B_avg < 0 or B_avg > 255:
        print("Wrong RGB")
        exit(0)
    
    rgb = sRGBColor(R_avg, G_avg, B_avg, is_upscaled=True)
    lab = convert_color(rgb, LabColor, through_rgb_type=sRGBColor)
    return lab

def make_label_dict():
    directory = Path("/Users/kimtaegyun/colorization/detect/data/label")

    for season in seasons:
        for ttype in types:
            label = season+"_"+ttype+".png"
            img_dir = directory/label
            if ttype == "hair":
                hair_labels[season] = calc_lab(img_dir)
            else:
                eye_labels[season] = calc_lab(img_dir)    

def output(color_type,img_dir):
    lab = calc_lab(img_dir)

    if color_type=="eye":
        for season, lab2 in eye_labels.items():
            eye_dic[season] = delta_e_cie1976(lab, lab2)
    elif color_type=="hair":
        for season, lab2 in hair_labels.items():
            hair_dic[season] = delta_e_cie1976(lab, lab2)
    else:
        print("Wrong color type")
        exit(0)

if __name__=='__main__':
    print("===================RESULT===================")
    correct = 0 
    wrong = 0
    DATA_DIR =Path("/Users/kimtaegyun/colorization/detect/data/test")
    for T in range(1,11):
        eye = "eye/"+str(T)+".jpg"
        hair = "hair/"+str(T)+".jpg"
        EYE_DIR = DATA_DIR/eye
        HAIR_DIR = DATA_DIR/hair

        make_label_dict()

        output("eye",EYE_DIR)
        output("hair",HAIR_DIR)

        priority_queue = []
        for eye_clr, eye_v in eye_dic.items():
            for hair_clr, hair_v in hair_dic.items():
                heapq.heappush(priority_queue,(eye_v+hair_v,(eye_clr,hair_clr)))

        while priority_queue:
            diff, comb = heapq.heappop(priority_queue)
            if comb[0] == comb[1]:
                print("Case {}".format(T))
                print("\tGT: ", ground_truth[str(T)].lower())
                print("\tResult:",comb[0])
                print("\tDiff:",diff)
                if ground_truth[str(T)].lower() == comb[0]:
                    correct += 1
                else:
                    wrong += 1
                break
    print("Correct: ",correct)
    print("Wrong: ", wrong)
    print("============================================")