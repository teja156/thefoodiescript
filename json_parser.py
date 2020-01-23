'''

menus -> menu -> categories -> items -> item -> name,price, -> rating -> total_rating_text,value

'''
import json


def get_name_price(jsondata):
	menu_info = dict()
	menus = json.loads(jsondata)["menus"]

	for i in menus:
		cats = i["menu"]["categories"]

		for cat in cats:
			items = cat["category"]["items"]

			for item in items:
				item_id = item["item"]["id"]
				name = item["item"]["name"]
				price = item["item"]["display_price"]
				rating = 0

				try:
					rating = item["item"]["rating"]["value"]
				except:
					rating = 0

				menu_info[item_id] = {"name":name,"display_price":price,"rating":rating}



	return menu_info



