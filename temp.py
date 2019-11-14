import numpy as np
from math import inf
import argparse
from pathlib import Path
import imageio
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976
import heapq

seasons= ["spring","summer","autumn","winter"]
types=["hair","eye"]

results={
    ("blue","blonde"),
    ("","brunette")
}

eyes={
    "brown":(210,105,30),
    "black":(0,0,0),
    "blue": (57,115,220)
}

hairs={
    "blonde":(255,255,0),
    "black":(0,0,0),
    "brunette":(116,42,15)
}

##http://www.inven.co.kr/board/heroes/2028/28035
skins={
    "apricot":(251,206,177),
    "black":(120,92,69),
    "white":(255,255,255)
}

eye_dic = dict()
hair_dic = dict()
skin_dic = dict()

def find_smallest(rgb,R_avg,G_avg,B_avg):
    tmp_red,tmp_green,tmp_blue = rgb 
    return abs(tmp_red-R_avg) + abs(tmp_green - G_avg) + abs(tmp_blue - B_avg)

def make_label_dict():
    for season in seasons:
        for ttype in types:
            vars()[season+"_"+ttype] = dict()

def output(color_type,dir):
    rgb_img = imageio.imread(dir)

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

    #minimum = inf
    ret =""
    
    if color_type=="eye":
        for color, rgb in eyes.items():
#            flag = minimum
            tmp_r, tmp_g, tmp_b = rgb
            tmp_rgb = sRGBColor(tmp_r, tmp_g, tmp_b, is_upscaled=True)
            lab2 = convert_color(tmp_rgb, LabColor, through_rgb_type=sRGBColor)
            eye_dic[color] = delta_e_cie1976(lab, lab2)
#            minimum = min(minimum,delta_e_cie1976(lab, lab2))
#            if minimum != flag:
#                ret = color

    elif color_type=="hair":
        for color, rgb in hairs.items():
            flag = minimum
            tmp_r, tmp_g, tmp_b = rgb
            tmp_rgb = sRGBColor(tmp_r, tmp_g, tmp_b, is_upscaled=True)
            lab2 = convert_color(tmp_rgb, LabColor, through_rgb_type=sRGBColor)
            hair_dic[color]=delta_e_cie1976(lab, lab2)
#            minimum = min(minimum,delta_e_cie1976(lab, lab2))
            # if minimum != flag:
            #     ret = color

    elif color_type=="skin":
        for color, rgb in skins.items():
#            flag = minimum
            tmp_r, tmp_g, tmp_b = rgb
            tmp_rgb = sRGBColor(tmp_r, tmp_g, tmp_b, is_upscaled=True)
            lab2 = convert_color(tmp_rgb, LabColor, through_rgb_type=sRGBColor)
            skin_dic[color]=delta_e_cie1976(lab, lab2)
            # minimum = min(minimum,delta_e_cie1976(lab, lab2))
            # if minimum != flag:
            #     ret = color
    else:
        print("Wrong color type")
        exit(0)

#    return ret

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("eye")
    parser.add_argument("skin")
    parser.add_argument("hair")
    args = parser.parse_args()

    eye = args.eye+".png"
    skin = args.skin+".png"
    hair = args.hair+".png"

    DATA_DIR =Path("/Users/kimtaegyun/colorization/detect/data/")
    EYE_DIR = DATA_DIR/"eyes"/eye
    SKIN_DIR = DATA_DIR/"skins"/skin
    HAIR_DIR = DATA_DIR/"hairs"/hair
#    eye = output("eye",EYE_DIR)
#    skin = output("skin",SKIN_DIR)
#    hair = output("hair",HAIR_DIR)

    output("eye",EYE_DIR)
    output("skin",SKIN_DIR)
    output("hair",HAIR_DIR)

    print("Real Eye: ",args.eye)
    print("Eye Prediction: ",eye)
    print("Real Hair: ",args.skin)
    print("Skin Prediction: ",skin)
    print("Real Hair: ", args.hair)
    print("Hair Prediction: ",hair)

    priority_queue = []
    for eye_clr, eye_v in eye_dic.items():
        for hair_clr, hair_v in hair_dic.items():
            heapq.heappush(priority_queue,(eye_v+hair_v,(eye_clr,hair_clr)))
            # for skin_clr, skin_v in skin.items():
            #     heapq.heappush(priority_queue,(eye_v+hair_v+skin_v,(eye_clr,hair_clr,skin_clr)))

    while priority_queue:
        diff, comb = heapq.heappop(priority_queue)
        if comb in results:
            print(results[comb])
            print("Color detection error: ",diff)