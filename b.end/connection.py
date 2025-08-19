from sqlalchemy import create_engine, Column, Integer, String, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists
from setting import pgsettings as setting
from urllib.parse import quote_plus
from sqlalchemy.orm import declarative_base
from setting import pgsettings as setting


Base = declarative_base()

def get_engine(user, password, host, port, db):
    password = quote_plus(password)  
    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    print(" Trying to connect to URL:", url)

    if not database_exists(url):
        raise Exception("Bad URL or database does not exist")

    engine = create_engine(url)
    return engine


def get_engine_from_settings():
    required_keys = ['pguser', 'pgpasswd', 'pghost', 'pgport', 'pgdb']
    
    if not all(key in setting for key in required_keys):
        print("Setting keys found:", list(setting.keys()))
        raise Exception("Bad config: missing keys")

    password_encoded = setting['pgpasswd']
    return get_engine(
        setting['pguser'],
        password_encoded,
        setting['pghost'],
        setting['pgport'],
        setting['pgdb']
    )


def get_session():
    engine = get_engine_from_settings()
    print(f"Connecting to: {engine.url}")
    Session = sessionmaker(bind=engine)
    return Session()

# Define your model
class Student(Base):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    age = Column(Integer)
    grade = Column(String(50))

# Create tables
Base.metadata.create_all(get_engine_from_settings())

# Create session
session = get_session()

# Add students
student1 = Student(name="jay", age=25, grade='OG')
session.add(student1)
session.commit()

student2 = Student(name="Adi", age=22, grade='A')
student3 = Student(name="vja", age=26, grade='ultra OG')
session.add_all([student2, student3])
session.commit()

# Query all students
students = session.query(Student).all()
for student in students:
    print(student.name, student.age)

# Query ordered by name
students = session.query(Student).order_by(Student.name).all()
for student in students:
    print(student.name, student.age, student.grade)

# Query with filter or_
student = session.query(Student).filter(Student.name == "jay").first()
print(student.name, student.age)

students = session.query(Student).filter(or_(Student.name == "jay", Student.name == "Adi")).all()
for stu in students:
    print(stu.name, stu.age)

# Count students
student_count = session.query(Student).count()
print(f"Student count: {student_count}")

# Update student
student_to_update = session.query(Student).filter(Student.name == "jay").first()
if student_to_update:
    student_to_update.name = "Adi"
    session.commit()

# Print after update
students = session.query(Student).all()
for student in students:
    print(student.name, student.age)

# Delete a student
student_to_delete = session.query(Student).filter(Student.name == "jay").first()
if student_to_delete:
    session.delete(student_to_delete)
    session.commit()

# Print after delete
students = session.query(Student).all()
for stu in students:
    print(stu.name, stu.age)
