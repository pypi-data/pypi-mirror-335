import boto3
import os
from typing import Optional

class SNSClient:
    def __init__(self):
        self.sns_client = boto3.client('sns',region_name=os.environ.get("AWS_REGION", "us-east-1"))
        self.topic_arn = os.getenv('SNS_TOPIC_ARN')

    def create_appointment_topic(self):
        """Create the appointments notification topic"""
        response = self.sns_client.create_topic(Name='AppointmentNotifications')
        self.topic_arn = response['TopicArn']
        return self.topic_arn

    def subscribe_patient(self, email: str):
        """Subscribe a patient to notifications"""
        return self.sns_client.subscribe(
            TopicArn=self.topic_arn,
            Protocol='email',
            Endpoint=email
        )

    def send_appointment_notification(self, email: str, message: str):
        """Send appointment status notification"""
        self.sns_client.publish(
            TopicArn=self.topic_arn,
            Message=message,
            Subject='Appointment Status Update',
            MessageAttributes={
                'email': {
                    'DataType': 'String',
                    'StringValue': email
                }
            }
        )

    def send_prescription_notification(self, patient_email:str, message:str):
        self.sns_client.publish(
            TopicArn=self.topic_arn,
            Message=message,
            Subject='Prescription Upload',
            MessageAttributes={
                'email': {
                    'DataType': 'String',
                    'StringValue': patient_email
                }
            }
        )