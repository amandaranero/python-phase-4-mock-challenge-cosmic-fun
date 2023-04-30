from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Scientist, Planet, Mission

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

class Scientists(Resource):
    def get(self):
        scientists = [scientist.to_dict() for scientist in Scientist.query.all()]

        response = make_response(
            scientists,
            200
        )

        return response

    def post(self):
        try:
            data = request.get_json()
            new_scientist = Scientist(
                name = data['name'],
                field_of_study = data['field_of_study'],
                avatar = data['avatar']
            )

            db.session.add(new_scientist)
            db.session.commit()

            response = make_response(
                new_scientist.to_dict(),
                201
            )
            return response
        except Exception as ex:
            return make_response({
                'errors': [ex.__str__()]
            },400)

api.add_resource(Scientists, '/scientists')

class ScientistByID(Resource):
    def get(self,id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return make_response({
                'error': 'Scientist not found'
            }, 404)

        response = make_response(
            scientist.to_dict(rules=('planets',))
        )

        return response

    def patch(self, id):
        data = request.get_json()
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return make_response({
                'error': 'Scientist not found'
            }, 404)
        try:
            for attr in data:
                setattr(scientist, attr, data[attr])

            db.session.add(scientist)
            db.session.commit()

            response = make_response(
                scientist.to_dict(),
                202
            )
        except Exception as ex:
            return make_response({
                'error': [ex.__str__()]
            }, 400)

    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return make_response({
                'error': 'Scientist not found'
            }, 404)
        
        db.session.delete(scientist)
        db.session.commit()

        return make_response({
            'message': 'Scientist was deleted'
        }, 202)

api.add_resource(ScientistByID, '/scientists/<int:id>')

class Planets(Resource):
    def get(self):
        planets = [planets.to_dict() for planets in Planet.query.all()]
        response = make_response(
            planets,
            200
        )
        return response

api.add_resource(Planets, '/planets')

class Missions(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_mission = Mission(
                name = data['name'],
                scientist_id = data['scientist_id'],
                planet_id = data['planet_id']
            )

            db.session.add(new_mission)
            db.session.commit()

            return make_response(
                new_mission.planet.to_dict(),
                201
            )
        except Exception as ex:
            return make_response({
                'errors': [ex.__str__()]
            }, 400)

api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
