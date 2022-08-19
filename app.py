import tweepy
import json
from decouple import config
import requests

BEARER_TOKEN = config('BEARER_TOKEN')

# ID of @disastersbot account
BOT_ID = 1553394058542084096
# API endpoint of the Django app
API_ENDPOINT = 'https://disasteropedia.herokuapp.com/api/add-tweet/'

# Twitter authentication
client = tweepy.Client(BEARER_TOKEN)

try:
    client.get_user(id=BOT_ID)
    print('🟢 Authentication OK')
except:
    print('🔴 ERROR in authentication')


class StreamListener(tweepy.StreamingClient):

    def on_connect(self):
        print('Connected to stream. Listening to tweets')


    def on_data(self, raw_data):
        # Process the raw data by decoding from bytes to string and then de-serializing the string to dict
        data = raw_data.decode("utf-8")
        data = json.loads(data)
        # print(f'Processed data: {data} \n')

        # Extract different data types from the received tweet object
        text = data["data"]["text"]
        created_at = data['data']['created_at']
        mediaType = data["includes"]["media"][0]["type"]

        # Extract the media from tweet object baseed on the media type
        if mediaType == 'photo':
            media = data["includes"]["media"][0]["url"]
            
        elif mediaType == 'video' or mediaType == 'animated_gif':
            contentType = data['includes']['media'][0]['variants'][0]['content_type']
            if contentType == 'video/mp4':
                media = data["includes"]["media"][0]["variants"][0]["url"]
            else:
                media = data["includes"]["media"][0]["variants"][1]["url"]
            
        else:
            media = None
            print('⚠️ ERROR: Unidentified media type:' + mediaType)

        # Extract username and postID from tweet, and then generate the tweet link using that.
        username = data['includes']['users'][0]['username']
        postID = data['data']['id']
        link = f"https://twitter.com/{username}/status/{postID}"

        # Payload to send through API
        api_data = {
            'text' : text,
            'created_at' : created_at,
            'media' : media,
            'mediaType' : mediaType,
            'username' : username,
            'link' : link
        }

        # Make a POST request to the API to add the tweet to database
        try:
            api_call = requests.post(url=API_ENDPOINT, json=api_data)
            print('API response: ', api_call.text, '\n')
        except:
            print('🔴 ERROR: Unable to make a POST request')
        
        
    def on_errors(self, errors):
        print(f"Error while retweeting: {errors}")


    def on_closed(self, response):
        print(f'stream closed! {response}')



stream = StreamListener(
  BEARER_TOKEN,
  wait_on_rate_limit=True
)


# stream.delete_rules([1560480934230904833])    
stream.add_rules(add=tweepy.StreamRule(value='has:media -is:retweet -is:reply -is:quote \
(bio_location:india OR place_country:IN) \
(flood OR floods OR flooded OR flooding OR wildfire OR wildfires OR eartquake OR earthquakes OR tornado OR tornadoes OR tornados \
OR hurricane OR hurricanes OR drought OR droughts OR tsunami OR tsunamis OR landslide OR landslides) \
-crypto -balochistan -pakistan -possible -BJP -congress -donate -PVR -cinema', tag='has:location has:keywords'))

rules = stream.get_rules()
print('ACTIVE FILTERS:', rules)


# Look for tweets with the below mentioned keywords only
stream.filter(expansions=["author_id","attachments.media_keys"], media_fields=["url","variants"], tweet_fields=["created_at"])
