from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from src.database.database import get_db
from src.database.models import SurveyResponse, Employee

router = APIRouter()

@router.delete("/delete-pending-and-null-employees")
async def delete_pending_and_null_employees(db: AsyncSession = Depends(get_db)):
    
    # 1️⃣ Delete PENDING survey responses
    delete_pending_stmt = delete(SurveyResponse).where(
        SurveyResponse.status == "PENDING"
    )
    pending_result = await db.execute(delete_pending_stmt)

    # 2️⃣ Delete employees where overall_sentiment IS NULL
    delete_null_emp_stmt = delete(Employee).where(
        Employee.overall_sentiment.is_(None)     # <-- important
    )
    null_emp_result = await db.execute(delete_null_emp_stmt)

    # Commit all changes
    await db.commit()

    return {
        "message": "Pending survey responses and NULL sentiment employees deleted successfully",
        "deleted_pending_responses": pending_result.rowcount,
        "deleted_null_sentiment_employees": null_emp_result.rowcount
    }