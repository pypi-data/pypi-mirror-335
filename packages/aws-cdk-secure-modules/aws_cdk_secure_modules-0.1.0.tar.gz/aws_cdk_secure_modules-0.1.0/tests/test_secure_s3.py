import aws_cdk as cdk
from aws_cdk.assertions import Template
from constructs.secure_s3.secure_s3_construct import SecureS3Bucket
from aws_cdk import App, Stack

def test_secure_s3_construct():
    app = App()
    stack = Stack(app, "TestStack")

    # Default behavior (no logging, enforce HTTPS enabled)
    SecureS3Bucket(stack, "TestSecureS3", bucket_name="test-secure-bucket", enforce_https=True)
    template = Template.from_stack(stack)

    # Debugging Output: Print all resources
    print("Synthesized CloudFormation Template:")
    print(template.to_json())

    # Debug: Print all detected resource types
    resource_types = template.find_resources("AWS::S3::Bucket")
    print(f"Detected S3 Buckets: {resource_types}")

    assert len(resource_types) == 1  # Ensure one bucket exists
