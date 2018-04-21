# final507_zfp


1.Data sources used:
Yelp website, google place map, Lyft. For yelp, because it is web crawling there is no need for api. For google place map, you need api(had better be the unlimited use because text search counts 10 for once and it may raises errors if it exceed the limits. https://developers.google.com/places/web-service/get-api-key?authuser=1). For Lyft, you need API and clienr secrets because it uses Oauth2, https://developer.lyft.com/docs/overview. Format can check "secrets.py".)


2.Brief description of how your code is structured
There is a function to create the sql database (create_first_table) but you donnot need to invoke it unless you wanna check how it runs. The one important class called Yelpeat(), which scrawl data from yelp website and write into database. Another one is called lyft_data(), which use api get data. To connect these two function, google_map() function will be invoked to get data from google place.

3. Brief user guide
All functional files should be in env1.
To run the presentation, just open app.py file. And it will ask you to enter the address after you click the button "ready?go". And a list of restaurants will show, then you can choose multiple restaurants by checking the box. And scroll down to the bottom, there is second input for user to enter any address.
If the address is valid, you will see a table which tell you the estimation from lyft is not available.  Then you can just go back and re-enter.
In the lyft html you can see a table of estimation information about the restaurants you chose. You can sort the information by click the radio buttom then the table will change by the order you choose.
