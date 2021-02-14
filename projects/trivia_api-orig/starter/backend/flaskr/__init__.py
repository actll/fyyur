import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  #cors = CORS(app, resources{r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-ALlow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    if not categories:
      abort(404)
    else:
      page = request.args.get('page', 1, type=int)
      start = (page-1)*QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE
      categories = Category.query.order_by(Category.id).all()
      formatted_categories = [category.format() for category in categories]
      
      cats = []
      for category in formatted_categories:
        cats.append([category['type']])
      
      return jsonify({
        'success':True,
        'categories':formatted_categories[start:end]
        
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
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    if not questions:
      abort(404)
    else:
      page = request.args.get('page', 1, type=int)
      start = (page-1)*QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE
      
      formatted_question = [question.format() for question in questions]
      
      formatted_question_list = []
      for q in formatted_question:
        formatted_question_list.append(q['question'])
        
      categories = Category.query.all()
      formatted_categories = [category.format() for category in categories]
      cats = []
      for category in formatted_categories:
        cats.append(category['type'])
      
      return jsonify({
        'success':True,
        'question':formatted_question_list[start:end],
        'number of questions': len(formatted_question_list)
        
      })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.filter_by(question_id=Question.id).one_or_none()
    if not question:
      abort(400, {'message': 'No question exists'})
    try:
      question.delete()
      return jsonify({
        'success':True,
        'deleted':question_id
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

    

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  
  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()
    if not body:
      abort(400, {'message': 'no json body in request'})
    search_term = body.get('searchTerm', None)
    #print("term is: " + body.get('searchTerm', None))
    
    if search_term:
      questions = Question.query.filter(Question.question.contains(search_term)).all()

      if not questions:
        abort(404, {'message':'no question exists that contains "{}".'.format(search_term)})
      
      page = request.args.get('page', 1, type=int)
      start = (page-1)*QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE
      
      formatted_question = [question.format() for question in questions]
      results = Question.query.order_by(Question.id).all()
      
      categories = Category.queryall()
      categories_all = [category.format() for category in categories]

      return jsonify({
        'success': True,
        'questions': question_result,
        'total_questions': len(question_result),
        'current_category' : categories_all
      })

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty = body.get('difficulty', None)
    new_category = body.get('category', None)

    if not new_question:
      abort(400, {'message': 'Question can not be blank'})

    if not new_answer:
      abort(400, {'message': 'Answer can not be blank'})

    if not new_category:
      abort(400, {'message': 'Category can not be blank'})

    if not new_difficulty:
      abort(400, {'message': 'Difficulty can not be blank'})
      
    page = request.args.get('page', 1, type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = Question.query.order_by(Question.id).all()
    formatted_question = [question.format() for question in questions]

    try:
      question = Question(
        question = new_question, 
        answer = new_answer, 
        difficulty = new_difficulty,
        category= new_category)
      question.insert()

      return jsonify({
        'success': True,
        'created': question.id,
        'questions': formatted_question,
        'total_questions': len(questions)
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
  
  @app.route('/categories/<string:category_id>/questions', methods = ['GET'])
  def get_question_by_cat_id(category_id):
    categories = Question.query.filter(Question.category == str(category_id)).all()
    if not categories:
      abort(400, {'message': 'No questions under that category.'})
    page = request.args.get('page', 1, type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    formatted_question = [question.format() for question in categories]
    
   #formatted_question_list = []
   # for q in formatted_question:
    #  formatted_question_list.append([q['type']])
    return jsonify({
      'success':True,
      'question': formatted_question[start:end],
      'total questions': len(formatted_question),
      'category': category_id
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
  @app.route('/quizzes', methods = ['POST'])
  def quiz_questions():
    body = request.get_json()
    if not body:
      Abort(400, {'message': 'no question selected'})
    prev_questions = body.get('previous_questions')
    quiz_category = body.get('quiz_category')
    print(prev_questions)
    if not previous_questions:
      if current_category:
        questions_raw = (Question.query
          .filter(Question.category == str(current_category['id']))
          .all())
      else:
        questions_raw = (Question.query.all())    
    else:
      if current_category:
        questions_raw = (Question.query
          .filter(Question.category == str(current_category['id']))
          .filter(Question.id.notin_(previous_questions))
          .all())
      else:
        questions_raw = (Question.query
          .filter(Question.id.notin_(previous_questions))
          .all())

    # Format questions & get a random question
    questions_formatted = [question.format() for question in questions_raw]
    random_question = questions_formatted[random.randint(0, len(questions_formatted))]
      
    return jsonify({
        'success': True,
        'question': random_question
      })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success":False,
      "error":400,
      "message":'bad request'
    })
    
  @app.errorhandler(401)
  def bad_request(error):
    return jsonify({
      "success":False,
      "error":401,
      "message":"unauthorized"
    })
    
  @app.errorhandler(403)
  def bad_request(error):
    return jsonify({
      "success":False,
      "error":403,
      "message": "forbidden"
    })
    
  @app.errorhandler(404)
  def bad_request(error):
    return jsonify({
      "success":False,
      "error":404,
      "message": "file not found"
    })
    
  @app.errorhandler(405)
  def bad_request(error):
    return jsonify({
      "success":False,
      "error":405,
      "message":"method not allowed"
    })
    
  @app.errorhandler(422)
  def bad_request(error):
    return jsonify({
      "success":False,
      "error":422,
      "message": "unprocessable error"
    })
    
  @app.errorhandler(500)
  def bad_request(error):
    return jsonify({
      "success":False,
      "error":500,
      "message": "server error"
    })
  
  return app

    