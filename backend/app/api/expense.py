from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseSummary,
    ExpenseCategory,
)
from app.services.expense_service import expense_service
from app.api.deps import get_current_user_id

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense: ExpenseCreate, user_id: str = Depends(get_current_user_id)
):
    """
    Create a new travel expense record.
    """
    try:
        return await expense_service.create_expense(user_id, expense)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating expense: {str(e)}",
        )


@router.get("/", response_model=List[ExpenseResponse])
async def list_expenses(
    itinerary_id: Optional[str] = None,
    category: Optional[ExpenseCategory] = None,
    limit: int = 100,
    user_id: str = Depends(get_current_user_id),
):
    """
    List expenses for the current user with optional filters.
    """
    try:
        return await expense_service.list_expenses(
            user_id, itinerary_id=itinerary_id, category=category, limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing expenses: {str(e)}",
        )


@router.get("/summary", response_model=ExpenseSummary)
async def get_expense_summary(
    itinerary_id: Optional[str] = None, user_id: str = Depends(get_current_user_id)
):
    """
    Get expense summary with totals by category.
    """
    try:
        return await expense_service.get_expense_summary(user_id, itinerary_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting expense summary: {str(e)}",
        )


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Get a specific expense by ID.
    """
    expense = await expense_service.get_expense(expense_id, user_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    expense_update: ExpenseUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """
    Update an existing expense.
    """
    try:
        expense = await expense_service.update_expense(
            expense_id, user_id, expense_update
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found or could not be updated",
        )
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(expense_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Delete an expense.
    """
    success = await expense_service.delete_expense(expense_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found or could not be deleted",
        )
    return None
