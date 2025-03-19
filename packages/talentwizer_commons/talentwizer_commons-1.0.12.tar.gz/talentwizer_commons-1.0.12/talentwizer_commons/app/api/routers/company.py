from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from app.models import _Company, Company
from talentwizer_commons.utils.db import mongo_database
from datetime import datetime
import traceback
# Create an instance of APIRouter to handle company-related routes
company_router = c = APIRouter()

# Endpoint to create a new company
@c.post("/{user_id}")
async def create_company(
    user_id: str,
    data: _Company,
):
    """
    Create a new company.

    :param data: Data of the company to be created and the user id.
    :type data: str, _Company
    :raises HTTPException 400: If no company name is provided.
    :return: ID of the created company.
    :rtype: dict
    """
    # check preconditions and get last message
    if data.company_name == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No company provided",
        )
    
    # check if user exists
    user_data = mongo_database["Users"].find_one({"_id": ObjectId(user_id)})
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    # Define your query
    # query = {"no_of_companies": {"$exists": True}}

    # Check if the field exists in any document in the collection
    if user_data and "user_companies_count" in user_data:
        current_companies_count = user_data["user_companies_count"]
    else:
        current_companies_count = 0

    current_companies_count += 1

    result = mongo_database["Company"].insert_one({
        **data.dict(),
        "is_deleted": False,
        "created_at": datetime.now(),  
        "updated_at": datetime.now() 
    })

    company_id = str(result.inserted_id)

    mongo_database["Users"].update_one(
        {"_id": ObjectId(user_id)}, 
        {
            # "$push": {"company": {"company": company_id}},
            "$push": {"companies": str(company_id)},
            "$set": {"user_companies_count": current_companies_count,"updated_at": datetime.now()}
        }
    )
    
    return {"id": company_id}

# Endpoint to retrieve all companies associated with a user
@c.get("/{user_id}/all")
async def get_all_companies(
    user_id: str,
):
    """
    Retrieve all companies associated with a user.

    :param user_id: ID of the user.
    :type user_id: str
    :return: List of companies associated with the user.
    :rtype: dict
    """
    user_details = mongo_database["Users"].find_one({"_id": ObjectId(user_id)})
    if not user_details or "companies" not in user_details:
        # Handle the case where the user or their associated companies are not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No companies associated with this user"
        )

    # company_ids = user_details["company"]
    company_ids = user_details["companies"]
    # return {}

    companies = []
    for company_id in company_ids:
        company_dict = mongo_database["Company"].find_one({"_id": ObjectId(company_id)})
        if company_dict and (company_dict["is_deleted"] is None or company_dict["is_deleted"]==False) :
            company = Company(company_dict["_id"], company_dict["company_name"], company_dict["is_deleted"])
            companies.append(company)
 
    # Convert ObjectId to string for JSON serialization
    for company in companies:
        company._id = str(company._id)
      
    return companies
    
# Endpoint to retrieve jobs of a specific company
@c.get("/{id}/jobs")
async def get_jobs(
    id: str,
):
    """
    Retrieve jobs of a specific company.

    :param id: ID of the company.
    :type id: str
    :return: List of jobs of the company.
    :rtype: dict
    """
    try:
        company_id = (id)
        company = mongo_database["Company"].find_one({"_id": ObjectId(company_id)})

        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")

        jobs = company.get("jobs", [])

        job_ids = []
        for job_id in jobs:
            job = mongo_database["Job"].find_one({"_id": ObjectId(job_id)})
            if job and not job.get("is_deleted", False):
                job_ids.append({"_id": str(job_id)})

        return job_ids

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving jobs: {str(e)}")

@c.delete("/{id}")
def delete_company(id: str):
    """
    Delete a specific company and update the associated user's company and job counts.

    :param id: ID of the company.
    :type id: str
    :return: {"message": "Company Deleted successfully"}
    :rtype: dict
    :raises HTTPException 404: If the company or user is not found.
    """
    company_id = id
    company = mongo_database["Company"].find_one({"_id": ObjectId(company_id)})
    jobs = company.get("jobs", [])

    try:
        # Retrieve the user document containing the company_id
        user_doc = mongo_database["Users"].find_one({"companies": company_id})

        # Check if the user document exists
        if user_doc:
            # Decrement the user_companies_count
            new_companies_count = user_doc["user_companies_count"] - 1

            # Calculate the number of jobs to be removed from user_jobs_count
            jobs_to_remove_count = len(jobs)

            # Update the user's document with the new counts
            mongo_database["Users"].update_one(
                {"_id": user_doc["_id"]},
                {
                    "$set": {
                        "user_companies_count": new_companies_count,
                        "user_jobs_count": user_doc["user_jobs_count"] - jobs_to_remove_count,
                        "updated_at": datetime.now()
                    }
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Delete the company and its associated jobs
        for job in jobs:
            job_id = str(job)
            mongo_database["Job"].update_one(
                {"_id": ObjectId(job_id)},
                {"$set": {"is_deleted": True, "updated_at": datetime.now()}}
            )

        mongo_database["Company"].update_one(
            {"_id": ObjectId(company_id)},
            {"$set": {"is_deleted": True, "updated_at": datetime.now()}}
        )

        return {"message": "Company Deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )