from sqlalchemy import text, create_engine
from sqlalchemy.orm import Session
from pprint import pprint

# Assume `engine` is an SQLAlchemy engine instance
engine = create_engine("postgresql+psycopg2://iomiras:@localhost:5432/asgn3")
session = Session(engine)

# List all diseases caused by "bacteria" that were discovered before 2020.
stmt1 = text("""
    SELECT Disease.disease_code, Disease.description 
    FROM Disease 
    JOIN Discover ON Disease.disease_code = Discover.disease_code
    WHERE Disease.pathogen = 'bacteria' AND Discover.first_enc_date < '2020-01-01';
""")
diseases_bacteria = session.execute(stmt1).fetchall()
pprint(diseases_bacteria)

# Retrieve the names and degrees of doctors who are not specialized in “infectious diseases.”
stmt2 = text("""
    SELECT DISTINCT Users.name, Users.surname, Doctor.degree
    FROM Users
    JOIN Doctor ON Users.email = Doctor.email
    LEFT JOIN Specialize ON Doctor.email = Specialize.email
    WHERE Doctor.email NOT IN (
        SELECT email 
        FROM Specialize
        LEFT JOIN DiseaseType ON DiseaseType.id = Specialize.id
        WHERE DiseaseType.description = 'Infectious Diseases'
    );
""")
doctors_not_infectious = session.execute(stmt2).fetchall()
pprint(doctors_not_infectious)

# List the name, surname and degree of doctors who are specialized in more than 2 disease types.
stmt3 = text("""
    SELECT Users.name, Users.surname, Doctor.degree
    FROM Users
    JOIN Doctor ON Users.email = Doctor.email
    JOIN Specialize ON Doctor.email = Specialize.email
    GROUP BY Users.email, Doctor.degree
    HAVING COUNT(Specialize.id) > 2;
""")
doctors_specializing_in_multiple = session.execute(stmt3).fetchall()
pprint(doctors_specializing_in_multiple)

# List countries and the average salary of doctors specialized in "virology."
stmt4 = text("""
    SELECT Users.cname, ROUND(AVG(Users.salary), 3) AS avg_salary
    FROM Users
    JOIN Doctor ON Users.email = Doctor.email
    JOIN Specialize ON Doctor.email = Specialize.email
    WHERE Specialize.id = (SELECT id FROM DiseaseType WHERE description = 'Virology')
    GROUP BY Users.cname;
""")
avg_salary_virology = session.execute(stmt4).fetchall()
pprint(avg_salary_virology)

# Find departments with public servants reporting "covid-19" cases across multiple countries.
stmt5 = text("""
    SELECT PublicServant.department, COUNT(DISTINCT PublicServant.email) AS num_emp
    FROM PublicServant
    JOIN Record ON PublicServant.email = Record.email
    WHERE Record.disease_code = (SELECT disease_code FROM Disease WHERE description = 'covid-19')
    GROUP BY PublicServant.department
    HAVING COUNT(DISTINCT Record.cname) > 1;
""")
departments_with_covid_cases = session.execute(stmt5).fetchall()
pprint(departments_with_covid_cases)

# Double the salary of public servants who have recorded more than three “covid-19” patients.
stmt6a = text("""
    SELECT Users.email, Users.name, Users.surname, Users.salary
    FROM PublicServant
    JOIN Users ON PublicServant.email = Users.email
    JOIN Record ON PublicServant.email = Record.email
    WHERE Record.disease_code = (SELECT disease_code FROM Disease WHERE description = 'covid-19')
    GROUP BY Users.email, Users.name, Users.surname, Users.salary
    HAVING SUM(Record.total_patients) > 3;
""")
public_servants_covid = session.execute(stmt6a).fetchall()
pprint(public_servants_covid)

stmt6b = text("""
    UPDATE Users
    SET salary = salary * 2
    WHERE email IN (
        SELECT PublicServant.email
        FROM PublicServant
        JOIN Record ON PublicServant.email = Record.email
        WHERE Record.disease_code = (SELECT disease_code FROM Disease WHERE description = 'covid-19')
        GROUP BY PublicServant.email
        HAVING SUM(Record.total_patients) > 3
    );
""")
session.execute(stmt6b)

# Delete users whose name contains the substring “bek” or “gul.”
stmt7a = text("""
    SELECT * FROM Users
    WHERE name LIKE '%bek%' OR name LIKE '%gul%';
""")
users_with_name_substrings = session.execute(stmt7a).fetchall()
pprint(users_with_name_substrings)

stmt7b = text("""
    DELETE FROM Users
    WHERE name LIKE '%bek%' OR name LIKE '%gul%';
""")
session.execute(stmt7b)

# Create a primary indexing on the “email” field in the Users table.
stmt8a = text("""
    CREATE UNIQUE INDEX idx_users_email ON Users (email);
""")
session.execute(stmt8a)

# Create a secondary indexing on the “disease code” field in the Disease table.
stmt9a = text("""
    CREATE INDEX idx_disease_code ON Disease (disease_code);
""")
session.execute(stmt9a)

# List the top 2 countries with the highest number of total patients recorded.
stmt10 = text("""
    SELECT Record.cname, SUM(Record.total_patients) AS total_patients
    FROM Record
    GROUP BY Record.cname
    ORDER BY total_patients DESC
    LIMIT 2;
""")
top_countries_patients = session.execute(stmt10).fetchall()
pprint(top_countries_patients)

# Calculate the total number of patients who have covid-19 disease.
stmt11 = text("""
    SELECT SUM(Record.total_patients) AS total_covid_patients
    FROM Record
    JOIN Disease ON Record.disease_code = Disease.disease_code
    WHERE Disease.description = 'covid-19';
""")
total_covid_patients = session.execute(stmt11).scalar()
pprint(total_covid_patients)

# Create a view with all patients’ names and surnames along with their respective diseases.
stmt12a = text("""
    CREATE VIEW PatientsDiseases AS
    SELECT Users.name, Users.surname, Disease.description AS disease
    FROM Users
    JOIN PatientDisease ON Users.email = PatientDisease.email
    JOIN Disease ON PatientDisease.disease_code = Disease.disease_code;
""")
session.execute(stmt12a)

# Retrieve a list of all patients’ full names along with the diseases they have been diagnosed with.
stmt13 = text("""
    SELECT name, surname, disease 
    FROM PatientsDiseases;
""")
all_patients_diseases = session.execute(stmt13).fetchall()
pprint(stmt13)
