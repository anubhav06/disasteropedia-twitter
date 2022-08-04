import tweepy
import json
import time
import sys
from decouple import config

# CONSUMER_KEY = config('CONSUMER_KEY')
# CONSUMER_SECRET = config('CONSUMER_KEY_SECRET')
# ACCESS_TOKEN = config('ACCESS_TOKEN')
# ACCESS_TOKEN_SECRET = config('ACCESS_TOKEN_SECRET')
BEARER_TOKEN = config('BEARER_TOKEN')

# ID of @disastersbot account
BOT_ID = 1553394058542084096
# Time between retweeting a tweet again. Set to 120 in accordance with the twitter api requests limits
SLEEP_TIME = 120

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
        print(f"Data recieved {raw_data} \n")
        # Process the raw data by decoding from bytes to string and then de-serializing the string to dict
        data = raw_data.decode('utf-8')
        data = json.loads(data)
        print(f'Processed data: {data} \n')
        text = data['data']['text']
        print(f'Data text: {text} \n')

        
    def on_errors(self, errors):
        print(f"Error while retweeting: {errors}")


    def on_closed(self, response):
        print(f'stream closed! {response}')



stream = StreamListener(
  BEARER_TOKEN,
  wait_on_rate_limit=True
)


# stream.delete_rules([1555245925081448448])    
stream.add_rules(add=tweepy.StreamRule(value='has:media -is:retweet -is:reply (bio_location:india) \
(flood OR floods OR wildfire OR wildfires OR earthquake OR earthquakes OR tornado OR tornados OR \
storm OR hurricane OR drought OR tsunami OR landslide OR landslides)', tag='temporary custom rule'))
stream.add_rules(add=tweepy.StreamRule(value='has:media (bio_location:india OR place_country:IN) (flood OR wildfire OR eartquake OR tornado OR storm OR hurricane OR drought OR tsunami OR landslide)', tag='location:IN has:info'))

rules = stream.get_rules()
print('ACTIVE FILTERS:', rules)


# Look for tweets with the below mentioned keywords only
stream.filter(expansions="author_id")
