import pymongo
from decouple import config

try:
    client = pymongo.MongoClient(config('MONGODB'))
    flux_wallet_db = client['fluxwallet']
except Exception as err:
    print(err)
    client = None
