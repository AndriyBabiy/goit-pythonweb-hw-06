from contextlib import contextmanager
import random

from sqlalchemy import create_engine, func, desc, cast, Numeric, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from config import DATABASE_URL
from models import Student, Group, Teacher, Subject, Grade, groups_association_table

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@contextmanager
def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()

def random_elem(elem):
    with get_session() as session:
        result = (
            session.query(
                elem.name.label('teacher_name')
            )
            .distinct()
            .all()
        )
        return random.choice(result).teacher_name

def select_1():
    """
    Find the 5 students with the greatest average grade from all subjects
    """
    with get_session() as session:
        result = (
            session.query(
                Student.name,
                func.round(cast(func.avg(Grade.grade), Numeric), 2).label("avg_grade")
            )
            .join(Grade)
            .group_by(Student.id, Student.name)
            .order_by(desc("avg_grade"))
            .limit(5)
            .all()
        )
        return result

def select_2(subject_name: str = random_elem(Subject)):
    """
    Find the student with the highest average grade for a specific subject
    """
    with get_session() as session:
        result = (
            session.query(
                Student.name,
                Subject.name.label("subject_name"),
                func.round(cast(func.avg(Grade.grade), Numeric), 2).label("avg_grade")
            )
            .select_from(Student)
            .join(Grade)
            .join(Subject)
            .filter(Subject.name == subject_name)
            .group_by(Student.id, Student.name, Subject.name)
            .order_by(desc('avg_grade'))
            .limit(1)
            .all()
        )
        return result

def select_3(subject_name: str = random_elem(Subject)):
    """
    Find the average grade for a group for a specific subject
    """
    with get_session() as session:
        result = (
            session.query(
                Group.name.label('group_name'),
                Subject.name.label('subject_name'),
                func.round(cast(func.avg(Grade.grade), Numeric), 2).label('avg_grade')
            )
            .select_from(Group)
            .join(groups_association_table, Group.id == groups_association_table.c.group_id)
            .join(Student, Student.id == groups_association_table.c.student_id)
            .join(Grade, Student.id == Grade.student_id)
            .join(Subject, Grade.subject_id == Subject.id)
            .filter(Subject.name == subject_name)
            .group_by(Group.id, Group.name, Subject.name)
            .order_by(desc("avg_grade"))
            .all()
        )

        return result

def select_4():
    """
    Get the average grade for the whole stream (across all grades tables)
    """
    with get_session() as session:
        result = (
            session.query(
                func.round(cast(func.avg(Grade.grade), Numeric), 2).label('avg_grade')
            )
            .scalar()
        )
        return result

def select_5(teacher_name: str = random_elem(Teacher)):
    """
    Get all the courses taught by a specified teacher
    """
    with get_session() as session:
        result = (
            session.query(
                Teacher.name.label('teacher_name'),
                Subject.name.label('subject_name')
            )
            .join(Subject)
            .filter(Teacher.name == teacher_name)
            .all()
        )
        return result

def select_6(group_name: str = random_elem(Group)):
    """
    Get all the students in a specified group
    """
    with get_session() as session:
        result = (
            session.query(
                Student.name.label("student_name")
            )
            .select_from(Student)
            .join(groups_association_table, Student.id == groups_association_table.c.student_id)
            .join(Group, groups_association_table.c.group_id == Group.id)
            .filter(Group.name == group_name)
            .all()
        )

        return result
    
def select_7(group_name: str = random_elem(Group), subject_name: str = random_elem(Subject)):
    """
    Get student grades for a specified group and subject
    """
    with get_session() as session:
        result = (
            session.query(
                Student.name.label('student_name'),
                Subject.name.label('subject_name'),
                Group.name.label('group_name'),
                Grade.grade.label('grade'),
                Grade.date_of.label('date')
            )
            .select_from(Grade)
            .join(Student)
            .join(groups_association_table, groups_association_table.c.student_id == Student.id)
            .join(Group, groups_association_table.c.group_id == Group.id)
            .join(Subject)
            .filter(
                and_(
                    Group.name == group_name,
                    Subject.name == subject_name
                )
            )
            .order_by(desc(Grade.grade))
            .all()
        )
        return result

def select_8(teacher_name: str = random_elem(Teacher)):
    """
    Average grade given by a teacher based on their subjects
    """
    with get_session() as session:
        result = (
            session.query(
                Teacher.name.label('teacher_name'),
                Subject.name.label('subject'),
                func.round(cast(func.avg(Grade.grade), Numeric), 2).label('avg_grade')
            )
            .select_from(Teacher)
            .join(Subject, Teacher.id == Subject.teacher_id)
            .join(Grade, Grade.subject_id == Subject.id)
            .filter(Teacher.name == teacher_name)
            .group_by(Teacher.id, Teacher.name, Subject.name)
            .all()
        )
        return result

def select_9(student_name: str = random_elem(Student)):
    """
    Subjects taken by specified student
    """
    with get_session() as session:
        result = (
            session.query(
                Student.name.label("student_name"),
                Subject.name.label("subject")
            )
            .select_from(Student)
            .join(Grade, Grade.student_id == Student.id)
            .join(Subject, Grade.subject_id == Subject.id)
            .filter(Student.name == student_name)
            .distinct()
            .all()
        )
        return result
    
def select_10(student_name: str = random_elem(Student), teacher_name: str = random_elem(Teacher)):
    """
    List of subjects that a specified student has with a specified teacher
    """
    with get_session() as session:
        result = (
            session.query(
                Student.name.label("student"),
                Teacher.name.label("teacher"),
                Subject.name.label("subject")
            )
            .select_from(Student)
            .join(Grade, Student.id == Grade.student_id)
            .join(Subject, Subject.id == Grade.subject_id)
            .join(Teacher, Teacher.id == Subject.teacher_id)
            .filter(
                and_(
                    Student.name == student_name,
                    Teacher.name == teacher_name
                )
            )
            .all()
        )
        return result

if __name__ == "__main__":
    print("\n1. Top 5 students by average grade")
    for student in select_1():
        print(f"   {student.name}: {student.avg_grade}")

    print("\n2. Top student by average grade by subject")
    # for student in select_2("Python Advanced"):
    for student in select_2("Python Advanced"):
        print(f"   {student.name}: {student.avg_grade} ({student.subject_name})")

    print("\n3. Average grade by group")
    # for group in select_3("Python Advanced"):
    for group in select_3("Python Advanced"):
        print(f"   {group.group_name}: {group.avg_grade} ({student.subject_name})")

    print("\n4. The average grade for the whole stream")
    print(f"   {select_4()}")

    print("\n5. All the subjects taught by a given teacher")
    for result in select_5():
        print(f"   {result.subject_name} ({result.teacher_name})")

    print("\n6. Students in a group")
    for student in select_6():
            print(f"   {student.student_name}")

    print("\n7. Student grades by group and subject")
    for student in select_7():
        print(f"   {student.group_name} - {student.subject_name} - {student.student_name} - {student.grade} - {student.date}")

    print("\n8. Average grade given by teacher for subjects")
    for elem in select_8():
        print(f"   {elem.teacher_name} - {elem.subject} - {elem.avg_grade}")

    print("\n9. Subjects taken by student")
    for subject in select_9():
        print(f"   {subject.student_name} - {subject.subject}")

    print("\n10.Subjects taken by student with specified teacher")
    for subject in select_10():
        print(f"   {subject.teacher} - {subject.student} - {subject.subject}")

    