
from flask import Flask, render_template,request,redirect
import fn


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect('/hello')
    else:
        return render_template("index.html")


@app.route('/hello', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        pass
        # except:
        #     return render_template("hello.html", cityname=input_city)#,error_message='')
    else:
        input_city = ''
        return render_template("hello.html")


@app.route('/yelptable',methods=['GET', 'POST'])
def yelptable():
    if request.method == 'POST':
        # sortby = request.form['sortby']
        # cityname=hello().city
        input_city = request.form['cityname']


        yelp_db=fn.Yelpeat(input_city).get_data()
        error_message = ""
        if not yelp_db:
            error_message = "Please input a valid address."
        # yelp_db=test.get_data(input_city)
        return render_template("yelptable.html",city=input_city,list_of_res=yelp_db,ERROR=error_message)
        # city=hello().request.form['cityname']
        # Yelpeat().sorteat(sortby)
    else:
        return render_template("yelptable.html")


      # list_of_res=fn.Yelpeat(city).get_data()
#     # name = request.form["name"]
#     # message = request.form["message"]
#     # model.add_entry(name, message)return render_template("hello.html", city=city)

@app.route('/lyftlist',methods=['GET', 'POST'])
def lyft():
    if request.method == "POST":
        eatid_list=request.form.getlist('store')
        origin=request.form['user_location']
        lyft = fn.lyft_data()
        fare_table=lyft.create_table(origin,eatid_list)
        return render_template('lyftlist.html',list_of_lyft=fare_table)

    else:
        return render_template("yelptable.html")

@app.route('/lyftupdate',methods=['GET', 'POST'])
def lyftupdate():
    if request.method == 'POST':
        sortby = request.form['sortby']
        lyft = fn.lyft_data()
        lyft_up=lyft.sort_table(sortby)
    return render_template('lyftupdate.html',requirement=sortby,update_lyft=lyft_up)


if __name__ == '__main__':
    # model.init_bball()
    app.run(debug=True)
