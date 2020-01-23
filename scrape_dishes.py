import json
import requests
import threading
import sys
import time
import ast
from bs4 import BeautifulSoup
import json_parser
import re


headers = dict()
headers['User-Agent']= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:71.0) Gecko/20100101 Firefox/71.0'
headers['Host']= 'www.zomato.com'
headers['Origin']= 'https://www.zomato.com'

all_cookies = dict()
dish_info_byname = dict()
prev_resp = ""




def get_cookies_zomato(cfname):
    f = open(cfname,"r")
    cookies = f.read()
    f.close()
    cookies = json.loads(cookies)

    #get name and value of cookie
    for i in range(0,len(cookies)):
        name = cookies[i]['name'].encode("utf-8")
        value = cookies[i]['value'].encode("utf-8")
        all_cookies[name] = value



def calculate_dish_score(final_price,final_rating):
    final_price_score = final_price * (-0.1)
    final_rating_score = final_rating * 10

    return (final_price_score + final_rating_score)


def calc_final_price(restaurant_offer,dish_price):
    #Now let's calculate final price of dish

    #First find the type of offer

    offer_value = 0
    above_value = 0

    if "%" in restaurant_offer:
        offer_value = int(re.match(".*%",restaurant_offer).group(0)[0:-1])

        if "above" in restaurant_offer:
            
            #restaurant_offer[restaurant_offer.index("above")+len("above")+2:len(restaurant_offer)]
            #print(restaurant_offer[restaurant_offer.index("above")+len("above")+2:len(restaurant_offer)-1])
            #above_value = int(restaurant_offer[restaurant_offer.index("above")+len("above")+2:len(restaurant_offer)-1])
            above_value = int(restaurant_offer.strip()[restaurant_offer.rindex(" ")+2:-1])
            

            if(dish_price>above_value):
                dish_price = dish_price - (float(offer_value)/100.0 * float(dish_price))
                

        else:
            dish_price = dish_price - (float(offer_value)/100.0 * float(dish_price))
        

        return dish_price


    elif u"\u0024" in restaurant_offer:
        offer_value = int(re.match(".*%",restaurant_offer).group(0)[0:-1])
        if "above" in restaurant_offer:
            above_value = int(restaurant_offer.strip()[restaurant_offer.rindex(" ")+2:-1])

            if(dish_price>above_value):
                dish_price = dish_price - (float(offer_value)/100.0 * float(dish_price))

        else:
            dish_price = dish_price - (float(offer_value)/100.0 * float(dish_price))

        return dish_price

    return dish_price


def get_restaurant_menu(restaurant):
    csrf_token = all_cookies['csrf']
    data = dict()
    res_menu = dict()

    data["res_id"] = restaurant["res_id"]
    data["case"] = "getdata"
    data["csrfToken"] = csrf_token

    r = requests.post("https://www.zomato.com/php/o2_handler.php",headers=headers,cookies=all_cookies,data=data)
    menu_info = json_parser.get_name_price(r.text)


    for i in menu_info:
        item_info = dict()
        item_info["dish_name"] = menu_info[i]["name"]
        item_info["dish_price"] = menu_info[i]["price"]
        item_info["dish_rating"] = menu_info[i]["rating"]

        if(restaurant['res_name']=='Ice Park'):
            print(menu_info[i]["name"])
    print(len(menu_info))

def dishes_zomato(restaurant,dishes):
    dish_info = dict()

    for dish in dishes:
        #Now check if dish exists


        if(dish in dish_info_byname):
            pass
        else:
            dish_info_byname[dish] = list()
        words = dish.split(' ')
        regex = "^.*"
        for word in words:
            regex = regex + word + ".*"
        regex = regex + "$"
  

        #csrf = r.text[r.text.index("zomato.csrft"):r.text.index(";",r.text.index("zomato.csrft"))]
        #csrf_token = csrf[csrf.index('"')+1:len(csrf)-1]

        csrf_token = all_cookies['csrf']

        #print("CSRF cookie - %s"%csrf_token)


        data = dict()

        data["res_id"] = restaurant['res_id']
        data["case"] = "getdata"
        data["csrfToken"] = csrf_token

        r = requests.post("https://www.zomato.com/php/o2_handler.php",headers=headers,cookies=all_cookies,data=data)


        menu_info = json_parser.get_name_price(r.text)

        for i in menu_info:
            name = menu_info[i]["name"]
            price = menu_info[i]["display_price"]
            rating = menu_info[i]["rating"]

            

            #print("Checking %s in restaurant %s"%(regex,restaurant['res_name']))

            if(re.match(regex,name,re.IGNORECASE)):
                #Match found

                print("Found %s in %s - %s"%(dish,restaurant['res_name'],name))
                final_rating = (restaurant['res_rating'] + rating)/2
                final_price = calc_final_price(restaurant_offer=restaurant['res_offer'],dish_price=price)
                dish_score = calculate_dish_score(final_price=final_price,final_rating=final_rating)
                dish_info = dict()

                dish_info['res_name'] = restaurant['res_name']
                dish_info['res_id'] = restaurant['res_id']
                dish_info['res_offer'] = restaurant['res_offer']
                dish_info['dish_name'] = name
                dish_info['res_rating'] = restaurant['res_rating']
                dish_info['dish_rating'] = rating
                dish_info['dish_init_price'] = price
                dish_info['dish_final_price'] = final_price
                dish_info['dish_score'] = dish_score


                #print(dish_info)
                #print("\n")


                dish_info_byname[dish].append(dish_info)
    




def go_scraping(cfname,restaurants,dishes):
    get_cookies_zomato(cfname)
    threads = list()


    for restaurant in restaurants:
        #Each restaurant, one thread
        t = threading.Thread(target=dishes_zomato,args=(restaurant,dishes,))
        t.daemon = True
        threads.append(t)
        time.sleep(1) #Don't rush, you may get banned.
        t.start()
        #dishes_zomato(restaurant,dishes)

    for i in threads:
        i.join()


    #print(dish_info_byname)
    return dish_info_byname











