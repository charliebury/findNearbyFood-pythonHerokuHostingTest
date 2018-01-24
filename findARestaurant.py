import json
import httplib2

foursquare_client_id = 'QTLFWDHLVVSQC4QON1E2Q4JFN2AD4PQCFGDUS3XUXXLXXGE3'
foursquare_client_secret = '0TPF2YXDB4B2OJDH2K4GV2HWSLM15IOQNRJUAD5VTNTGTMHQ'
google_api_key = 'AIzaSyBP06-IPKmqnly9njKCfonw13WOHiWcayg'


def getGeocodeLocation(inputString):
    # replace spaces with '+' in URL
    locationString = inputString.replace(" ", "+")
    url = ('https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s' % (locationString, google_api_key))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    latitude = result['results'][0]['geometry']['location']['lat']
    longitude = result['results'][0]['geometry']['location']['lng']
    return (latitude, longitude)


# This function takes in a string representation of a location and cuisine
# type, geocodes the location, and then pass in the latitude and longitude
# coordinates to the Foursquare API
def findARestaurant(mealType, location, howMany):
    latitude, longitude = getGeocodeLocation(location)
    url = ('https://api.foursquare.com/v2/venues/search?client_id=%s&client_secret=%s&v=20130815&ll=%s,%s&query=%s' % (foursquare_client_id, foursquare_client_secret, latitude, longitude, mealType))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result['response']['venues']:

        restaurantInfos = []
        for i in range(howMany):

            # only search for more restaurants if they appear to exist
            if i > len(result['response']['venues']):
                return restaurantInfos
            try:
                restaurant = result['response']['venues'][i]
            except KeyError:
                return restaurantInfos

            venue_id = restaurant['id']
            restaurant_name = restaurant['name']
            restaurant_address = restaurant['location']['formattedAddress']
            # formats the restaurant address into one string
            address = ""
            for i in restaurant_address:
                address += i + " "
            restaurant_address = address

            # Get a  300x300 picture of the restaurant using the venue_id
            url = ('https://api.foursquare.com/v2/venues/%s/photos?client_id=%s&v=20150603&client_secret=%s' % ((venue_id, foursquare_client_id, foursquare_client_secret)))
            photoResult = json.loads(h.request(url, 'GET')[1])
            # Grab the first image
            # if no image available, insert default image url
            if photoResult['response']['photos']['items']:
                firstpic = photoResult['response']['photos']['items'][0]
                prefix = firstpic['prefix']
                suffix = firstpic['suffix']
                imageURL = prefix + "300x300" + suffix
            else:
                imageURL = "N/A"

            restaurantInfo = {'name': restaurant_name, 'address': restaurant_address, 'image': imageURL}
            restaurantInfos.append(restaurantInfo)
        return restaurantInfos
    else:
        return "No Restaurants Found"

if __name__ == '__main__':
    # for testing, can use this example here
    output = findARestaurant("Falafel", "Cairo, Egypt", 5)
