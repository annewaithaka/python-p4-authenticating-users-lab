#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource # type: ignore

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
        session.clear()  # Clear all session data
        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = session.get('page_views', 0)  # Default to 0 if not set
        session['page_views'] += 1

        if session['page_views'] <= 3:
            article = Article.query.filter(Article.id == id).first()
            if article:
                return make_response(jsonify(article.to_dict()), 200)
            return jsonify({'message': 'Article not found'}), 404

        return {'message': 'Maximum pageview limit reached'}, 401

# New login resource
class Login(Resource):
    def post(self):
        username = request.json.get('username')
        user = User.query.filter_by(username=username).first()

        if user:
            session['user_id'] = user.id
            return user.to_dict(), 200  # Assuming you have a method to_dict in User
        return {'message': 'User not found'}, 404
    
# New logout resource
class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)  # Remove user_id from session
        return {}, 204

# New check session resource
class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')

        if user_id:
            user = User.query.get(user_id)
            return user.to_dict(), 200  # Assuming you have a method to_dict in User
        return {}, 401  # Unauthorized
    
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)