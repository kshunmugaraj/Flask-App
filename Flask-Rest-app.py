###########################################################################
# Task Manager for managing the tasks
###########################################################################
#!/usr/bin/env python
import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from flask.json import JSONEncoder
import json
# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'FLASK REST APPLICATION'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

@app.before_first_request
def create_tables():
    db.create_all()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class Task(db.Model):
    __tablename__= 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32),nullable=False) 
    description = db.Column(db.String(32), nullable=False)
    done = db.Column(db.Boolean(32), nullable=True)
    
     
    def __init__(self, title, description,done):
        self.title = title
        self.description=description
        self.done=done

    def dump_to_json(self):
            return {
                   'id'     : self.id,
                   'title'  : self.title,
                   'description'     :self.description,
                   'done':self.done
            }

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
@auth.login_required
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


#API for create tasks
@app.route('/taskmanager/api/v1.0/tasks', methods=['POST'])
@auth.login_required
def create_task():
    title = request.json.get('title')
    description = request.json.get('description')
    done = request.json.get('done')
    if title is None or description is None or done is None:
        abort(400)    # missing arguments
    if Task.query.filter_by(title=title).first() is not None:
        abort(400)    # existing task 
    task = Task(title=title,description=description,done=done)
    #task.title(title)
    #task.description(description)
    #task.done(done)
    db.session.add(task)
    db.session.commit()
    return (jsonify({'task': task.title}), 201,
            {'Location': url_for('get_task', id=task.id, _external=True)})


#Retrieves all the tasks
@app.route('/taskmanager/api/v1.0/tasks',methods=['GET'])
@auth.login_required
def get_task():
    tasks = Task.query.all()
    if not tasks:
        abort(400)
    return jsonify(tasks=[e.dump_to_json() for e in tasks])


#Updates the task
@app.route('/taskmanager/api/v1.0/tasks/<int:id>',methods=['PUT'])
@auth.login_required
def update_task(id):
    task = Task.query.get(id)
    if not task:
        abort(400)    # ID is not present 

    if 'title' in request.json:
        task.title = request.json.get('title')
    if 'description' in request.json:
        task.description = request.json.get('description')
    if 'done' in request.json:
        task.done = request.json.get('done')
    db.session.commit()
    return jsonify({'task': task.title})


#Retrieves the task
@app.route('/taskmanager/api/v1.0/tasks/<int:id>')
@auth.login_required
def get_tasks(id):
    task = Task.query.get(id)
    if not task:
        abort(400)
    return jsonify({'task': task.title})

#Delete task
@app.route('/taskmanager/api/v1.0/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.filter_by(id=id).one()
    if not task:
        abort(400)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'Delete Status': "Success"})

if __name__ == '__main__':
    app.run(debug=True)
