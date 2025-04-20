# 🚀 MCP-AWS: AI Agent for AWS EC2 Management

Welcome to **MCP-AWS**, a simple yet powerful AI-driven application that leverages OpenAI Agents and MCP servers to manage AWS EC2 instances. This app allows you to provision and terminate EC2 instances using natural language commands in your terminal. 🖥️✨


---

## 🎥 Demo Video

Watch the demo video to see MCP-AWS in action! 🚀

[![Watch the Demo]([https://img.youtube.com/vi/nT6w48w03NI/0.jpg)](https://youtu.be/nT6w48w03NI](https://youtu.be/FeGmKmsYcRc))

---


## 🌟 Features

1. **Provision EC2 Instances**: Just tell the AI agent to create an EC2 instance, and it will handle the rest, providing you with the instance ID. 🛠️
2. **Terminate EC2 Instances**: Provide the instance ID, and the agent will terminate the instance for you. ❌
3. **MCP Server Integration**: Explore how custom MCP servers can be created and integrated with OpenAI Agents SDK. 🧩

---

## 🛠️ Tools in the MCP Server

The MCP server is a custom server with two tools:
1. **`initiate_aws_ec2_instance`**: Creates an AWS EC2 instance.
2. **`terminate_aws_ec2_instance`**: Terminates an AWS EC2 instance by its ID.

---

## 🚀 Getting Started

### Prerequisites
1. **Python 3.12+** (for local setup) or **Docker** (for containerized setup)
2. **AWS IAM Role**: Create an IAM role with the necessary permissions to manage EC2 instances.
3. **Environment Variables**: Prepare a `.env` file with the following variables:
    - `AWS_ACCESS_KEY_ID`
    - `AWS_SECRET_ACCESS_KEY`
    - `AWS_DEFAULT_REGION`
    - `OPENAI_API_KEY`
    - `AMI_ID`
    - `INSTANCE_TYPE`
    - `KEY_NAME`
    - `SECURITY_GROUP_IDS`
    - `AWS_REGION`

### 🏃‍♂️ Running the App
1. Clone the repository:
     ```bash
     git clone https://github.com/anirban1592/mcp-server-aws.git
     cd mcp-aws
     ```
2. Create `.env` file as shown in prerequisites

#### Option 1: Docker Setup (Recommended)

3. Build the Docker image:
     ```bash
     docker image build -t my-mcp .
     ```
4. Run the container:
     ```bash
     docker container run -it my-mcp
     ```

#### Option 2: Local Setup

3. Create and activate virtual environment:
     ```bash
     pip install uv
     uv venv .venv
     # Windows
     .venv\Scripts\activate
     # Unix/MacOS
     source .venv/bin/activate
     ```



4. Run the application:
     ```bash
     cd openai-agent/
     uv run agent.py
     ```

### 💬 Using the AI Agent

1. To create an EC2 instance:
    ```
    Enter your command: Create an EC2 instance
    ```

2. To terminate an EC2 instance:
    ```
    Enter your command: Terminate EC2 instance with ID <instance-id>
    ```

## ⚠️ Word of Caution

- **IAM Role and Credentials**: Please create AWS IAM roles and credentials at your own risk. Ensure you follow AWS best practices for security.
- **Billing and Security**: This app is a proof of concept (POC) and is intended for learning purposes only. We are not responsible for any billing issues or security incidents.

## 📚 Learnings

This project demonstrates:
1. How to integrate MCP servers with OpenAI Agents SDK
2. How to build a simple AI-driven application for AWS resource management

Enjoy exploring the power of AI and MCP servers! 🌟
