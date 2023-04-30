from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)



class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable = False)
    field_of_study = db.Column(db.String, nullable = False)
    avatar = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    missions = db.relationship('Mission', backref = 'scientist', cascade = "all, delete, delete-orphan")
    planets = association_proxy('missions','planet')

    serialize_rules = ('-created_at', '-updated_at', '-missions')

    @validates('name')
    def validates_name(self,key,value):
        if not value:
            return ValueError('Must have name')
        return value

    @validates('field_of_study')
    def validates_field_of_study(self,key,value):
        if not value:
            return ValueError('Must have field of study')
        return value

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    @validates('name')
    def validates_name(self,key,value):
        if not value:
            return ValueError('Must add a mission')
        return value

    @validates('scientist_id')
    def validates_scientist(self, key, value):
        scientists = [scientist.id for scientist in Scientist.query.all()]
        if not value:
            return ValueError('Must have scientist')
        elif value not in scientists:
            return ValueError('That scientist does not exist')
        return value

    @validates('planet_id')
    def validates_planet(self,key,value):
        planets = [planet.id for planet in Planet.query.all()]
        if not value:
            return ValueError('Must have planet')
        elif value not in planets:
            return ValueError('That is not a planet')
        return value



class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.String)
    nearest_star = db.Column(db.String)
    image = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    missions = db.relationship('Mission', backref = 'planet')
    scientists = association_proxy('missions', 'scientist')

    serialize_rules = ('-created_at', '-updated_at', '-missions')
