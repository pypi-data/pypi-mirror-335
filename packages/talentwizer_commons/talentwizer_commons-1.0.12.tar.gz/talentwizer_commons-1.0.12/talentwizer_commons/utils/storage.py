from dotenv import load_dotenv

load_dotenv()
import boto3
import os

# Initialize AWS S3 client
s3_client = boto3.client('s3', 
                  aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"], 
                  aws_secret_access_key=os.environ["AWS_SECRET"], 
                  region_name=os.environ["AWS_REGION"])

lambda_client = boto3.client('lambda',
                            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"], 
                            aws_secret_access_key=os.environ["AWS_SECRET"], 
                            region_name=os.environ["AWS_REGION"])
