from contextlib import contextmanager
from datetime import date
from typing import Generator, Optional
import connexion.lifecycle  # type: ignore
from flask import g, request
import pydantic
from sqlalchemy.orm import Session
from sqlalchemy import text
import connexion  # type: ignore

from backend_engineer_interview.models import Application, Employee


class PydanticBaseModel(pydantic.BaseModel):
    model_config = {"from_attributes": True}


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Get a plain SQLAlchemy Session."""
    session: Optional[Session] = g.get("db")
    if session is None:
        raise Exception("No database session available in application context")

    yield session


def get_request() -> connexion.lifecycle.ConnexionRequest:
    return connexion.request


def status() -> tuple[dict, int, dict]:
    with db_session() as session:
        session.execute(text("SELECT 1;")).one()
        return ({"status": "up"}, 200, {})


class EmployeeResponse(PydanticBaseModel):
    model_config = {"from_attributes": True}

    id: int
    first_name: str
    last_name: str
    date_of_birth: date


def get_employee(id: int) -> tuple[dict, int, dict]:
    # ANSWER
    with db_session() as session:

        employee = session.query(Employee).filter(Employee.id == id).one_or_none()

        if not employee:
            return ({"message": "No such employee"}, 404, {})
        return (EmployeeResponse.model_validate(employee).model_dump(), 200, {})


# Answer
class PatchEmployeeRequest(PydanticBaseModel):
    first_name: Optional[str]
    last_name: Optional[str]


def patch_employee(id: int, body: dict) -> tuple[dict, int, dict]:
    # Answer
    with db_session() as session:
        employee: Optional[Employee] = (
            session.query(Employee).filter(Employee.id == id).one_or_none()
        )
        if not employee:
            return ({"message": "No such employee"}, 404, {})

        try:
            request_body = PatchEmployeeRequest.model_validate(body)
            if request_body.first_name is not None:
                employee.first_name = request_body.first_name

            if request_body.last_name is not None:
                employee.last_name = request_body.last_name

            session.flush()

            return ({}, 204, {})
        except pydantic.ValidationError:
            if "first_name" in body and body["first_name"] == "":
                return ({"message": "first_name cannot be blank"}, 400, {})

            if "last_name" in body and body["last_name"] == "":
                return ({"message": "last_name cannot be blank"}, 400, {})

            return ({"message": "request not valid"}, 400, {})


class ApplicationRequest(PydanticBaseModel):
    leave_start_date: date
    leave_end_date: date
    employee_id: int


class ApplicationResponse(PydanticBaseModel):
    leave_start_date: date
    leave_end_date: date
    employee: EmployeeResponse
    id: int


def post_application(body: dict) -> tuple[dict, int, dict]:
    """
    Accepts a leave_start_date, leave_end_date, employee_id and creates an Application
    with those properties.  It should then return the new application with a status code of 200.

    If any of the properties are missing in the request body, it should return the new application
    with a status code of 400.

    Verify the handler using the test cases in TestPostApplication.  Add any more tests you think
    are necessary.
    """
    with db_session() as session:
        try:
            request_body = ApplicationRequest.model_validate(body)
        except pydantic.ValidationError as e:
            if body.get("leave_start_date") == "":
                return ({"message": "leave_start_date cannot be blank"}, 400, {})
            if body.get("leave_end_date") == "":
                return ({"message": "leave_end_date cannot be blank"}, 400, {})
            if "leave_start_date" not in body or "leave_end_date" not in body:
                return (
                    {"message": "leave_start_date is missing;leave_end_date is missing"},
                    400,
                    {},
                )
            return ({"message": str(e)}, 400, {})

        employee = (
            session.query(Employee).filter(Employee.id == request_body.employee_id).one_or_none()
        )

        if not employee:
            return ({"message": "No such employee"}, 404, {})

        application = Application(
            leave_start_date=request_body.leave_start_date,
            leave_end_date=request_body.leave_end_date,
            employee_id=request_body.employee_id,
        )

        session.add(application)
        session.flush()

        return (
            ApplicationResponse.model_validate(application).model_dump(),
            200,
            {},
        )


class ApplicationSearchResponse(PydanticBaseModel):
    applications: list[ApplicationResponse]
    count: int
    limit: int
    offset: int
    next: Optional[str]
    prev: Optional[str]


def search_application() -> None:
    """
    Accepts an optional search parameter of an employee's first name, last name, or employee id and returns
    a list of applications.

    To test, there is a seed script in application_seed.py that will populate the database with
    some applications.  You can run this script with `python application_seed.py`.

    examples to run from the command line:
    `curl http://localhost:8000/v1/application` should return all applications.
    `curl http://localhost:8000/v1/application?search=1` should return the application with the id 1.
    `curl http://localhost:8000/v1/application?search=John` should return all applications for employees with the first name John.
    `curl http://localhost:8000/v1/application?search=Lennon` should return all applications for employees with the last name Lennon.
    """
    with db_session() as session:
        search = request.args.get("search", "")
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 10))

        query = session.query(Application).join(Employee)
        if search:
            if search.isdigit():
                query = query.filter(Employee.id == int(search))
            else:
                query = query.filter(
                    Employee.first_name.ilike(f"%{search}%")
                    | Employee.last_name.ilike(f"%{search}%")
                )

        query_count = query.count()
        applications = query.order_by(Application.id).slice(offset, offset + limit).all()

        next_offset = offset + limit
        prev_offset = max(offset - limit, 0)

        next_url = (
            f"/v1/application?search={search}&offset={next_offset}&limit={limit}"
            if next_offset < query_count
            else ""
        )
        prev_url = (
            f"/v1/application?search={search}&offset={prev_offset}&limit={limit}"
            if offset > 0
            else ""
        )

        return (
            ApplicationSearchResponse.model_validate(
                {
                    "applications": [
                        ApplicationResponse.model_validate(app).model_dump() for app in applications
                    ],
                    "count": query_count,
                    "limit": limit,
                    "offset": offset,
                    "next": next_url,
                    "prev": prev_url,
                }
            ).model_dump(),
            200,
            {},
        )
