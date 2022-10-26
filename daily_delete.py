
from dotenv import dotenv_values
from pymongo import MongoClient


config = dotenv_values(".env")
client = MongoClient(config['HOST'],
                  username=config['USERNAME'],
                 password=config['PASSWORD'])

db = client.dbjungle
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}


rows = list(db.party.find({}))


for r in rows:
    db.party.delete_one({ '_id': r['_id'] })
    

         