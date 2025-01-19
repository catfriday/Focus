from datetime import date
from models import Application
from handlers import db_session


def seed_data():
    with db_session() as session:  # type: Session
        session.add(
            Application(
                leave_start_date=date(2021, 1, 1), leave_end_date=date(2021, 2, 1), employee_id=1
            )
        )
        session.add(
            Application(
                leave_start_date=date(2021, 2, 1), leave_end_date=date(2021, 3, 1), employee_id=2
            )
        )
        session.add(
            Application(
                leave_start_date=date(2021, 3, 1), leave_end_date=date(2021, 4, 1), employee_id=10
            )
        )
        session.commit()


if __name__ == "__main__":
    seed_data()
    print("Database seeded successfully!")
    applications = Application.query.all()
    for application in applications:
        print(f"Application {application.id} for employee {application.employee_id}")
