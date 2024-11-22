import logging
from typing import Annotated, List

from auth.services import admin_access, get_current_user
from core.associations import UserSubjectAssociation
from core.enums import Role
from core.models import User
from database.core import get_async_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from subject.schemas import SubjectCreate
from subject.services import get_subject_by_name

from .schemas import StudentUpdate
from .services import (
    get_student_account_by_id,
    remove_student_by_id,
    update_student_account,
)

student_router = APIRouter(prefix="/student", tags=["Students"])
student_subject_router = APIRouter(prefix="/student-subject", tags=["StudentSubjects"])

ogger = logging.getLogger(__name__)


@student_router.get(
    "/",
    summary="List user accounts",
    dependencies=[Depends(admin_access)],
    operation_id="get_students",
)
async def get_useraccounts(db: Annotated[AsyncSession, Depends(get_async_db)]):
    query = select(User).where(User.role == Role.STUDENT)
    users = await db.execute(query)
    users = users.scalars().all()
    return users


@student_router.get(
    "/{student_id}",
    summary="Detail a account using its ID",
    dependencies=[Depends(admin_access)],
    operation_id="get_student_by_id",
)
async def get_student_by_id(
    student_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    student = await get_student_account_by_id(student_id, db)
    return student


@student_router.patch(
    "/update/{student_id}",
    # response_model=UserResponse,
    summary="Update a useraccount using its ID",
    operation_id="patch_update_student",
)
async def update_useraccount(
    current_user: Annotated[User, Depends(get_current_user)],
    updated_student: StudentUpdate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    new_updated_student = await update_student_account(
        student_id=current_user.id, student_in=updated_student, db=db
    )
    if not new_updated_student:
        # If no user is found, raise a 404 error
        raise HTTPException(
            status_code=404, detail="Student not found or update failed."
        )

    return new_updated_student


@student_router.delete(
    "/delete/{student_id}",
    summary="delete a user account using its ID",
    dependencies=[Depends(admin_access)],
    operation_id="delete_student_by_id",
)
async def delete_useraccount(
    id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    student = await remove_student_by_id(id, db)
    return student


####################################### Student Subject Related routes #########################################


@student_subject_router.get(
    "/get-student-subjects",
    summary="Get subjects for student (with grade)",
    operation_id="get_student_subjects",
)
async def get_subjects_for_student(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[
        User, Depends(get_current_user)
    ],  # Ensure this checks the user, not admin
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Ensure the user is a student, if needed
    if current_user.role != Role.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this information",
        )

    # Fetch all subjects associated with this user
    query = select(UserSubjectAssociation).where(
        UserSubjectAssociation.user_id == current_user.id,
        UserSubjectAssociation.is_deleted.is_(
            False
        ),  # Assuming this is for soft-deleted associations
    )
    result = await db.execute(query)
    associations = result.scalars().all()

    # You may want to return detailed info, including the subject name and grade
    subjects_with_grades = [
        {
            "name": association.subject.name,
            "grade": association.grade,  # Assuming grade is stored in 'grade'
        }
        for association in associations
    ]

    return subjects_with_grades


@student_subject_router.post(
    "/add-student-subject",
    summary="Add subjects to a student (with grade)",
    operation_id="post_add_student_subject",
)
async def add_subject_to_student(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    subject_in: SubjectCreate,  # Assuming this schema contains name and grade/grade
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Fetch the subject by name
    subject = await get_subject_by_name(db=db, subject_name=subject_in.name)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found"
        )

    # Check if the user already has this subject
    existing_association_query = select(UserSubjectAssociation).where(
        UserSubjectAssociation.user_id == current_user.id,
        UserSubjectAssociation.subject_id == subject.id,
        UserSubjectAssociation.is_deleted.is_(False),  # Exclude deleted associations
    )
    result = await db.execute(existing_association_query)
    existing_association = result.scalar_one_or_none()

    if existing_association:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subject already associated with the user.",
        )

    # Create a new subject association
    association = UserSubjectAssociation(
        user_id=current_user.id,
        subject_id=subject.id,
        grade=subject_in.grade,  # grade represents the grade
    )

    # Add the association to the database
    db.add(association)
    await db.commit()
    await db.refresh(association)

    return {"message": "Subject added successfully", "association": association}


@student_subject_router.post(
    "/add-bulk-student-subjects",
    summary="Add multiple subjects to a student (with grades)",
    operation_id="post_bulk_add_student_subject",
)
async def add_bulk_subjects_to_student(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    subjects: List[SubjectCreate],  # Expecting a list of subjects with grades
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # List to hold successful associations
    successful_associations = []

    for subject_in in subjects:
        # Fetch the subject by name
        subject = await get_subject_by_name(db=db, subject_name=subject_in.name)
        if not subject:
            # If the subject doesn't exist, skip it and continue to the next
            continue

        # Check if the user already has this subject
        existing_association_query = select(UserSubjectAssociation).where(
            UserSubjectAssociation.user_id == current_user.id,
            UserSubjectAssociation.subject_id == subject.id,
            UserSubjectAssociation.is_deleted.is_(
                False
            ),  # Exclude deleted associations
        )
        result = await db.execute(existing_association_query)
        existing_association = result.scalar_one_or_none()

        if existing_association:
            # If the association already exists, you might want to skip it or raise an error
            continue

        # Create a new subject association
        association = UserSubjectAssociation(
            user_id=current_user.id,
            subject_id=subject.id,
            grade=subject_in.grade,  # Assuming 'grade' represents the grade
        )

        # Add the association to the database
        db.add(association)
        successful_associations.append(association)

    # Commit all associations
    await db.commit()

    return {
        "message": "Subjects added successfully",
        "associations": [
            {"subject_name": assoc.subject.name, "grade": assoc.grade}
            for assoc in successful_associations
        ],
    }


@student_subject_router.delete(
    "/remove-student-subject",
    summary="Remove a subject from a student (hard-delete)",
    operation_id="delete_student_subject",
)
async def remove_subject_from_student(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    subject_name: str,
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Fetch the subject by name
    subject = await get_subject_by_name(db=db, subject_name=subject_name)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found"
        )

    # Check if the association exists
    query = select(UserSubjectAssociation).where(
        UserSubjectAssociation.user_id == current_user.id,
        UserSubjectAssociation.subject_id == subject.id,
        UserSubjectAssociation.is_deleted.is_(
            False
        ),  # Only look for active associations
    )
    result = await db.execute(query)
    association = result.scalar_one_or_none()

    if not association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject association not found for this student.",
        )

    # Hard delete the association
    await db.delete(association)
    await db.commit()

    return {"message": f"Subject {subject_name} successfully removed from student."}


####################################### Student Subject Related routes #########################################
