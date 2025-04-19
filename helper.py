import boto3
import sys
from dotenv import load_dotenv
import os

def create_ec2_instance():
    """
    This function creates an EC2 instance in AWS.

    Ensure you have your AWS credentials configured properly (either via
    environment variables, a configuration file, or an IAM role).  You will
    also need to specify the correct AMI ID, instance type, and security group.
    """

    # Load properties from .env file

    load_dotenv()  # Load environment variables from .env file

    # Retrieve properties from the environment
    ami_id = os.getenv('AMI_ID', '<your value>')  # Default value if not set
    instance_type = os.getenv('INSTANCE_TYPE', '<your value>')
    key_name = os.getenv('KEY_NAME', '<your value>')
    security_group_ids = os.getenv('SECURITY_GROUP_IDS', '<your value>').split(',')
    region_name = os.getenv('AWS_REGION', '<your value>')

    # Update the EC2 client with the region from the .env file
    ec2 = boto3.client('ec2', region_name=region_name)
    # Initialize the EC2 client using boto3
     # Change to your desired region

    # Define the parameters for the EC2 instance
    #  * ImageId:  The Amazon Machine Image (AMI) ID.  Choose an AMI that
    #     matches your desired operating system and region.  You can find
    #     these in the AWS Management Console.
    #  * InstanceType:  The type of instance to launch (e.g., 't2.micro',
    #     't3.medium').
    #  * MinCount and MaxCount:  The minimum and maximum number of
    #     instances to launch.  Here, we launch exactly one instance.
    #  * KeyName:  The name of the key pair to use for SSH access to the
    #     instance.  Ensure this key pair exists in your AWS account.
    #  * SecurityGroupIds: A list of security group IDs to associate with
    #     the instance.  These control the inbound and outbound traffic for
    #     the instance.
    #  * TagSpecifications:  Optional tags to apply to the instance.  Tags
    #     are key-value pairs that can help you organize and manage your
    #     AWS resources.
    try:
        response = ec2.run_instances(
            ImageId=ami_id,  # Example: Ubuntu 20.04 (replace with your desired AMI)
            InstanceType=instance_type,          # Example
            MinCount=1,
            MaxCount=1,
            KeyName=key_name,    # Replace with your key pair name
            SecurityGroupIds=list(security_group_ids),  # Replace with your security group ID
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'MyPyEc2Instance-mcp'
                        },
                        {
                            'Key': 'Environment',
                            'Value': 'Staging'
                        }
                    ]
                }
            ]
        )

        # Extract the instance ID from the response
        instance_id = response['Instances'][0]['InstanceId']
        print(f"EC2 instance created with ID: {instance_id}")
        return instance_id  # Return the Instance ID

    except Exception as e:
        print(f"Error creating EC2 instance: {e}")
        return None # Return None in case of Error

def terminate_ec2_instance(instance_id):
    """
    Terminates the EC2 instance with the given ID.

    Args:
        instance_id (str): The ID of the EC2 instance to terminate.
    """

    load_dotenv()
    region_name = os.getenv('AWS_REGION', '<your value>')
    # Initialize the EC2 client
    ec2 = boto3.client('ec2', region_name=region_name)

    try:
        # Terminate the instance
        response = ec2.terminate_instances(
            InstanceIds=[instance_id]
        )

        # Print the termination status
        print(f"Terminating instance: {instance_id}")
        for instance in response['TerminatingInstances']:
            print(f"  Instance ID: {instance['InstanceId']}")
            print(f"  Previous State: {instance['PreviousState']['Name']}")
            print(f"  Current State: {instance['CurrentState']['Name']}")

    except Exception as e:
        print(f"Error terminating instance {instance_id}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Example usage
    instance_id = create_ec2_instance()
    if instance_id:
        terminate_ec2_instance(instance_id)
    else:
        print("No instance ID returned. Cannot terminate.")

