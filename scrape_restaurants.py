import json
import requests
import threading
import sys
import time
import ast
from bs4 import BeautifulSoup



res_per_page = 30
all_cookies = dict()
headers = dict()
headers['User-Agent']= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:71.0) Gecko/20100101 Firefox/71.0'
zomato_url = "https://zomato.com"
zomato = list()
sorted_zomato = list()
subzone_url = ""
stop_scraping = False
categories = list()

proxies = {"http" : "127.0.0.1:8080","https" : "127.0.0.1:8080"}


def get_cookies_zomato(cfile):
    f = open(cfile,"r")
    cookies = f.read()
    f.close()
    cookies = json.loads(cookies)

    #get name and value of cookie
    for i in range(0,len(cookies)):
        name = cookies[i]['name'].encode("utf-8")
        value = cookies[i]['value'].encode("utf-8")
        all_cookies[name] = value
    
	#print(all_cookies)


def connect_zomato(city):
    global subzone_url

    r = requests.get(zomato_url+"/%s/order"%city,headers=headers,cookies=all_cookies)
    print(r.status_code)

    f = open("output.html","wb")
    f.write(r.text.encode('utf-8'))
    f.close()

    #Check if cookies are valid
    if "Log out" in r.text:
        print("Logged in!")
    else:
        print("Login Fail - Please change cookies!")
        sys.exit(0)    

    #get URL for other pages
    soup = BeautifulSoup(r.text,"html.parser")
    subzone_url = soup.find_all("a",{'class':'paginator_item'})[0].get("href")
    
    return subzone_url



def calculate_score(rating,offer_value):
    rating_score = (rating/0.1) * 1
    offer_score = offer_value * 2
    
    return (rating_score + offer_score)



def scrape_zomato(pg_no):
    global stop_scraping
    global categories
    
    #Check scraping status
    if(stop_scraping):
        return
    
    r = requests.get(zomato_url+subzone_url[0:len(subzone_url)-1]+str(pg_no),headers=headers,cookies=all_cookies)
    soup = BeautifulSoup(r.text,"html.parser")
    
    #First get number of restaurants on the page
    restaurants = soup.find_all("div",{'class':'search-o2-card'})
    
    
    print("No. of Restaurants on page %d - %d"%(pg_no,len(restaurants)))
    

    #If no restaurants on a page, it means we've reached end.
    if(len(restaurants)<res_per_page):
        stop_scraping = True
    
    for restaurant in restaurants:
        #First check if restaurant is offline
        if(restaurant.findChildren("div",{'class':'order_search_button'})):
            continue
        
        #Get the name of the restaurant
        res_name = restaurant.findChildren("a",{'class':'result-order-flow-title'})[0].text.strip()
        #print(res_name)
        
        
        #Get restaurant ID
        res_id = restaurant.get("data-res_id")

        #Get category
        res_category=restaurant.findChildren("div",{'class':'grey-text'})[0].text.strip()
        
        #Get the rating of the restaurant
        res_rating = restaurant.findChildren("div",{'class':'rating-popup','data-res-id':res_id})[0].text.strip()

        try:
            res_rating = float(res_rating)
        except ValueError:
            res_rating = 0.0
        
        
        #Get the offer of restaurant
        res_offer = "No offer"
        res_offer_value = 0
        if(restaurant.findChildren("span",{'class':'offer-text'})):
            res_offer = restaurant.findChildren("span",{'class':'offer-text'})[0].text.strip()
            #print(res_offer)

            if u"\u0024" in res_offer: #rupee symbol
                res_offer_value = res_offer[res_offer.index(u"\u0024")+1:res_offer.index(" ")]
            elif "%" in res_offer:
                res_offer_value = int((res_offer[0:res_offer.index('%')]).strip())
        
        
        res_info = dict()
        
        res_score = calculate_score(rating=res_rating,offer_value = res_offer_value)
        
        res_info['res_id'] = res_id
        res_info['res_rating'] = res_rating
        res_info['res_category'] = res_category
        res_info['res_name'] = res_name
        res_info['res_offer'] = res_offer
        res_info['res_score'] = res_score
        

        #If specific categories are submitted as input
        if((len(categories)>0)):
            cats = res_category.strip().split(',')
            for cat in cats:
                if(cat.lower() in categories):
                    zomato.append(res_info)
                    break

        else:
            zomato.append(res_info)


def go_scraping(city,cfile,cats):
    global categories
    categories = list(cats)
    get_cookies_zomato(cfile)
    subzone_url = connect_zomato(city) #Get subzone_id so that we can frame other pages links
    
    #Now start scraping. Each page, one thread
    k=1
    threads = list()
    for i in range(0,2):
        t = threading.Thread(target=scrape_zomato,args=(k,))
        t.daemon= True
        k = k + 1
        threads.append(t)
        if(stop_scraping):
            print("Stopping Scraping")
            break
        t.start()
        
    
    for i in threads:
        i.join()

        
    #contains only active/online restaurants  
    sorted_zomato = sorted(zomato,key = lambda i: i['res_score'],reverse=True)


    '''

    k=1
    for i in sorted_zomato:
        print("Res id - %s\nName - %s\nOffer - %s\nRating - %f\nScore - %f\nCategory - %s"%(i['res_id'],i['res_name'],i['res_offer'],i['res_rating'],i['res_score'],i['res_category']))
        print("\n\n")
        k=k+1

        if(k==10):
            break

        
    print("Total Active restaurants - %d"%len(sorted_zomato))

    '''

    return sorted_zomato


