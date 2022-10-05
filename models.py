from . import db
from flask_sqlalchemy import inspect

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    password = db.Column(db.Text, nullable=False)
    project = db.relationship('Project', backref="users")
    task = db.relationship('Task', backref="users")
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)

class UserRole(db.Model):
    __tablename__ = 'user_role'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id'),
        nullable=False
    )
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)

    user = db.relationship(
        'User', backref=db.backref(
            'user_role_entries',
            cascade='all,delete-orphan'
        )
    )
    role = db.relationship(
        'Role', backref=db.backref(
            'user_role',
            cascade='all,delete-orphan'
        )
    )

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    task = db.relationship('Task', backref="projects")
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)

class DeveloperProject(db.Model):
    __tablename__ = 'developer_project'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    developer_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    project_id = db.Column(
        db.Integer,
        db.ForeignKey('projects.id'),
        nullable=False
    )
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)

    user = db.relationship(
        'User', backref=db.backref(
            'developer_project_entries',
            cascade='all,delete-orphan'
        )
    )
    project = db.relationship(
        'Project', backref=db.backref(
            'developer_project',
            cascade='all,delete-orphan'
        )
    )
class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    description = db.Column(db.String(128), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)

class UserTask(db.Model):
    __tablename__ = 'user_task'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    task_id = db.Column(
        db.Integer,
        db.ForeignKey('tasks.id'),
        nullable=False
    )
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)

    user = db.relationship(
        'User', backref=db.backref(
            'user_task_entries',
            cascade='all,delete-orphan'
        )
    )
    task = db.relationship(
        'Task', backref=db.backref(
            'user_task',
            cascade='all,delete-orphan'
        )
    )
