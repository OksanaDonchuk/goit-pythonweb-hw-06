from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session

from conf.db import SessionLocal
from entity.models import Student, Grade, Subject, Teacher, Group

def select_01(session: Session) -> list[tuple[str, float]]:
    """Знаходить 5 студентів із найбільшим середнім балом по всіх предметах."""
    query = (
        select(Student.full_name, func.avg(Grade.grade).label("avg_grade"))
        .join(Grade, Grade.student_id == Student.id)
        .group_by(Student.id, Student.first_name, Student.last_name)
        .order_by(desc("avg_grade"))
        .limit(5)
    )
    return session.execute(query).all()


def select_02(session: Session, subject_id: int) -> tuple[str, float] | None:
    """Знаходить студента з найвищим середнім балом з певного предмета."""
    query = (
        select(Student.full_name, func.avg(Grade.grade).label("avg_grade"))
        .join(Grade, Grade.student_id == Student.id)
        .where(Grade.subject_id == subject_id)
        .group_by(Student.id, Student.first_name, Student.last_name)
        .order_by(desc("avg_grade"))
        .limit(1)
    )
    return session.execute(query).first()


def select_03(session: Session, subject_id: int) -> list[tuple[str, float]]:
    """Знаходить середній бал у групах з певного предмета."""
    query = (
        select(Group.name, func.avg(Grade.grade).label("avg_grade"))
        .join(Student, Student.group_id == Group.id)
        .join(Grade, Grade.student_id == Student.id)
        .where(Grade.subject_id == subject_id)
        .group_by(Group.id, Group.name)
    )
    return session.execute(query).all()


def select_04(session: Session) -> float | None:
    """Знаходить середній бал на потоці (по всій таблиці оцінок)."""
    return session.execute(select(func.avg(Grade.grade))).scalar()


def select_05(session: Session, teacher_id: int) -> list[Subject]:
    """Повертає список курсів, які читає певний викладач."""
    query = (
        select(Subject)
        .where(Subject.teacher_id == teacher_id)
        .order_by(Subject.name)
    )
    return session.execute(query).scalars().all()


def select_06(session: Session, group_id: int) -> list[Student]:
    """Повертає список студентів у певній групі."""
    query = (
        select(Student)
        .where(Student.group_id == group_id)
        .order_by(Student.last_name, Student.first_name)
    )
    return session.execute(query).scalars().all()


def select_07(session: Session, group_id: int, subject_id: int) -> list[tuple[str, float]]:
    """Знаходить оцінки студентів у певній групі з певного предмета."""
    query = (
        select(Student.full_name, Grade.grade)
        .join(Grade, Grade.student_id == Student.id)
        .where(Grade.subject_id == subject_id, Student.group_id == group_id)
        .order_by(Student.last_name, Student.first_name)
    )
    return session.execute(query).all()


def select_08(session: Session, teacher_id: int) -> float | None:
    """Знаходить середній бал, який ставить певний викладач зі своїх предметів."""
    query = (
        select(func.avg(Grade.grade))
        .select_from(Subject)
        .join(Grade, Grade.subject_id == Subject.id)
        .where(Subject.teacher_id == teacher_id)
    )
    return session.execute(query).scalar()


def select_09(session: Session, student_id: int) -> list[Subject]:
    """Повертає список курсів, які відвідує певний студент."""
    query = (
        select(Subject)
        .join(Grade, Grade.subject_id == Subject.id)
        .where(Grade.student_id == student_id)
        .distinct()
        .order_by(Subject.name)
    )
    return session.execute(query).scalars().all()


def select_10(session: Session, student_id: int, teacher_id: int) -> list[Subject]:
    """Повертає список курсів, які певний викладач читає конкретному студенту."""
    query = (
        select(Subject)
        .join(Grade, Grade.subject_id == Subject.id)
        .where(Grade.student_id == student_id, Subject.teacher_id == teacher_id)
        .distinct()
        .order_by(Subject.name)
    )
    return session.execute(query).scalars().all()


