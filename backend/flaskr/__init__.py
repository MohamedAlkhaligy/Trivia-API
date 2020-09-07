import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
NOT_SPECIFIED = 0

def paginate_questions(request, questions):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  selected_questions = [question.format() for question in questions[start:end]]
  return selected_questions

def get_all_categories():
  return {category.id : category.type for category in Category.query.order_by(Category.id).all()}

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = get_all_categories()

    if len(categories) == 0:
      abort(404)

    return jsonify({
      "categories" : categories
    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_paginated_question():
    questions = Question.query.order_by(Question.id).all()
    selected_questions = paginate_questions(request, questions)
    categories = get_all_categories()

    if len(selected_questions) == 0:
      abort(404)

    return jsonify({
      "questions": selected_questions,
      "total_questions": len(questions),
      "current_category": NOT_SPECIFIED,
      "categories": categories
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route("/questions/<int:question_id>", methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      
      if question is None:
        abort(404)
        
      question.delete()

      return jsonify({
        'success': True,
        'deleted': question_id 
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route("/add", methods=['POST'])
  def create_question():
    body = request.get_json()
    try:
      new_question = Question(question = body['question'], answer = body['answer'],\
        category = body['category'], difficulty = body['difficulty'])

      new_question.insert()

      return jsonify({
        'success': True
      })
    except:
      abort(422)
    
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route("/questions", methods=['POST'])
  def create_or_search_question():
    body = request.get_json()
    search_term = body.get('searchTerm', None)
    try:
      search_results = Question.query.filter(\
        Question.question.ilike(f'%{search_term}%')).order_by(Question.id).all()
      selected_questions = paginate_questions(request, search_results)
      return jsonify({
        'questions':selected_questions,
        'total_questions':len(search_results),
        'current_category': NOT_SPECIFIED
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route("/categories/<category_id>/questions")
  def get_category_by_id(category_id):
    questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
    selected_questions = paginate_questions(request, questions)

    if len(selected_questions) == 0:
      abort(404)

    return jsonify({
      "questions":selected_questions,
      "total_questions": len(questions),
      "current_category":category_id
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_next_question():
    body = request.get_json()
    previous_questions = body['previous_questions']
    category_id = body['quiz_category']['id']
    questions = None
    question = None
    if category_id == NOT_SPECIFIED:
      questions = Question.query.order_by(Question.id).all()
    else:
      questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()

    if len(questions) == 0:
      abort(404)
    
    question_index = len(previous_questions)
    if question_index < len(questions):
      question = questions[question_index].format()
    else:
      question = None

    return jsonify({
      'question': question
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        'success':False,
        'error':400,
        'message':'Bad request'
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        'success':False,
        'error':404,
        'message':'Resource not found'
    }), 404

  @app.errorhandler(405)
  def disallowed_method(error):
    return jsonify({
        'success':False,
        'error':405,
        'message':'Method not allowed'
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        'success':False,
        'error':422,
        'message':'Unprocessable entity'
    }), 422

  @app.errorhandler(500)
  def internal_server(error):
    return jsonify({
        'success':False,
        'error':500,
        'message':'Internal server error'
    }), 500
  
  return app

    