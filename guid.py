import uuid
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
import json
from datetime import datetime, timedelta
import redis
from pymongo import MongoClient
from bson import json_util

# MongoDB database
cluster = "mongodb+srv://naytewen:vZUshobAIfqJc7R9@cluster0.dcw7l7u.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(cluster)
db = client.test
guids_data = db.guids

# method to parse JSON for mongoDB database
def parse_json(data):
    return json.loads(json_util.dumps(data))
# cache for redis
r_cache = redis.Redis(host='localhost', port=6379)
# handler for different endpoints
class GUIDhandler(RequestHandler):

    def post(self, guid=None):
        if guid is None: # generate valid guids if none is given
            guid = str(uuid.uuid4()).replace('-', '').upper()
        else: 
            guid = guid # doesn't change guid 
        
        # try parsing input data
        try:
            data = json.loads(self.request.body)
        except Exception as e: # error on client side
            self.set_status(400)
            self.write({'error': 'Invalid JSON format'})
            return

        user = data.get('user')
        # error for when guid is in input post
        if 'guid' in data:
            self.set_status(400)
            self.write({'error': 'cannot have guid in input'})
            return
        # error for when trying to make post with existing guid
        if guid in r_cache or guids_data.find_one({'guid': guid}) is not None:
            self.set_status(400)
            self.write({'error': 'guid already exists'})
            return
        # check if expiration is valid 
        if 'expire' in data:
            try: 
                expire = datetime.utcfromtimestamp(int(data['expire'])).strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e: # if not formatted in unix format
                self.set_status(400)
                self.write({'error': 'Time not in Unix format'})
                return
        else:
            # if expiration not given, default is just 30 days from point of creation
            expire = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        # timezone affects time module
        expiration = datetime.strptime(expire, '%Y-%m-%d %H:%M:%S')
        unix_time = (expiration - datetime(1970, 1, 1)).total_seconds()
        output = {'guid': guid, 'expire': unix_time, 'user': user}
        # sets the cache
        r_cache.set(guid, json.dumps(output))
        guids_data.insert_one(parse_json(output)) # stores in database
        # returns the output
        self.write(output)

    def get(self, guid):
        # gets data from the cache
        data = r_cache.get(guid)
        if data is None: # if guid is not found in cache, check database
            data = guids_data.find_one({'guid': guid})
            if data is None: # exception if guid is not found in database or cache
                self.set_status(400)
                self.write({'error': 'GUID not found'})
                return
        # returns the output
        self.write(json.loads(data))
    
    def put(self, guid):
        data = r_cache.get(guid)
        if data is None: # if guid is not found in cache, check database
            data = guids_data.find_one({'guid': guid})
            if data is None: # exception if guid is not found in database or cache
                self.set_status(400)
                self.write({'error': 'GUID not found'})
                return
        data = json.loads(data)
        input = json.loads(self.request.body)
        if 'guid' in input: # error if user tries to change guid 
            if input['guid'] != guid:
                self.set_status(400)
                self.write({'error': 'cannot update guid'})
                return
        if 'user' in input: # updates user
            data['user'] = input['user']
        if 'expire' in input: # updates expiration
            try: 
                expire = datetime.utcfromtimestamp(int(input['expire'])).strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e: # error if not formatted in unix format
                self.set_status(400)
                self.write({'error': 'Time not in Unix format'})
                return
            # timezone affects time module
            expiration = datetime.strptime(expire, '%Y-%m-%d %H:%M:%S')
            unix_time = (expiration - datetime(1970, 1, 1)).total_seconds()
            data['expire'] = unix_time
        # updates values in cache
        r_cache.set(guid, json.dumps(data))
        # updates values in database
        guids_data.update_one(guids_data.find_one({'guid':guid}), {"$set": parse_json(data)}) # stores in database
        self.write(data)

    def delete(self, guid):
        if guid not in r_cache and guids_data.find_one({'guid': guid}) is None: # not a valid guid error
            self.set_status(400)
            self.write({'error': 'guid not found'})
            return
        if guid in r_cache:
            r_cache.delete(guid) # removes from cache if it's still cache
        # removes from database 
        guids_data.delete_one(guids_data.find_one({'guid': guid}))

# creates app with given endpoints
def make_app():
  urls = [
     ("/guid/([A-F0-9]{32})", GUIDhandler), # endpoint given GUID
     ("/guid", GUIDhandler) # endpoint without GUID
          ]
  return Application(urls) 
  
# starts server 
if __name__ == '__main__':
    app = make_app()
    app.listen(8080)
    print("server is listening on port 8080")
    IOLoop.instance().start()
    