from mcp.server.fastmcp import FastMCP
from helper import create_ec2_instance, terminate_ec2_instance


# Initialize FastMCP server
mcp = FastMCP("aws")


@mcp.tool()
async def initiate_aws_ec2_instance():
    """
    Initiates the AWS EC2 instance creation process.
    This function doesn't take any arguments and is called when the script is run.
    """
    print("Initiating AWS EC2 instance creation...")
    instance_id = create_ec2_instance()
    if instance_id:
        return f"EC2 instance created with ID: {instance_id}"
    else:
        return "Failed to create EC2 instance. Please check the logs for more details."


@mcp.tool()
async def terminate_aws_ec2_instance(instance_id: str):
    """
    Terminates the AWS EC2 instance.
    This function doesn't take any arguments and is called when the script is run.
    """
    print("Terminating AWS EC2 instance...")
    # Replace 'your_instance_id' with the actual instance ID you want to terminate

    if instance_id:
        terminate_ec2_instance(instance_id)
        return f"EC2 instance with ID: {instance_id} has been terminated."
    else:
        return (
            "No instance ID provided. Please provide a valid instance ID to terminate."
        )


if __name__ == "__main__":
    # Initialize and run the server

    print("Starting FastMCP server...")
    mcp.run(transport="stdio")
    print("FastMCP server is running.")
