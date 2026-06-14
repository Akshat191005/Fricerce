"""
AWS Lambda handler — wraps the FastAPI app with Mangum for API Gateway.
Deploy this as the Lambda entry point: lambda_handler.handler
"""
from mangum import Mangum
from app.main import app

# Mangum adapter maps API Gateway / ALB events to ASGI
handler = Mangum(app, lifespan="off")
