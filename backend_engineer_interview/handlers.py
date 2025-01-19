from contextlib import contextmanager
from datetime import date
from typing import Generator, Optional
import connexion.lifecycle  # type: ignore
from flask import g
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
