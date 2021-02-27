import requests
from bs4 import BeautifulSoup
import pandas
import argparse
import connect

parser=argparse.ArgumentParser()
parser.add_argument("--page_num_max",help="enter the number of pages to parse",type=int)
parser.add_argument("--dbname",help="enter the number of pages to parse",type=str)
args=parser.parse_args()

oyo_url="https://www.oyorooms.com/hotels-in-bangalore/?page="
page_num_MAX=args.page_num_max
scraped_into_list=[]
connect.connect(args.dbname)

for page_num_max in range(1,page_num_MAX):
    req=requests.get(oyo_url+str(page_num_max))
    content=req.content

    soup=BeautifulSoup(content,"html.parser")

    all_hotels=soup.find_all("div",{"class":"hotelCardsListing"})
    for hotel in all_hotels:
        hotel_dict={}
        hotel_dict["name"]=hotel.find("h3",{"class":"ListingHotelDescription_hotelName"}).text
        hotel_dict["address"]=hotel.find("span",{"itmeprop":"streetaddress"}).text
        hotel_dict["price"]=hotel.find("span",{"class":"ListingPrice_finalPrice"}).text

        try:
            hotel_dict["rating"]=hotel.find("span",{"class":"hotelRating_ratingSummary"}).text
        except AttributeError:
            pass
        
        parent_amenities_element=hotel.find("div",{"class":"amenityWrapper"})

        amenities_list=[]

        for amenity in parent_amenities_element.find_all("div",{"class":"amenityWrapper__amenity"}):
            amenities_list.append(amenity.find("span",{"class": "d-body-sm"}).text.strip())

        hoteldict["amenities"]= ', '.join(amenities_list[:-1])

        scraped_into_list.append(hotel_dict)
        connect.insert_into_table(args.dbname,tuple(hotel_dict.values()))
        
dataFrame=pandas.DataFrame(scraped_into_list)
dataFrame.to_csv("oyo.csv")

connect.get_hotel_info(args.dbname)