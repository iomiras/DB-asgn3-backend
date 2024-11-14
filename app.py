from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
# CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Country(db.Model):
    # __tablename__ = 'Country'
    cname = db.Column(db.String(50), primary_key=True)
    population = db.Column(db.BigInteger)

    def serialize(self):
        return {
            'cname': self.cname,
            'population': self.population
        }

class Users(db.Model):
    email = db.Column(db.String(60), primary_key=True)
    name = db.Column(db.String(30))
    surname = db.Column(db.String(40))
    salary = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    cname = db.Column(db.String(50), db.ForeignKey('country.cname', ondelete='CASCADE', onupdate='CASCADE'))

    def serialize(self):
        return {
            'email': self.email,
            'name': self.name,
            'surname': self.surname,
            'salary': self.salary,
            'phone': self.phone,
            'cname': self.cname
        }

class Doctor(db.Model):
    # __tablename__ = 'Doctor'
    email = db.Column(db.String(60), db.ForeignKey('users.email', ondelete='CASCADE', onupdate='CASCADE'))
    degree = db.Column(db.String(20))
    __table_args__ = (
        db.PrimaryKeyConstraint('email'),
    )

    def serialize(self):
        return {
            'email': self.email,
            'degree': self.degree
        }

class PublicServant(db.Model):
    __tablename__ = 'publicservant'
    email = db.Column(db.String(60), db.ForeignKey('users.email', ondelete='CASCADE', onupdate='CASCADE'))
    department = db.Column(db.String(50))
    __table_args__ = (
        db.PrimaryKeyConstraint('email'),
    )

    def serialize(self):
        return {
            'email': self.email,
            'department': self.department
        }

class Patients(db.Model):
    # __tablename__ = 'patients'
    email = db.Column(db.String(60), db.ForeignKey('users.email', ondelete='CASCADE', onupdate='CASCADE'))
    __table_args__ = (
        db.PrimaryKeyConstraint('email'),
    )

    def serialize(self):
        return {
            'email': self.email
        }

class DiseaseType(db.Model):
    __tablename__ = 'diseasetype'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(140))

    def serialize(self):
        return {
            'id': self.id,
            'description': self.description
        }

class Specialize(db.Model):
    # __tablename__ = 'Specialize'
    id = db.Column(db.Integer, db.ForeignKey('diseasetype.id', ondelete='CASCADE', onupdate='CASCADE'))
    email = db.Column(db.String(60), db.ForeignKey('doctor.email', ondelete='CASCADE', onupdate='CASCADE'))
    __table_args__ = (
        db.PrimaryKeyConstraint('id', 'email'),
    )

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email
        }

class Disease(db.Model):
    discoveries = db.relationship('Discover', backref='disease', lazy=True)
    disease_code = db.Column(db.String(50), primary_key=True)
    pathogen = db.Column(db.String(20))
    description = db.Column(db.String(140))
    id = db.Column(db.Integer, db.ForeignKey('diseasetype.id', ondelete='CASCADE', onupdate='CASCADE'))

    def serialize(self):
        return {
            'disease_code': self.disease_code,
            'pathogen': self.pathogen,
            'description': self.description,
            'id': self.id
        }

class Discover(db.Model):
    # __tablename__ = 'Discover'
    cname = db.Column(db.String(50), db.ForeignKey('country.cname', ondelete='CASCADE', onupdate='CASCADE'))
    disease_code = db.Column(db.String(50), db.ForeignKey('disease.disease_code', ondelete='CASCADE', onupdate='CASCADE'))
    first_enc_date = db.Column(db.Date)
    __table_args__ = (
        db.PrimaryKeyConstraint('disease_code'),
    )

    def serialize(self):
        return {
            'cname': self.cname,
            'disease_code': self.disease_code,
            'first_enc_date': self.first_enc_date
        }

class PatientDisease(db.Model):
    __tablename__ = 'patientdisease'
    email = db.Column(db.String(60), db.ForeignKey('users.email', ondelete='CASCADE', onupdate='CASCADE'))
    disease_code = db.Column(db.String(50), db.ForeignKey('disease.disease_code', ondelete='CASCADE', onupdate='CASCADE'))

    __table_args__ = (
        db.PrimaryKeyConstraint('email', 'disease_code'),
    )

    def serialize(self):
        return {
            'email': self.email,
            'disease_code': self.disease_code
        }

