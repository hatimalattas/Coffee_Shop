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

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def drinks():
    # get all drinks
    drinks = Drink.query.all()

    # 404 if no drinks found
    if len(drinks) == 0:
        abort(404)

    # format using .short()
    drinks_short = [drink.short() for drink in drinks]

    # return drinks
    return jsonify({
        'success': True,
        'drinks': drinks_short
    })


'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    # get all drinks
    drinks = Drink.query.all()

    # 404 if no drinks found
    if len(drinks) == 0:
        abort(404)

    # format using .long()
    drinks_long = [drink.long() for drink in drinks]

    # return drinks
    return jsonify({
        'success': True,
        'drinks': drinks_long
    })

'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    # get the drink info from request
    body = request.get_json()
    title = body['title']
    recipe = body['recipe']

    # create a new drink
    drink = Drink(title=title, recipe=json.dumps(recipe))

    try:
        # add drink to the database
        drink.insert()
    except:
        abort(422)

    return jsonify({
        "success": True,
        "drinks": drink.long()
    })

'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink_by_id(payload, id):
    # get drink by id
    drink = Drink.query.filter_by(id=id).one_or_none()

    # if drink not found
    if drink is None:
        abort(404)

    # get request body
    body = request.get_json()

    # update title if present in body
    if 'title' in body:
        drink.title = body['title']

    # update recipe if present in body
    if 'recipe' in body:
        drink.recipe = json.dumps(body['recipe'])

    try:
        # update drink in database
        drink.insert()
    except:
        # Bad Request
        abort(400)

    # array containing .long() representation
    drink = [drink.long()]

    # return drink to view
    return jsonify({
        'success': True,
        'drinks': drink
    })
'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    # get drink by id
    drink = Drink.query.filter_by(id=id).one_or_none()

    # if drink not found
    if drink is None:
        abort(404)

    try:
        # delete drink from database
        drink.delete()
    except:
        # server error
        abort(500)

    # return status and deleted drink id
    return jsonify({
        'success': True,
        'delete': id
    })

## Error Handling
'''
Example error handling for unprocessable entity
'''
# @app.errorhandler(422)
# def unprocessable(error):
#     return jsonify({
#                     "success": False, 
#                     "error": 422,
#                     "message": "unprocessable"
#                     }), 422

'''
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@DONE implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400
@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "server error"
    }), 500

'''
@DONE implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def handle_auth_errors(e):
    return jsonify({
        'success': False,
        'error': e.status_code,
        'message': e.error
    }), 401