def select_11(session: Session, student_id: int, teacher_id: int) -> float | None:
    """Знаходить середній бал, який певний викладач ставить певному студентові."""
    query = (
        select(func.avg(Grade.grade))
        .join(Subject, Subject.id == Grade.subject_id)
        .where(Grade.student_id == student_id, Subject.teacher_id == teacher_id)
    )
    return session.execute(query).scalar()


def select_12(session: Session, group_id: int, subject_id: int) -> list[tuple[str, float, str]]:
    """Знаходить оцінки студентів у певній групі з певного предмета на останньому занятті."""
    subquery = (
        select(func.max(Grade.date_received))
        .join(Student, Student.id == Grade.student_id)
        .where(Grade.subject_id == subject_id, Student.group_id == group_id)
        .scalar_subquery()
    )

    query = (
        select(Student.full_name, Grade.grade, Grade.date_received)
        .join(Grade, Grade.student_id == Student.id)
        .where(
            Grade.subject_id == subject_id,
            Student.group_id == group_id,
            Grade.date_received == subquery
        )
        .order_by(Student.last_name, Student.first_name)
    )
    return session.execute(query).all()


if __name__ == "__main__":
    with SessionLocal() as session:
        result_01 = select_01(session)
        result_02 = select_02(session, 2)
        result_03 = select_03(session, 4)
        result_04 = select_04(session)
        result_05 = select_05(session, 3)
        result_06 = select_06(session, 8)
        result_07 = select_07(session, 7, 2)
        result_08 = select_08(session, 3)
        result_09 = select_09(session, 61)
        result_10 = select_10(session, 70, 3)
        result_11 = select_11(session, 85, 2)
        result_12 = select_12(session, 8, 2)

        print("1. 5 студентів із найбільшим середнім балом по всіх предметах:")
        for full_name, avg_grade in result_01:
            print(f"   {full_name}: {avg_grade:.2f}")
        print("-" * 60)

        print("2. Студент із найвищим середнім балом з певного предмета:")
        if result_02:
            full_name, avg_grade = result_02
            print(f"   {full_name}: {avg_grade:.2f}")
        print("-" * 60)

        print("3. Середній бал у групах з певного предмета:")
        for group_name, avg_grade in result_03:
            print(f"   {group_name}: {avg_grade:.2f}")
        print("-" * 60)

        print(f"4. Середній бал на потоці: {result_04:.2f}")
        print("-" * 60)

        print("5. Список курсів, які читає певний викладач:")
        for subject in result_05:
            print(f"   {subject.name}")
        print("-" * 60)

        print("6. Список студентів у певній групі:")
        for student in result_06:
            print(f"   {student.full_name}")
        print("-" * 60)

        print("7. Оцінки студентів у певній групі з певного предмета:")
        for name, grade in result_07:
            print(f"   {name}: {grade}")
        print("-" * 60)

        if result_08 is not None:
            print(f"8. Середній бал, який ставить певний викладач зі своїх предметів: {result_08:.2f}")
        else:
            print("8. У цього викладача ще немає оцінок.")
        print("-" * 60)

        print("9. Список курсів, які відвідує певний студент:")
        for subject in result_09:
            print(f"   {subject.name}")
        print("-" * 60)

        print("10. Список курсів, які певний викладач читає конкретному студенту:")
        for subject in result_10:
            print(f"   {subject.name}")
        print("-" * 60)

        if result_11 is not None:
            print(f"11. Середній бал, який певний викладач ставить певному студентові: {result_11:.2f}")
        else:
            print("11. Цей викладач ще не виставляв оцінок цьому студенту.")
        print("-" * 60)

        print("12. Оцінки студентів у певній групі з певного предмета на останньому занятті:")
        for name, grade, date in result_12:
            print(f"   {name}: {grade} ({date.date()})")
        print("=" * 60)