from flask import Flask, render_template, request, json
from findARestaurant import findARestaurant
from flask import session

app = Flask(__name__)

app.secret_key = 'jhtresferhwergfq34654q3efvtw43we'


# homepage set to index.html
@app.route('/')
def index():
    return render_template('index.html')


# return to index.html
@app.route('/goHome')
def goHome():
    return render_template('index.html')


# find a restaurant based off what and where inputs
@app.route('/enterFoodWants', methods=['POST'])
def enterFoodWants():
    if request.method == 'POST':
        location = request.form['location']
        foodType = request.form['foodType']
        restaurantInfo = findARestaurant(foodType, location, 5)
        session['restaurantInfo'] = restaurantInfo
        if restaurantInfo != "No Restaurants Found":
             return render_template('result.html')
        else:
            return render_template('sorry.html')


@app.route('/getFoodResult')
def getFoodResult():
    restaurantInfo = session.get('restaurantInfo')
    if restaurantInfo != "No Restaurants Found":
        return json.dumps(restaurantInfo)


if __name__ == '__main__':
    app.run(debug=True)