class Record(db.Model):
    # __tablename__ = 'Record'
    email = db.Column(db.String(60), db.ForeignKey('publicservant.email', ondelete='CASCADE', onupdate='CASCADE'))
    cname = db.Column(db.String(50), db.ForeignKey('country.cname', ondelete='CASCADE', onupdate='CASCADE'))
    disease_code = db.Column(db.String(50), db.ForeignKey('disease.disease_code', ondelete='CASCADE', onupdate='CASCADE'))
    total_deaths = db.Column(db.Integer)
    total_patients = db.Column(db.Integer)

    __table_args__ = (
        db.PrimaryKeyConstraint('email', 'cname', 'disease_code'),
    )

    def serialize(self):
        return {
            'email': self.email,
            'cname': self.cname,
            'disease_code': self.disease_code,
            'total_deaths': self.total_deaths,
            'total_patients': self.total_patients
        }


# CRUD Operations
# Country CRUD
@app.route('/api/countries/', methods=['GET', 'POST'])
def countries():
    if request.method == 'GET':
        countries = Country.query.all()
        return jsonify([country.serialize() for country in countries])
    elif request.method == 'POST':
        data = request.get_json()
        country = Country(
            cname=data['cname'],
            population=data['population']
        )
        db.session.add(country)
        db.session.commit()
        return jsonify(country.serialize()), 201

@app.route('/api/countries/<cname>', methods=['PUT', 'DELETE'])
def country(cname):
    country = Country.query.get(cname)
    if request.method == 'PUT':
        data = request.get_json()
        country.cname = data['cname']
        country.population = data['population']
        db.session.commit()
        return jsonify(country.serialize())
    elif request.method == 'DELETE':
        db.session.delete(country)
        db.session.commit()
        return jsonify({'message': 'Country deleted'}), 204

