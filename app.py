from flask import Flask, render_template, request, jsonify, session, abort, g, json
from findARestaurant import findARestaurant
from models import Base, User, previousSearches
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_httpauth import HTTPBasicAuth
import string
import random

auth = HTTPBasicAuth()

engine = create_engine('sqlite:///findFoodUsers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
dbsession = DBSession()

app = Flask(__name__)

app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))


# verify whether a username/password or token are valid
@auth.verify_password
def verify_password(username_or_token, password):
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = dbsession.query(User).filter_by(id=user_id).one()
    else:
        user = dbsession.query(User).filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


# get a new token (requires username/password to use)
@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


# make a new user and save to database for later use
@app.route('/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        # not enough info supplied
        abort(400)
    if dbsession.query(User).filter_by(username=username).first() is not None:
        # existing user
        abort(400)
    user = User(username=username)
    user.hash_password(password)
    dbsession.add(user)
    dbsession.commit()
    return jsonify({'username': username}), 201


# homepage set to index.html
@app.route('/')
def index():
    return render_template('index.html')


# return to index.html
@app.route('/goHome')
def goHome():
    return render_template('index.html')


# find a restaurant based off what/where inputs
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


# supply json format information on restaurants to result.html
@app.route('/getFoodResult', methods=['GET'])
def getFoodResult():
    restaurantInfo = session.get('restaurantInfo')
    if restaurantInfo != "No Restaurants Found":
        return json.dumps(restaurantInfo)


# logged in users can see all previous searches
@app.route('/showPreviousSearches', methods=['GET'])
@auth.login_required
def showPreviousSearches():
    if request.method == 'GET':
        prevSearches = dbsession.query(previousSearches).all()
        return jsonify(prevSearches=[prevSearch.serialize for prevSearch in prevSearches])


if __name__ == '__main__':
    app.run(debug=True)
