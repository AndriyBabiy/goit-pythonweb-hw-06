from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    PrimaryKeyConstraint,
    DateTime,
    Float,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    relationship,
    mapped_column,
    Mapped,
)

class Base(DeclarativeBase):
    pass


groups_association_table = Table(
    "student_groups_association",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id", ondelete="CASCADE")),
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("student_id", "group_id")
)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150))

    groups: Mapped[list["Group"]] = relationship(
        "Group", secondary=groups_association_table, back_populates="students"
    )

    grades: Mapped[list["Grade"]] = relationship(
        "Grade",
        back_populates="student"
    )

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, name='{self.name}')>"


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150))

    students: Mapped[list["Student"]] = relationship(
        "Student", secondary=groups_association_table, back_populates="groups"
    )

    def __repr__(self) -> str:
        return f"<Group(id={self.id}, name='{self.name}')>"


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150))

    subjects: Mapped[list["Subject"]] = relationship(
        "Subject", back_populates="teacher"
    )

    def __repr__(self) -> str:
        return f"<Teacher(id={self.id}, name='{self.name}')>"


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))

    teacher: Mapped["Teacher"] = relationship(
        "Teacher", back_populates="subjects"
    )
    grades: Mapped[list["Grade"]] = relationship("Grade", back_populates="subject")

    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, name='{self.name}')>"


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grade: Mapped[float] = mapped_column(Float)
    date_of: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))

    student: Mapped["Student"] = relationship("Student", back_populates="grades")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="grades")

    def __repr__(self) -> str:
        return f"<Grade(id={self.id}, grade={self.grade}, student='{self.student.name if self.student else None}')>"
