from .models import (User, Role, UserRole, Project, DeveloperProject, Task, UserTask)

from flask import Flask, request, jsonify
from . import app, db
import bcrypt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity, verify_jwt_in_request
)
# Expetions for sqlaclemy
from sqlalchemy.exc import IntegrityError



from functools import wraps


# Setup the Flask-JWT-Extended extension. Read more: https://flask-jwt-extended.readthedocs.io/en/stable/options/
app.config['JWT_SECRET_KEY'] = 'secret-secret'  # Change this!
jwt = JWTManager(app)



#define decorator for accessing the route with project manager role
def manager_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_jwt_identity()
        if user["role"] == "Project Manager":
            return fn(*args, **kwargs)

        return jsonify(msg='THis route is restricted to project Manager!'), 403
    return wrapper

#Function to check if the current user is the project manager of this project or not
def isprojectManager(projectID):
    user = get_jwt_identity()
    manager = User.query.get(user['id'])
    project = Project.query.get(projectID)
    if manager.id == project.manager_id:
        return True
    return False

#Function to check if given user is a project manger or member of project
def isMemeberofProjct(projectID,developerID):
    userproject = DeveloperProject.query.filter_by(developer_id=developerID).filter_by(project_id=projectID).first()
    if not userproject:
        return False
    return True

#Function to check if user is a project manger or member of project
def ismanagerorMemeber(projectID):
    user = get_jwt_identity()
    if user['role'] == 'Project Manager':
        project = Project.query.get(projectID)
        if user['id'] == project.manager_id:
            return True
        return False
    else:
        userproject = DeveloperProject.query.filter_by(developer_id=user['id']).first()
        if not userproject:
            return False
        return True

#Function to check if user has permission to assign a task or not. Only project manager or users who created the task could assign task to themself
def taskassignPermission(taskID, developerID):
    user = get_jwt_identity()
    task = Task.query.get(taskID)
    if user['role'] == 'Project Manager':
        project = Project.query.get(task.project_id)
        if user['id'] == project.manager_id:
            return True
        return False
    else:
        userproject = DeveloperProject.query.filter_by(developer_id=user['id']).first()
        if not userproject:
            return False
        else:
            if task.creator_id == user['id'] and developerID == user['id']:
                return True
            return False


#Sign up
@app.route('/signup', methods=['POST'])
def signup():
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        rolename = request.json.get('role', None)
        role = Role.query.filter_by(name=rolename).one()

        if not username:
            return 'Missing username', 400
        if not password:
            return 'Missing password', 400

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user = User(username=username, password=hashed)
        db.session.add(user)
        db.session.commit()

        db.session.add(UserRole(role=role, user=user))
        db.session.commit()

        access_token = create_access_token(identity={"username": username})
        return {"access_token": access_token}, 200
    except IntegrityError:
        # the rollback func reverts the changes made to the db ( so if an error happens after we commited changes they will be reverted )
        db.session.rollback()
        return 'User Already Exists', 400
    except AttributeError:
        return 'Provide an Username and Password in JSON format in the request body', 400

#Log in
@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)

        if not username:
            return 'Missing username', 400
        if not password:
            return 'Missing password', 400

        user = User.query.filter_by(username=username).first()
        if not user:
            return 'User Not Found!', 404

        role = Role.query.get(UserRole.query.filter_by(user_id=user.id).first().role_id)
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            access_token = create_access_token(identity={"username": username,"id":user.id,"role":role.name})
            return {"access_token": access_token}, 200
        else:
            return 'Invalid Login Info!', 400
    except AttributeError:
        return 'Provide an Username and Password in JSON format in the request body', 400

#Adding project, only project manager can do this
@app.route('/addproject', methods=['POST'])
@jwt_required()
@manager_required
def addproject():
    user = get_jwt_identity()
    manager = User.query.get(user['id'])
    name = request.json.get('name', None)
    project = Project(name=name, users=manager)
    db.session.add(project)
    db.session.commit()
    db.session.commit()
    return f'One project with name {name} created', 200

#Retrieve projects which current user is manager of them
@app.route('/projects', methods=['GET'])
@jwt_required()
@manager_required
def projects():
    user = get_jwt_identity()
    projects = Project.query.filter_by(manager_id=user['id']).all()
    projectsArr = {}
    count = 0
    for project in projects:
        count = count + 1
        projectsArr[count] = project.name
    return jsonify(projectsArr)

#Assign project to a developer
@app.route('/assignproject/<int:project_ID>', methods=['POST'])
@jwt_required()
@manager_required
def assignproject(project_ID):
    if isprojectManager(project_ID):
        developerID = request.json.get('developerID', None)
        project = Project.query.get(project_ID)
        developer = User.query.get(developerID)
        db.session.add(DeveloperProject(project=project, user=developer))
        db.session.commit()
        return f'One developer assigned to project', 200
    else:
        return jsonify(msg='You can only add a developer to a project if you have created that project yourself!'), 403

#Adding a task in a project that can be done by the project manager and all project developers
@app.route('/addtask/<int:project_ID>', methods=['POST'])
@jwt_required()
def addtask(project_ID):
    if ismanagerorMemeber(project_ID):
        user = get_jwt_identity()
        creator = User.query.filter_by(username=user['username']).first()
        description = request.json.get('description', None)
        project = Project.query.get(project_ID)

        task = Task(description=description, users=creator, projects=project)
        db.session.add(task)
        db.session.commit()
        return f'One task with description {description} is added', 200
    else:
        return jsonify(msg="You don't have permission to add task in this project!"), 403

#Assignin task to a developer
@app.route('/assigntask/<int:task_ID>', methods=['POST'])
@jwt_required()
def assigntask(task_ID):
    developerID = request.json.get('developerID', None)
    projectID = Task.query.get(task_ID).project_id
    if isMemeberofProjct(projectID,developerID):
        if taskassignPermission(task_ID, developerID):
            task = Task.query.get(task_ID)
            developer = User.query.get(developerID)
            db.session.add(UserTask(user=developer, task=task))
            db.session.commit()
            return f'One task assigned to {developer.username}', 200
        else:
            return jsonify(msg="You don't have permission to assign task in this project!"), 403
    else:
        return jsonify(msg="The intended user is not a member of the project in which the task was created!"), 403

#List of all tasks in a project
@app.route('/tasks/<int:project_ID>', methods=['GET'])
@jwt_required()
def tasks(project_ID):
    if ismanagerorMemeber(project_ID):
        tasks = Task.query.filter_by(project_id=project_ID).first()
        tasksArr = {}
        count = 0
        for task in tasks:
            count = count + 1
            tasksArr[count] = task.description
            return jsonify(tasksArr)
    else:
        return jsonify(msg="You don't have permission to see tasks of this project!"), 403

#List of user’s tasks in the project
@app.route('/mytasks', methods=['GET'])
@jwt_required()
def mytasks():
    user = get_jwt_identity()
    developer = User.query.get(user['id'])
    usertasks = UserTask.query.filter_by(user_id=developer.id).all()
    tasksArr = {}
    count = 0
    for usertask in usertasks:
        count = count + 1
        task = Task.query.get(usertask.task_id)
        project = Project.query.get(task.project_id)
        tasksArr['Project = ' + project.name + ' task number ' + str(count)] = task.description
    return jsonify(tasksArr)

# protected test route
@app.route('/test', methods=['GET'])
@jwt_required()
@manager_required
def test():
    user = get_jwt_identity()
    username = user['username']
    return f'Welcome to the protected route {username}!', 200
