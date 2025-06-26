import random
from datetime import datetime, timedelta
from contextlib import contextmanager
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Student, Group, Teacher, Subject, Grade
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(
    bind=engine
)

fake = Faker()

@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def reset_database():
    with get_session() as session:
        session.query(Grade).delete()
        session.query(Subject).delete()
        session.query(Student).delete()
        session.query(Teacher).delete()
        session.query(Group).delete()

def create_groups() -> list[int]:
    with get_session() as session:
        groups = []
        group_names = ["Computer Science", "Maths", "PythonWeb"]

        for name in group_names:
            group = Group(name=name)
            session.add(group)
            groups.append(group)

        session.flush()
        group_ids = [group.id for group in groups]
        return group_ids

def create_teachers() -> list[int]:
    with get_session() as session:
        teachers = []
        num_teachers = random.randint(3, 5)

        for _ in range(num_teachers):
            teacher = Teacher(name=fake.name())
            session.add(teacher)
            teachers.append(teacher)

        session.flush()
        teacher_ids = [teacher.id for teacher in teachers]
        return teacher_ids

def create_subjects(teachers: list[int]) -> list[int]:
    with get_session() as session:
        subjects = []
        subject_names = [
            "Python Core",
            "JS",
            "Python Advanced",
            "Cloud Computing",
            "Web Basics",
            "Algorithms and Data Structures",
            "Web Development: React",
            "UI/UX Design"
            ]

        num_subjects = random.randint(5, 8)
        selected_subjects = random.sample(subject_names, num_subjects)

        for subject_name in selected_subjects:
            teacher = random.choice(teachers)
            subject = Subject(name=subject_name, teacher_id=teacher)
            session.add(subject)
            subjects.append(subject)

        session.flush()
        subject_ids = [subject.id for subject in subjects]
        return subject_ids

def create_students(group_ids: list[int]) -> list[int]:
    with get_session() as session:
        students = []
        num_students = random.randint(30, 50)

        groups = session.query(Group).filter(Group.id.in_(group_ids)).all()

        for _ in range(num_students):
            student = Student(name=fake.name())

            student_groups = random.sample(groups, random.randint(1, 2))
            student.groups = student_groups

            session.add(student)
            students.append(student)

        session.flush()
        student_ids = [student.id for student in students]
        return student_ids

def create_grades(students: list[int], subjects: list[int]):
    with get_session() as session:
        for student in students:
            num_grades = random.randint(5, 20)

            for _ in range(num_grades):
                subject = random.choice(subjects)
                grade_value = round(random.uniform(0.10, 1.00), 2)

                days_ago = random.randint(1, 180)
                grade_date = datetime.now() - timedelta(days=days_ago)

                grade = Grade(
                    grade = grade_value,
                    date_of = grade_date,
                    student_id = student,
                    subject_id = subject
                )

                session.add(grade)

def seed_database():
    reset_database()

    groups = create_groups()
    if not groups:
        print("❌ Failed to create groups. Stopping")
        return
    print("✅ Created groups")

    teachers = create_teachers()
    if not teachers:
        print("❌ Failed to create teachers. Stopping")
        return
    print("✅ Created teachers")

    subjects = create_subjects(teachers)
    if not subjects:
        print("❌ Failed to create subjects. Stopping")
        return
    print("✅ Created subjects")

    students = create_students(groups)
    if not students:
        print("❌ Failed to create students. Stopping")
        return
    print("✅ Created students")

    create_grades(students, subjects)
    print("✅ Created grades")

if __name__ == "__main__":
    seed_database()
