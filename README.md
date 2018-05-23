# Autoscaling using Devops and Cloudformation on AWS:cloud:

## Description:
This project basically focuses on two tasks namely:
 - Creating EC2 instances on AWS in autoscaled group behind a load balancer with Cloudwatch alarm setup using Ansible YAML file.
 - A simple Redis server installed on an EC2 instance using Cloudformation YAML and Python Troposphere script.

## Setting up the project:
A separete EC2 instance should be spin-up and Ansible should be installed using Python-pip or other installation. This will serve as the Master node for formulating autoscaled EC2 instances

## Tasks
Following are the operations used for this project:

### :one: EC2 instances Autoscaling Group
We can start building our EC2 instances in an autoscaling group with load balancer in the front balancing the application EC2 instances. The tool used to create automation infrastructure is Ansible, as it has great documentation, good features of implementing the changes and the YAML scripts can be generated and tested quickly. The setup is as follows:

**Creation Steps:**
1.	First step is to create an EC2 instance and install ansible on it. Ubuntu free-tier AMI was chosen for this. This instance will serve as the master node from which changes can be pushed to all EC2 instances once they are created.
2.	Create a new security group (test-ansible-instance for this example)  with configuration set as below (only HTTP and SSH works):


