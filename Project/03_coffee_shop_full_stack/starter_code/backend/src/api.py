import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


with app.app_context():
    db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drink():
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200

@app.route('/hello', methods=['GET'])
def hello_test():
    print('hello')
    return 'hello'

@app.route('/drink/<string:title>', methods=['GET'])
def get_specific_drink(title):
    try:
        drink = Drink.query.filter(Drink.title==title).one_or_none()
        if drink is None:
            abort(404)

        return jsonify({
        "success": True,
        "drinks": drink.short()
        }),200
    
    except:
        abort(401)

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_dring_detail(payload):

    drinks = Drink.query.all()
    print('hello')
    return jsonify({
        "success": True,
        "drinks": [drink.long() for drink in drinks]
    }),200

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(payload):
    body = request.get_json()
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)
    try:
        new_drink = Drink(title=new_title, 
                        recipe=json.dumps(new_recipe))
        new_drink.insert()
    except:
        abort(401)
    else:
        return jsonify({
            "success": True,
            "new_drink": new_drink.short()
        }),200


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    body = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)

    try:
        title= body.get('title', None)
        recipe = body.get('recipe', None)

        if title:
            drink.title=title
        
        if recipe:
            drink.recipe = json.dumps(recipe)
        
        drink.update()

    except BaseException:
        abort(400)

    else:
        return jsonify({
            "success": True,
            "drinks": drink.long()
        }),200

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def remove_drink(payload, id):
    drink = Drink.query.filter(Drink.id==id).one_or_none()
    if drink is None:
        abort(404)
    try:
        drink.delete()
        return jsonify({
            "success": True,
            "deleted_drink": drink.short() 
        }),200
    except:
        abort(401)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500
