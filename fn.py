from bs4 import BeautifulSoup
import secrets
import requests
import sqlite3
import csv
import json
import urllib
from urllib.parse import urlencode
from lyft_rides.auth import ClientCredentialGrant
from lyft_rides.session import Session
from lyft_rides.client import LyftRidesClient

map_api=secrets.map_api

client_id=secrets.client_id
client_secret=secrets.client_secret
access_token=secrets.access_token
scope= secrets.scope
token_type=secrets.token_type
# 1.cache
CACHE_FNAME = 'checkcache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

def get_unique_key(url,params=None):
    if params!=None:
       qstr=urlencode(params)
       nurl=url+"?"+qstr
       return nurl
    else:
        return url

def make_request_using_cache(url,params=None):
    unique_ident = get_unique_key(url,params)

    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        print("Making a request for new data...")


        resp = requests.get(url,params)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[unique_ident]


#2 Create DB
# 3 WRITE INTO DB

def create_first_table(db='FoodieGo.sqlite'):
    DBNAME=db
    conn = sqlite3.connect(DBNAME,check_same_thread=False)
    cur = conn.cursor()
    # #

    statement='''CREATE TABLE EAT(
    'Id' INTEGER NULL PRIMARY KEY AUTOINCREMENT,
    'City' TEXT NOT NULL,
    'Name' TEXT NOT NULL,
    'Price' TEXT,
    'Rating' NUMERIC,
    'address' TEXT
    )'''
    cur.execute(statement)
    conn.commit()
    # conn.close()
    statement='''CREATE TABLE RIDE(
    'Id' INTEGER NOT NULL PRIMARY KEY,
    'Origin'TEXT NOT NULL,
    'Origin_geo' TEXT,
    'Name' TEXT,
    'Destination' TEXT,
    'Destination_geo' TEXT,
    'Estimated_minutes' REAL,
    'Estimated_miles' REAL,
    'Estimated_max_cost' REAL,
    'Estimated_min_cost'REAL,
    'EAT_ID'INTEGER,
    FOREIGN KEY(EAT_ID) REFERENCES EAT(Id))
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()


# #
# create_first_table()

# 3.1 google maps
def google_map(address):

        map_url='https://maps.googleapis.com/maps/api/place/textsearch/json'
        params={}
        params['key']=map_api
        params['query']=str(address)
        req=make_request_using_cache(map_url,params=params)
        rstxt=json.loads(req)
        rs=rstxt['results']
        geoloc=rs[0]['geometry']['location']

        lat=geoloc['lat']
        log=geoloc['lng']
        loc="{},{}".format(lat,log)

        return loc


# 3.2 yelp
class Yelpeat():

    def __init__(self,user_input_city,db='FoodieGo.sqlite'):
        self.city=user_input_city
        self.cachedict = {}
        self.db=db

    def get_data(self):
        DBNAME=self.db
        conn = sqlite3.connect(DBNAME,check_same_thread=False)
        cur = conn.cursor()

        statement='SELECT * FROM EAT where EAT.City='+"'"+str(self.city)+"'"
        datalist=cur.execute(statement).fetchall()
        if datalist !=[]:
                return datalist
        else:
            result = self.create_db()

            statement='SELECT * FROM EAT where EAT.City='+"'"+str(self.city)+"'"
            datalist=cur.execute(statement).fetchall()


            return datalist
        conn.close()

    def create_db(self):
        DBNAME=self.db
        conn = sqlite3.connect(DBNAME,check_same_thread=False)
        cur = conn.cursor()

        baseurl="https://www.yelp.com/"
        search_url=baseurl+'search'
        param={}
        param['find_desc']="Top+100+Places+to+Eat"
        param['find_loc']=self.city
        n=range(11)
        for i in n:
            param['start']=i*10
            html=make_request_using_cache(search_url,param)
            soup_a = BeautifulSoup(html, 'html.parser')
            list_of_eat=soup_a.find_all("li",class_="regular-search-result")

            for eat in list_of_eat:
                try:
                    name=eat.find('a',class_='biz-name').text.strip()
                    price=eat.find('span',class_="business-attribute price-range").text.strip()
                    rating=eat.find('div',class_='i-stars')['title'][:3]
                    add=str(eat.find('address'))
                    add = add.replace("<address>", "").replace("</address>", "").replace("<br>", " ").replace("<br/>", " ")

                    params=(self.city,name,price,rating,add)
                    statement='''INSERT INTO EAT VALUES(Null,?,?,?,?,?)'''
                    cur.execute(statement,params)
                    conn.commit()

                except:
                    pass
        conn.close()


class lyft_data():

    def __init__(self):
        pass


    def estmate_cost(self,start,end,type="lyft"):
        auth_flow = ClientCredentialGrant(client_id, client_secret,scope,)
        session = auth_flow.get_session()
        client = LyftRidesClient(session)

        s_lat=start.split(',')[0]
        s_log=start.split(',')[1]
        e_lat=end.split(',')[0]
        e_log=end.split(',')[1]

        est_dict={}
        try:
            cost_resp=client.get_cost_estimates(start_latitude=s_lat, start_longitude=s_log, end_latitude=e_lat, end_longitude=e_log).json
            est=cost_resp["cost_estimates"][0]

            est_dict['start']=start
            est_dict['end']=end
            est_dict['es_time']=est["estimated_duration_seconds"]//60
            est_dict['es_distance']=est["estimated_distance_miles"]
            est_dict['es_cost_max']=est["estimated_cost_cents_max"]/100
            est_dict['es_cost_min']=est["estimated_cost_cents_min"]/100
        except:
            est_dict['start']=start
            est_dict['end']=end
            est_dict['es_time']='Not avaliable'
            est_dict['es_distance']='Not avaliable'
            est_dict['es_cost_max']='Not avaliable'
            est_dict['es_cost_min']='Not avaliable'

        return est_dict

    def create_table(self,origin,list_of_dest, db="FoodieGo.sqlite"):
        DBNAME= db
        conn = sqlite3.connect(DBNAME,check_same_thread=False)
        cur = conn.cursor()
        #drop table
        statement = '''
            DROP TABLE IF EXISTS 'RIDE';
        '''
        cur.execute(statement)
        conn.commit()

        statement='''CREATE TABLE RIDE(
        'Id' INTEGER NOT NULL PRIMARY KEY,
        'Origin'TEXT NOT NULL,
        'Origin_geo' TEXT,
        'Name' TEXT,
        'Destination' TEXT,
        'Destination_geo' TEXT,
        'Estimated_minutes' REAL,
        'Estimated_miles' REAL,
        'Estimated_max_cost' REAL,
        'Estimated_min_cost'REAL,
        'EAT_ID'INTEGER,
        FOREIGN KEY(EAT_ID) REFERENCES EAT(Id))
        '''
        cur.execute(statement)
        conn.commit()

        start_add=google_map(origin)

        for fkid in list_of_dest:
            statement_dest= "SELECT Address, Name FROM EAT WHERE EAT.Id="
            statement_dest+=fkid
            dest_eat=cur.execute(statement_dest).fetchone()[0]
            dest_add = ""
            try:
                dest_add=google_map(dest_eat)
            except:
                print("Google place API error")
            dest_name=cur.execute(statement_dest).fetchone()[1]



            ridedb=self.estmate_cost(start_add,dest_add)
            param=(fkid,origin,start_add,dest_name,dest_add,ridedb['es_time'],ridedb['es_distance'],ridedb['es_cost_max'],ridedb['es_cost_min'])
            statement='''INSERT INTO RIDE (EAT_ID,Origin,Origin_geo,Name,Destination_geo,Estimated_minutes, Estimated_miles,Estimated_max_cost,Estimated_min_cost)
            VALUES(?,?,?,?,?,?,?,?,?)'''
            cur.execute(statement,param)
            conn.commit()

        update='UPDATE RIDE SET Destination=(SELECT Address FROM EAT where RIDE.EAT_ID=EAT.Id)'
        cur.execute(update)
        conn.commit()

        getdata='SELECT * FROM RIDE'
        lyft_db=cur.execute(getdata).fetchall()
        conn.close()

        return lyft_db

    def sort_table(self, key,db='FoodieGo.sqlite'):
        DBNAME=db
        conn = sqlite3.connect(DBNAME,check_same_thread=False)
        cur = conn.cursor()

        statement="SELECT * FROM RIDE ORDER BY {} ASC".format(key)

        lyft_up=cur.execute(statement).fetchall()
        conn.close()

        return lyft_up
