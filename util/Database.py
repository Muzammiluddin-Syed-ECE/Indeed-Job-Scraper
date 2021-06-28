import pymongo
from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = pymongo.MongoClient("mongodb+srv://admin:ladleLADLE@cluster0.ud2mk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.job

def insert_list_into_db(job_list):
    for job in job_list:
        db_job = {
            'title' : job['title'],
            'subtitle' : job['subtitle'],
            'description' :  job['description']
        }
        result = db.jobs.insert_one(db_job)
        print('Created {0} as {1}'.format(str(db_job['title']).encode('utf-8'),result.inserted_id))

def print_databases():
    print(client.list_database_names())

def print_collections():
    print(db.list_collection_names())

def print_everything_in_collection():
    for x in db['jobs'].find():
        print(str(x).encode('utf-8'))