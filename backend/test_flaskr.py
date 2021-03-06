import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')
        self.DB_USER = os.getenv('DB_USER', 'postgres')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
        self.DB_NAME = os.getenv('DB_NAME', 'trivia_test')
        database_path = 'postgresql+psycopg2://{}:{}@{}/{}'.format(self.DB_USER, self.DB_PASSWORD\
            , self.DB_HOST, self.DB_NAME)

        self.database_path = f'postgresql://postgres:postgres@localhost:5432/{self.database_name}'
        #"postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': "How did Tacitus die?",
            'answer': "The death of Tacitus is an unknown to the historical record.",
            'difficulty': 4,
            'category': 3
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['categories']))

    def test_get_paginated_question(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))
        self.assertTrue(len(data['questions']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_delete_question(self):
        res = self.client().delete("/questions/2")
        data = json.loads(res.data)

        question = Question.query.get(1)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], 2)
        self.assertEqual(question, None)

    def test_422_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Unprocessable entity')
        self.assertEqual(data['error'], 422)

    def test_create_question(self):
        res = self.client().post('/add', json = self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_question_search_does_not_exist(self):
        res = self.client().post('/questions', json={"searchTerm":"THEREISNOBOOKWITHTHISNAME"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_sent_requesting_beyond_valid_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_get_next_question(self):
        res = self.client().post('/quizzes', json={
            "previous_questions":[],
            "quiz_category": {"id":0, "type":"All"}
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(data['question'], None)

    def test_404_sent_requesting_beyond_valid_quiz_category(self):
        res = self.client().post('/quizzes', json={
            'previous_questions':[],
            'quiz_category': {'id':1000, 'type':"test"}
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()