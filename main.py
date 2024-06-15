from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime, timedelta
import random
from collections import defaultdict


# Define the shift types
class ShiftType(str, Enum):
    day = "day"
    evening = "evening"
    night = "night"


# Define the Employee model
class Employee(BaseModel):
    id: int
    name: str
    preferences: List[ShiftType]


# Define the RosterRequest model
class RosterRequest(BaseModel):
    employees: List[Employee]
    start_date: Optional[str] = Field(None, description="Start date for the roster (YYYY-MM-DD)")


# Define the Shift model
class Shift(BaseModel):
    employee_id: int
    shift_type: ShiftType
    date: str


# Generate shift roster function
def generate_shift_roster(employees: List[Employee], start_date: str) -> List[Shift]:
    num_employees = len(employees)
    shifts = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")

    # Dictionary to track shifts assigned to each employee
    employee_shifts = defaultdict(lambda: {"days": 0, "evenings": 0, "nights": 0})
    # Track days off for each employee
    days_off = {employee.id: set() for employee in employees}

    # Generate roster for 1 week
    for day in range(7):
        daily_shifts = {ShiftType.day: [], ShiftType.evening: [], ShiftType.night: []}
        available_employees = [e for e in employees if day not in days_off[e.id]]

        # Assign shifts considering preferences and constraints
        for shift_type in [ShiftType.day, ShiftType.evening, ShiftType.night]:
            shift_needed = num_employees // 3  # Assuming equal distribution for simplicity

            while len(daily_shifts[shift_type]) < shift_needed:
                employee = random.choice(available_employees)

                # Check constraints for night shifts
                if shift_type == ShiftType.night and employee_shifts[employee.id]["nights"] >= 3:
                    continue

                # Check if employee already has a shift of this type
                if employee in daily_shifts[shift_type]:
                    continue

                # Assign shift
                daily_shifts[shift_type].append(employee)
                shifts.append(
                    Shift(employee_id=employee.id, shift_type=shift_type, date=current_date.strftime("%Y-%m-%d"))
                )
                available_employees.remove(employee)

                # Track assigned shifts
                employee_shifts[employee.id][shift_type.value + "s"] += 1
                if shift_type != ShiftType.night:
                    employee_shifts[employee.id]["days"] += 1

        current_date += timedelta(days=1)

    # Ensure 2 consecutive days off for each employee
    for employee_id in employee_shifts.keys():
        assigned_days = [shift.date for shift in shifts if shift.employee_id == employee_id]
        for i in range(len(assigned_days) - 1):
            if (datetime.strptime(assigned_days[i + 1], "%Y-%m-%d") - datetime.strptime(assigned_days[i],
                                                                                        "%Y-%m-%d")).days > 1:
                days_off[employee_id].update([assigned_days[i], assigned_days[i + 1]])
                break

    return shifts


# Create FastAPI app
app = FastAPI()

# Create API router
router = APIRouter()


@router.post("/generate_roster", response_model=List[Shift])
def generate_roster(roster_request: RosterRequest):
    try:
        # Use the current date if start_date is not provided
        start_date = roster_request.start_date or datetime.now().strftime("%Y-%m-%d")
        shifts = generate_shift_roster(roster_request.employees, start_date)
        return shifts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Include the router in the FastAPI app
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
