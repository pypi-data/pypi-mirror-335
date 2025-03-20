import csv
import os
import uuid
# async def convert_list_to_csv(csv_file_name: str, column_names:list[str], all_failed_downloads: list[str]):

#     unique_id = uuid.uuid4()
#     temp_dir = os.path.join(os.path.expanduser("~"),f"{unique_id}")
#     if not os.path.exists(temp_dir):
#         os.makedirs(temp_dir)

#     # Convert failed_files to CSV and save it to a file
#     csv_path = os.path.join(temp_dir, csv_file_name)
        
#     with open(csv_path, mode='w', newline='') as csv_file:
#         writer = csv.writer(csv_file)
#         writer.writerow(column_names)
#         writer.writerows(all_failed_downloads)

#     attachments=list[str]
#     if(len(all_failed_downloads)>=1): 
#         attachments.append(csv_path)

#     return attachments  

async def convert_list_to_csv(csv_file_name: str, column_names: list[str], all_failed_downloads: list[list[str]]) -> list[str]:
    unique_id = uuid.uuid4()
    temp_dir = os.path.join(os.path.expanduser("~"), f"{unique_id}")
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Convert failed_files to CSV and save it to a file
    csv_path = os.path.join(temp_dir, csv_file_name)
    
    with open(csv_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(column_names)
        writer.writerows(all_failed_downloads)

    # Initialize attachments list and append csv_path if needed
    attachments = []
    if len(all_failed_downloads) >= 1:
        attachments.append(csv_path)

    return attachments


# Helper function to convert ObjectId to string
def object_id_to_str(data):
    if "_id" in data:
        data["_id"] = str(data["_id"])
    return data