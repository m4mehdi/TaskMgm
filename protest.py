from .models import (User, Role, UserRole, Project, DeveloperProject, Task, UserTask)

import pytest

from . import app, db
import requests
import json
from flask_sqlalchemy import inspect

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}

url ='http://127.0.0.1:5000'
def db_data_setup():
    # Add Roles
    developer = Role(name='Developer')
    manager = Role(name='Project Manager')
    with app.app_context():
        db.create_all()
        db.session.add(developer)
        db.session.add(manager)
        db.session.commit()
    return [developer,manager]

def createusers():
    signup = url + '/signup'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    devuse1 = json.dumps({'username':'devuser1','password':'123456','role':'Developer'})
    devuse2 = json.dumps({'username':'devuser2','password':'123456','role':'Developer'})
    devuse3 = json.dumps({'username':'devuser3','password':'123456','role':'Developer'})
    devuse4 = json.dumps({'username':'devuser4','password':'123456','role':'Developer'})

    manageruser1 = json.dumps({'username':'manageruser1','password':'123456','role':'Project Manager'})
    manageruser2 = json.dumps({'username':'manageruser2','password':'123456','role':'Project Manager'})

    print('Test adding users\n')
    response = requests.post(url=signup, data=devuse1, headers=headers)
    if response.status_code == 200:
        print('Developer user 1 added')

    response = requests.post(url=signup, data=devuse2, headers=headers)
    if response.status_code == 200:
        print('Developer user 2 added')

    response = requests.post(url=signup, data=devuse3, headers=headers)
    if response.status_code == 200:
        print('Developer user 3 added')

    response = requests.post(url=signup, data=devuse4, headers=headers)
    if response.status_code == 200:
        print('Developer user 4 added')

    response = requests.post(url=signup, data=manageruser1, headers=headers)
    if response.status_code == 200:
        print('Manager user 1 added')

    response = requests.post(url=signup, data=manageruser2, headers=headers)
    if response.status_code == 200:
        print('Manager user 2 added')

def loginuser(username,password):
    login = url + '/login'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    logindata = json.dumps({'username':username,'password':password})
    response = requests.post(url=login, data=logindata, headers=headers)
    return response

def addproject(name,access_token):
    addproject = url + '/addproject'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer '+access_token
    }
    addprojectdata = json.dumps({'name':name})
    response = requests.post(url=addproject, data=addprojectdata, headers=headers)
    return response

def assignproject(projectID,developerID,access_token):
    assignproject = url + '/assignproject/'+ str(projectID)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer '+access_token
    }
    assignprojectdata = json.dumps({'developerID':developerID})
    response = requests.post(url=assignproject, data=assignprojectdata, headers=headers)
    return response

def projects(access_token):
    projects = url + '/projects'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer '+access_token
    }
    response = requests.get(url=projects,headers=headers)
    return response

def addtask(projectID,description,access_token):
    addtask = url + '/addtask/' + str(projectID)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer '+access_token
    }
    addtaskdata = json.dumps({'description':description})
    response = requests.post(url=addtask, data=addtaskdata, headers=headers)
    return response

def assigntask(taskID,developerID,access_token):
    assignproject = url + '/assigntask/'+ str(taskID)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer '+access_token
    }
    assigntaskdata = json.dumps({'developerID':developerID})
    response = requests.post(url=assignproject, data=assigntaskdata, headers=headers)
    return response

def mytasks(access_token):
    mytasks = url + '/mytasks'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer '+access_token
    }
    response = requests.get(url=mytasks,headers=headers)
    return response


#1--Migrating database and creating roles
print('\n Test 1 === Migrating database and creating roles')
developer, manager = db_data_setup()


#2--Creating 4 developers and 2 Project Manager
print('\n Test 2 === Creating 4 developers and 2 Project Manager')
createusers()

#3--Testing login one developr user
print('\n Test 3 === Testing login user devuser1')
response = loginuser('devuser1','123456')
if response.status_code == 200:
    print('\nLogin user devuser1 successfully and Token=')
    print(response.json()['access_token'])
    print('\n')

#4--Testing adding project by a Project Manager
print('\n Test 4 === Testing adding project')
response = loginuser('manageruser1','123456')
if response.status_code == 200:
    access_token = response.json()['access_token']
    response = addproject('Test project1 created by manageruser1',access_token)
    if response.status_code == 200:
        print('\nA project has added by manageruser1')

#5--Testing permission user can not add project
print('\n Test 5 === Testing permission user can not add project')
response = loginuser('devuser1','123456')
if response.status_code == 200:
    access_token = response.json()['access_token']
    response = addproject('Test project2 created by devuser1',access_token)
    if response.status_code == 403:
        print('\n User devuser1 could not add project due to permission')

#6--Testing assiging developer to project by project manager created the project
print('\n Test 6 == Testing assiging developer to project by project manager who created the project')
response = loginuser('manageruser1','123456')
if response.status_code == 200:
    access_token = response.json()['access_token']
    with app.app_context():
        devuser1 = User.query.filter_by(username='devuser1').first()
        project = Project.query.filter_by(name='Test project1 created by manageruser1').first()
    response = assignproject(project.id,devuser1.id,access_token)
    if response.status_code == 200:
        print('\n devuser1 1 was added to the project by manageruser1, who is the project manager')

