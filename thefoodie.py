import getopt
import sys
import scrape_restaurants
import scrape_dishes

cookie_fname = "cookies.json"
city=""
dishes_list = list()
categories_list = list()
ignore_offer_above_limit = False
argv = sys.argv[1:]


try:
	opts,rem = getopt.getopt(argv,'c',['dishes=','categories=','ignore-offer-above-limit','help','city='])
	#print("Options : ",opts)
except getopt.GetoptError:
	print("Run,\n python thefoodie.py --help\nto see the help screen")


for opt,arg in opts: 
	if(opt=='--help'):
		print("Help screen")

	if(opt=='-c'):
		cookie_fname = arg
		if  not(".json" in cookie_fname):
			print("File must be a .json file!")
			sys.exit()

	if(opt=='--dishes'):
		dishes_list = arg.split(',')

	if(opt=='--categories'):
		categories_list = arg.lower().split(',')

	if(opt=='--ignore-offer-above-limit'):
		ignore_offer_above_limit = True

	if(opt=="--city"):
		city = arg.lower()

if(city==""):
	print("You need to mention a city with --city")
	sys.exit(0)

if(len(dishes_list)>0 and len(categories_list)>0):
	print("Either use --dishes or --categories, not both at once.")
	sys.exit(0)

restaurants = scrape_restaurants.go_scraping(city=city,cfile=cookie_fname,cats=categories_list)

if(len(categories_list)>0):
	print("Best Restaurants matching - %s : "%str(categories_list))
	for i in restaurants:
		print("\nRes id - %s\nName - %s\nOffer - %s\nRating - %f\nScore - %f\nCategory - %s"%(i['res_id'],i['res_name'],i['res_offer'],i['res_rating'],i['res_score'],i['res_category']))
        print("\n\n")
else:
	print("Best restaurants around you : ")
	for i in restaurants:
		print("\nRes id - %s\nName - %s\nOffer - %s\nRating - %f\nScore - %f\nCategory - %s"%(i['res_id'],i['res_name'],i['res_offer'],i['res_rating'],i['res_score'],i['res_category']))
        print("\n\n")


print("Total restaurants - %d"%len(restaurants))


if(len(dishes_list)>0):
	#print(dishes_list)
	dishes_results = scrape_dishes.go_scraping(cfname=cookie_fname,restaurants=restaurants,dishes=dishes_list)

	for dish in dishes_results:
		print("Best dishes for %s :\n"%dish)
		#Sort dishes according to score
		#print("\n\n")
		#print(dishes_results)
		sorted_dish_results = sorted(dishes_results[dish],key = lambda i: i['dish_score'],reverse=True)

		k = 0
		for i in sorted_dish_results:
			print("Restaurant - %s"%i['res_name'])
			print("Restaurant rating - %s"%i['res_rating'])
			print("Restaurant offer - %s"%i['res_offer'])
			print("Dish name - %s"%i['dish_name'])
			print("Dish initial price - %s"%i['dish_init_price'])
			print("Dish final price - %s"%i['dish_final_price'])
			print("Dish rating - %s"%i['dish_rating'])
			print("Dish score - %s"%i['dish_score'])

			print("\n\n")
			k = k+1
			if(k==10):
				break







