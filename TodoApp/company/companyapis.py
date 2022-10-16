from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_company_name():
    return {
        "company_name":"Example company"
    }

@router.get("/employess")
async def number_of_employees():
    return 180
