import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy.orm import Session

from conf.db import SessionLocal
from entity.models import Student, Grade, Subject, Teacher, Group

fake = Faker("uk_UA")
Faker.seed(42)

def seed_database()-> None:
    """Наповнює БД випадковими даними:
        3 групи; 3–5 викладачів; 5–8 предметів; 30–50 студентів;
        у кожного студента до 20 оцінок по різних предметах.
        """
    with SessionLocal() as session:
        try:
            groups = create_groups(session)
            teachers = create_teachers(session)
            subjects = create_subjects(session, teachers)
            students = create_students(session, groups)
            create_grades(session, students, subjects)

            session.commit()
            print("Database seeded successfully.")
        except Exception as e:
            session.rollback()
            raise

def create_groups(session: Session) -> list[Group]:
    group_name = ["MCS01", "MDS01", "MVS01"]
    groups = []
    for name in group_name:
        group = Group(name=name)
        session.add(group)
        groups.append(group)
    session.flush()
    return groups

def create_teachers(session: Session) -> list[Teacher]:
    teachers = []
    for i in range(5):
        teacher = Teacher(
            first_name=fake.first_name(),
            second_name=fake.last_name(),
            email=fake.unique.email(),
            phone=fake.phone_number(),
        )
        session.add(teacher)
        teachers.append(teacher)
    session.flush()
    return teachers

def create_subjects(session: Session, teachers: list) -> list[Subject]:
    subject_names = [
        "Python. Core",
        "Python. Web",
        "Design Thinking",
        "Algorithms",
        "Algorithms. Advanced",
        "JS + React",
        "Node.js",
        "Databases"
    ]
    subjects = []
    for name in subject_names:
        subject = Subject(name=name, teacher=random.choice(teachers))
        session.add(subject)
        subjects.append(subject)
    session.flush()
    return subjects

def create_students(session: Session, groups: list) -> list[Student]:
    students = []
    for i in range(50):
        student = Student(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            phone=fake.phone_number(),
            group=random.choice(groups)
        )
        session.add(student)
        students.append(student)
    session.flush()
    return students

def create_grades(session: Session, students: list, subjects: list) -> None:
    start_date = datetime.now() - timedelta(days=180)
    end_date = datetime.now()

    for student in students:
        num_grades = random.randint(10, 20)
        for _ in range(num_grades):
            subject = random.choice(subjects)
            grade = Grade(
                student_id=student.id,
                subject_id=subject.id,
                grade=random.randint(60, 100),
                date_received=start_date + timedelta(days=random.randint(0, (end_date-start_date).days))
            )
            session.add(grade)
    session.flush()

if __name__ == "__main__":
    seed_database()