#7--Testing mangeruser2, who is not the manager of project, cannot add devuser2 to the project due to permission
print('\n Test 7 == Testing mangeruser2, who is not the manager of project, cannot add devuser2 to the project due to permission')
response = loginuser('manageruser2','123456')
if response.status_code == 200:
    access_token = response.json()['access_token']
    with app.app_context():
        devuser2 = User.query.filter_by(username='devuser2').first()
        project = Project.query.filter_by(name='Test project1 created by manageruser1').first()
    response = assignproject(project.id,devuser2.id,access_token)
    if response.status_code == 403:
        print('\n manageruser2, who is not the manager of project, could not add devuser2 to the project due to permission')

#8--Testing devuser1, who is not project manager of project, cannot add devuser2 to the project due to permission
print('\n Test 8 == Testing devuser1, who is not project manager of project, cannot add devuser2 to the project due to permission')
response = loginuser('devuser1','123456')
if response.status_code == 200:
    access_token = response.json()['access_token']
    with app.app_context():
        devuser2 = User.query.filter_by(username='devuser2').first()
        project = Project.query.filter_by(name='Test project1 created by manageruser1').first()
    response = assignproject(project.id,devuser2.id,access_token)
    if response.status_code == 403:
        print('\n devuser1, who is not project manager of project, could not add devuser2 to the project due to permission')

#9--Testing Retrieve projects created by manageruser1
print('\n Test 9 == Testing Retrieve projects created by manageruser1')
response = loginuser('manageruser1','123456')
if response.status_code == 200:
    access_token = response.json()['access_token']
    response = projects(access_token)
    if response.status_code == 200:
        print('\n manageruser1, see its projects')
        print('\n')
        print(response.json())

#10--Testing adding tasks by project manager
print('\n Test 10 == Testing adding tasks by project manager manageruser1')
response = loginuser('manageruser1','123456')
if response.status_code == 200:
    access_token = response.json()['access_token']
    with app.app_context():
        project = Project.query.filter_by(name='Test project1 created by manageruser1').first()
    description = 'Task created by manageruser1 who is project manager'
    response = addtask(project.id,description,access_token)

    if response.status_code == 200:
        print('\n Task added by project manager manageruser1')

#11--Testing adding tasks by developer in a project
print('\n Test 10 == Testing adding tasks by developer in a project devuser1')
response = loginuser('devuser1','123456')
if response.status_code == 200:
    access_token = response.json()['access_token']
    with app.app_context():
        project = Project.query.filter_by(name='Test project1 created by manageruser1').first()
    description = 'Task created by devuser1 who is a developer and member of project'
    response = addtask(project.id,description,access_token)

    if response.status_code == 200:
        print('\n Task added by Developer devuser1 who is a member of project')

#11--Testing a project manager who is not a project manager of a project can not add task
print('\n Test 11 == Testing manageruser2 who is not a project manager of a project can not add task')
response = loginuser('manageruser2','123456')
if response.status_code == 200:
    access_token = response.json()['access_token']
    with app.app_context():
        project = Project.query.filter_by(name='Test project1 created by manageruser1').first()
    description = 'Task created by manageruser2 who is not project manager of project'
    response = addtask(project.id,description,access_token)

    if response.status_code == 403:
        print('\n manageruser2 who is not a project manager of a project could not not add task')

#12--Assigning task by project manager
print('\n Test 12 == Testing assigning task to developer devuser1 by project manager manageruser1')
response = loginuser('manageruser1','123456')
if response.status_code == 200:
    access_token = response.json()['access_token']
    with app.app_context():
        task = Task.query.filter_by(description='Task created by manageruser1 who is project manager').first()
        developer = User.query.filter_by(username='devuser1').first()
    response = assigntask(task.id,developer.id,access_token)

    if response.status_code == 200:
        print('\n Task assigned to devuser1 by manageruser1')

#13--Assigning task by developer
print('\n Test 13 == Testing assigning task to developer devuser1 by itself because it is task creator')
response = loginuser('devuser1','123456')
if response.status_code == 200:
    access_token = response.json()['access_token']
    with app.app_context():
        task = Task.query.filter_by(description='Task created by devuser1 who is a developer and member of project').first()
        developer = User.query.filter_by(username='devuser1').first()
    response = assigntask(task.id,developer.id,access_token)

    if response.status_code == 200:
        print('\n Task was assigned to devuser1 by devuser1 because the user created it')

#14--list of developer tasks
print("\n Test 14 == View test of devuser1's tasks")
response = loginuser('devuser1','123456')
if response.status_code == 200:
    access_token = response.json()['access_token']
    response = mytasks(access_token)

    if response.status_code == 200:
        print('\n devuser1, see its tasks')
        print('\n')
        print(response.json())