# Users CRUD
@app.route('/api/users/', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        users = Users.query.all()
        return jsonify([user.serialize() for user in users])
    elif request.method == 'POST':
        data = request.get_json()
        print("country =", data['cname'])
        user = Users(
            email=data['email'],
            name=data['name'],
            surname=data['surname'],
            salary=data['salary'],
            phone=data['phone'],
            cname=data['cname']
        )
        db.session.add(user)
        db.session.commit()
        return jsonify(user.serialize()), 201

@app.route('/api/users/<email>', methods=['PUT', 'DELETE'])
def user(email):
    user = Users.query.get(email)
    if request.method == 'PUT':
        data = request.get_json()
        user.email = data['email']
        user.name = data['name']
        user.surname = data['surname']
        user.salary = data['salary']
        user.phone = data['phone']
        user.cname = data['cname']
        db.session.commit()
        return jsonify(user.serialize())
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted'}), 204

# Doctor CRUD
@app.route('/api/doctors/', methods=['GET', 'POST'])
def doctors():
    if request.method == 'GET':
        doctors = Doctor.query.all()
        return jsonify([doctor.serialize() for doctor in doctors])
    elif request.method == 'POST':
        data = request.get_json()
        doctor = Doctor(
            email=data['email'],
            degree=data['degree']
        )
        db.session.add(doctor)
        db.session.commit()
        return jsonify(doctor.serialize()), 201

@app.route('/api/doctors/<email>', methods=['PUT', 'DELETE'])
def doctor(email):
    doctor = Doctor.query.get(email)
    if request.method == 'PUT':
        data = request.get_json()
        doctor.email = data['email']
        doctor.degree = data['degree']
        db.session.commit()
        return jsonify(doctor.serialize())
    elif request.method == 'DELETE':
        db.session.delete(doctor)
        db.session.commit()
        return jsonify({'message': 'Doctor deleted'}), 204

# PublicServant CRUD
@app.route('/api/public-servants/', methods=['GET', 'POST'])
def public_servants():
    if request.method == 'GET':
        public_servants = PublicServant.query.all()
        return jsonify([public_servant.serialize() for public_servant in public_servants])
    elif request.method == 'POST':
        data = request.get_json()
        public_servant = PublicServant(
            email=data['email'],
            department=data['department']
        )
        db.session.add(public_servant)
        db.session.commit()
        return jsonify(public_servant.serialize()), 201

@app.route('/api/public-servants/<email>', methods=['PUT', 'DELETE'])
def public_servant(email):
    public_servant = PublicServant.query.get(email)
    if request.method == 'PUT':
        data = request.get_json()
        public_servant.email = data['email']
        public_servant.department = data['department']
        db.session.commit()
        return jsonify(public_servant.serialize())
    elif request.method == 'DELETE':
        db.session.delete(public_servant)
        db.session.commit()
        return jsonify({'message': 'Public servant deleted'}), 204

# Patients CRUD
@app.route('/api/patients/', methods=['GET', 'POST'])
def patients():
    if request.method == 'GET':
        patients = Patients.query.all()
        return jsonify([patient.serialize() for patient in patients])
    elif request.method == 'POST':
        data = request.get_json()
        patient = Patients(
            email=data['email']
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify(patient.serialize()), 201

@app.route('/api/patients/<email>', methods=['PUT', 'DELETE'])
def patient(email):
    patient = Patients.query.get(email)
    if request.method == 'PUT':
        data = request.get_json()
        patient.email = data['email']
        db.session.commit()
        return jsonify(patient.serialize())
    elif request.method == 'DELETE':
        db.session.delete(patient)
        db.session.commit()
        return jsonify({'message': 'Patient deleted'}), 204

# DiseaseType CRUD
@app.route('/api/disease-types/', methods=['GET', 'POST'])
def disease_types():
    if request.method == 'GET':
        disease_types = DiseaseType.query.all()
        return jsonify([disease_type.serialize() for disease_type in disease_types])
    elif request.method == 'POST':
        data = request.get_json()
        disease_type = DiseaseType(
            id=data['id'],
            description=data['description']
        )
        db.session.add(disease_type)
        db.session.commit()
        return jsonify(disease_type.serialize()), 201

@app.route('/api/disease-types/<id>', methods=['PUT', 'DELETE'])
def disease_type(id):
    disease_type = DiseaseType.query.get(id)
    if request.method == 'PUT':
        data = request.get_json()
        disease_type.id = data['id']
        disease_type.description = data['description']
        db.session.commit()
        return jsonify(disease_type.serialize())
    elif request.method == 'DELETE':
        db.session.delete(disease_type)
        db.session.commit()
        return jsonify({'message': 'Disease type deleted'}), 204

# Specialize CRUD
@app.route('/api/specializations/', methods=['GET', 'POST'])
def specializations():
    if request.method == 'GET':
        specializations = Specialize.query.all()
        return jsonify([specialization.serialize() for specialization in specializations])
    elif request.method == 'POST':
        data = request.get_json()
        specialization = Specialize(
            id=data['id'],
            email=data['email']
        )
        db.session.add(specialization)
        db.session.commit()
        return jsonify(specialization.serialize()), 201

@app.route('/api/specializations/<id>/<email>', methods=['PUT', 'DELETE'])
def specialization(id, email):
    specialization = Specialize.query.get((id, email))
    if request.method == 'PUT':
        data = request.get_json()
        specialization.id = data['id']
        specialization.email = data['email']
        db.session.commit()
        return jsonify(specialization.serialize())
    elif request.method == 'DELETE':
        db.session.delete(specialization)
        db.session.commit()
        return jsonify({'message': 'Specialization deleted'}), 204

# Disease CRUD
@app.route('/api/diseases/', methods=['GET', 'POST'])
def diseases():
    if request.method == 'GET':
        diseases = Disease.query.all()
        return jsonify([disease.serialize() for disease in diseases])
    elif request.method == 'POST':
        data = request.get_json()
        disease = Disease(
            disease_code=data['disease_code'],
            pathogen=data['pathogen'],
            description=data['description'],
            id=data['id']
        )
        db.session.add(disease)
        db.session.commit()
        return jsonify(disease.serialize()), 201

@app.route('/api/diseases/<disease_code>', methods=['PUT', 'DELETE'])
def disease(disease_code):
    disease = Disease.query.get(disease_code)
    if request.method == 'PUT':
        data = request.get_json()
        disease.disease_code = data['disease_code']
        disease.pathogen = data['pathogen']
        disease.description = data['description']
        disease.id = data['id']
        db.session.commit()
        return jsonify(disease.serialize())
    elif request.method == 'DELETE':
        db.session.delete(disease)
        db.session.commit()
        return jsonify({'message': 'Disease deleted'}), 204

# Discover CRUD
@app.route('/api/discoveries/', methods=['GET', 'POST'])
def discoveries():
    if request.method == 'GET':
        discoveries = Discover.query.all()
        return jsonify([discovery.serialize() for discovery in discoveries])
    elif request.method == 'POST':
        data = request.get_json()
        discovery = Discover(
            cname=data['cname'],
            disease_code=data['disease_code'],
            first_enc_date=data['first_enc_date']
        )
        db.session.add(discovery)
        db.session.commit()
        return jsonify(discovery.serialize()), 201

@app.route('/api/discoveries/<disease_code>', methods=['PUT', 'DELETE'])
def discovery(disease_code):
    discovery = Discover.query.get(disease_code)
    if request.method == 'PUT':
        data = request.get_json()
        discovery.cname = data['cname']
        discovery.disease_code = data['disease_code']
        discovery.first_enc_date = data['first_enc_date']
        db.session.commit()
        return jsonify(discovery.serialize())
    elif request.method == 'DELETE':
        db.session.delete(discovery)
        db.session.commit()
        return jsonify({'message': 'Discovery deleted'}), 204

# PatientDisease CRUD
@app.route('/api/patient-diseases/', methods=['GET', 'POST'])
def patient_diseases():
    if request.method == 'GET':
        patient_diseases = PatientDisease.query.all()
        return jsonify([patient_disease.serialize() for patient_disease in patient_diseases])
    elif request.method == 'POST':
        data = request.get_json()
        patient_disease = PatientDisease(
            email=data['email'],
            disease_code=data['disease_code']
        )
        db.session.add(patient_disease)
        db.session.commit()
        return jsonify(patient_disease.serialize()), 201

@app.route('/api/patient-diseases/<email>/<disease_code>', methods=['PUT', 'DELETE'])
def patient_disease(email, disease_code):
    patient_disease = PatientDisease.query.get((email, disease_code))
    if request.method == 'PUT':
        data = request.get_json()
        patient_disease.email = data['email']
        patient_disease.disease_code = data['disease_code']
        db.session.commit()
        return jsonify(patient_disease.serialize())
    elif request.method == 'DELETE':
        db.session.delete(patient_disease)
        db.session.commit()
        return jsonify({'message': 'Patient-disease relationship deleted'}), 204

# Record CRUD
@app.route('/api/records/', methods=['GET', 'POST'])
def records():
    if request.method == 'GET':
        records = Record.query.all()
        return jsonify([record.serialize() for record in records])
    elif request.method == 'POST':
        data = request.get_json()
        record = Record(
            email=data['email'],
            cname=data['cname'],
            disease_code=data['disease_code'],
            total_deaths=data['total_deaths'],
            total_patients=data['total_patients']
        )
        db.session.add(record)
        db.session.commit()
        return jsonify(record.serialize()), 201

@app.route('/api/records/<email>/<cname>/<disease_code>', methods=['PUT', 'DELETE'])
def record(email, cname, disease_code):
    record = Record.query.get((email, cname, disease_code))
    if request.method == 'PUT':
        data = request.get_json()
        record.email = data['email']
        record.cname = data['cname']
        record.disease_code = data['disease_code']
        record.total_deaths = data['total_deaths']
        record.total_patients = data['total_patients']
        db.session.commit()
        return jsonify(record.serialize())
    elif request.method == 'DELETE':
        db.session.delete(record)
        db.session.commit()
        return jsonify({'message': 'Record deleted'}), 204

if __name__ == "__main__":
    app.run(debug=True)