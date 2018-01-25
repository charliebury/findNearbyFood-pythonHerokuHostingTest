from flask import Flask, render_template, request, jsonify, session, abort, g, json
from findARestaurant import findARestaurant
from models import Base, previousSearches

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import string
import random


engine = create_engine('sqlite:///findFoodUsers.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
dbsession = DBSession()

app = Flask(__name__)

app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))


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
            newSearch = previousSearches(location=location, foodType=foodType)
            dbsession.add(newSearch)
            dbsession.commit()
            return render_template('result.html')
        else:
            return render_template('sorry.html')


@app.route('/getFoodResult', methods=['GET', 'POST'])
def getFoodResult():
    restaurantInfo = session.get('restaurantInfo')
    if restaurantInfo != "No Restaurants Found":
        return json.dumps(restaurantInfo)


@app.route('/showPreviousSearches', methods=['GET'])
def showPreviousSearches():
    if request.method == 'GET':
        prevSearches = dbsession.query(previousSearches).all()
        return jsonify(prevSearches=[prevSearch.serialize for prevSearch in prevSearches])


if __name__ == '__main__':
    app.run(debug=True)
