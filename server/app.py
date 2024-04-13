
from flask import Flask, jsonify, make_response, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):
    def delete(self):
        session.pop('page_views', None)
        session.pop('user_id', None)
        return {}, 204

class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):
    def get(self, id):
        session['page_views'] = session.get('page_views', 0) + 1
        if session['page_views'] <= 3:
            article = Article.query.get(id)
            if article:
                return jsonify(article.to_dict()), 200
            else:
                return {'message': 'Article not found'}, 404
        else:
            return {'message': 'Maximum pageview limit reached'}, 401

class Login(Resource):
    def post(self):
        username = request.get_json().get('username')
        if username:
            user = User.query.filter(User.username == username).first()
            if user:
                session['user_id'] = user.id
                return user.to_dict(), 200
            else:
                return {'message': 'User not found'}, 404
        else:
            return {'message': 'Username not provided'}, 400

class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return '', 204

class CheckSession(Resource):
    def get(self):
        if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.get(user_id)
            if user:
                return user.to_dict(), 200
            else:
                return {'message': 'User not found'}, 404
        else:
            return {}, 401
        
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
