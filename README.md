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

![alt text](https://github.com/grv231/CloudInfrastructure-devops/blob/master/Images/Security_Groups.png "Security_Groups")

3.	Next step was installing Ansible on the instance. Before this is done, make sure there is Python installed. For this purpose, I SSH’ed into the Ubuntu EC2 instance and ran the following UNIX commands to setup Ansible:

```shell
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install software-properties-common
sudo apt-add-repository ppa:ansible/ansible
sudo apt-get update
sudo apt-get install ansible
```
Check the ansible version using: **ansible -–version**

![alt text](https://github.com/grv231/CloudInfrastructure-devops/blob/master/Images/Ansible_version.png "Ansible_Version")

4.	After installing Ansible, we start building our **autoscaling.yml** configuration script for launching the instances in a load balanced, auto-scaling group.
5.	Apart from autoscaling two other files containing the variables were created to abstract the automation script from the variables script and remove hardcoding important confidential information in the script. The two files are:

- **amiKeys.yml** – This file consists of AWS Access Key and AWS Secret Access Key for the user who is running the script. This file needs be changed for the user running the script.
- **regionInfo.yml** – This file consists region where we want our load balancers and autoscaling launch configuration to be created. Moreover keypair, security group (I used the one created with cloudformation for redis server) and subnetID (just an added feature) needs to be given here as configuration paramters to be used in the main autoscaling script.
6.	Make sure before running the autoscale.yml script, following things are completed:

- Permissions are correct on files or atleast execute permissions are there on each *“. yml”* file.
- Enter the ami of linux/ubuntu instances being used (Ubuntu was used here)
- All the files are kept in the same folder

![alt text](https://github.com/grv231/CloudInfrastructure-devops/blob/master/Images/Files_Location.png "Files_location")

7. Run the ansible script by issuing the following command: **ansible-playbook autoscale.yml**

![alt text](https://github.com/grv231/CloudInfrastructure-devops/blob/master/Images/Ansible_output_autoscaling.png "Ansible_autoscaling")

- This script launches the autoscaling ec2 instances in regions mentioned in the file. Now in this case, the regions are **us-west-1** and **us-west-2**. However, since autoscaling creates it randomly, in this case, both the instances came up in the same region. Moreover,  the configuration file has been given to pop up maximum 4 instances in case of high traffic and extended loads.

![alt text](https://github.com/grv231/CloudInfrastructure-devops/blob/master/Images/Autoscaled_instances_EC2.png "Autoscaled_EC2_instances")

- The groups asg-1 and asg-2 were created as mentioned in the **autoscale.yml** configuration file. One is terminated since a CloudWatch alarm has been setupwhere the instances will be taken down if cpu utilization is less than or equal to 10%. They will pop right back up if cpu utilization is more than 20%. This is a simulation of a healthcheck to create and remove autoscaled EC2 instances.

```yaml
# cloud watch alarm
   - ec2_metric_alarm:
      aws_access_key: '{{aws_access}}'
      aws_secret_key: '{{aws_secret}}'
      state: present
      region: "{{regi}}"
      name: "{{item.names}}"
      metric: "CPUUtilization"
      namespace: "AWS/EC2"
      statistic: Average
      comparison: "{{item.compare}}"
      threshold: "{{item.limits}}"
      period: 60
      evaluation_periods: 1
      unit: "Percent"
      description: "{{item.desc}}"
      dimensions: {'AutoScalingGroupName':'{{auto_sc}}'}
      alarm_actions: "{{item.pol}}"
     with_items:
      - names: "cpuUP_{{auto_sc}}"
        compare: ">="
        limits: "20.0"
        desc: "This will alarm when the average cpu usage of the ASG is greater than 20% for 1 minute"
        pol: "{{policies.results[0]['arn']}}"
      - names: "cpuDown_{{auto_sc}}"
        compare: "<="
        limits: "10.0"
        desc: "This will alarm when the average cpu usage of the ASG is less than 10% for 1 minute"
        pol: "{{policies.results[1]['arn']}}"
```
8. **Stress Testing**
- Finally, to check for scaling the application, stress package of debian was used. LOad was simulated on one running autoscaled instance. Since cloudwatch alarm checks for CPU utilization to be 20%, a new instance pops back right up using command.

**stress -c 4** command was used to simulate the load. Here, 4 CPU's are being invoked as a load testing parameter.

![alt text](https://github.com/grv231/CloudInfrastructure-devops/blob/master/Images/Stress_Testing_EC2Instances.png "Stress_testing")

- After the above mentioned command has run for a good period of time exit it and using AWS graphical user interface, we checked that a new instance pops up as we subjected to stress operation.


![alt text](https://github.com/grv231/CloudInfrastructure-devops/blob/master/Images/New_instances_stressTest.png "New_instances_creation")

- Moreover, we further confirm the load testing parameters with our CloudWatch logs and the image representation is shown below:

![alt text](https://github.com/grv231/CloudInfrastructure-devops/blob/master/Images/Cloudwatch_stats_stressTest.png "Cloudwatch_stressTest")

- Finally, when CPU utilization again goes down, the instance that were generated as part of cloudwatch alarm are terminated. Moreover, minimum instances generated is mentioned in the configuration files as 2 and maximum as 4.

![alt text](https://github.com/grv231/CloudInfrastructure-devops/blob/master/Images/ShuttingDown_EC2Instances_autoscaled.png "Scaledown_EC2instances")

### :two: Cloud infrastructure setup using Cloudformation YAML template, Python Troposphere and Redis server
Redis Instance was created on a EC2 server instance using Troposphere python library code on uploaded to Cloudformation as a template from a sample S3 bucket.

**Creation Steps:**
1.	1.	Firstly, code was developed using python troposphere library. Troposphere was installed using: **sudo pip install troposhere** 
2.	Code was generated using python-troposphere and saved as a python file (*redis-server.py*).
3. Python file was converted to a template file using: *python redis-server.py > redis-server.template*
4. Now in AWS Cloudformation GUI, the template was uploaded and following steps were followed:

- Create Stack --> Choose a Template (Upload Template to S3) --> Upload redis-server.py --> Keep all options default and keep clicking next and launch
 
![alt text](https://github.com/grv231/CloudInfrastructure-devops/blob/master/Images/CloudInfrastructure_progress.png "Cloudformation_infrastructure")

- The stack is generated from the stack above. The output that we get from the Cloudformation script gives us the SSH key that can be used straight away to used to enter the respective box. Moreover, WebURL for the EC2 instance endpoint is also generated that can be used easily to access the instance on web using that endpoint.

![alt text](https://github.com/grv231/CloudInfrastructure-devops/blob/master/Images/Cloudformation_script_output.png "Cloudformation_scriptOutput")

 **Alternative script - AWS CLoudfomration Script in YAML**
 An alternative script has been created as well to setup a redis server. However, this script gives added flexibility to deploy the infrastructure on various environments such as Production, UAT, development, with added benefit on security groups etc. creation inside the script and since it is the part of AWS stack, Cloudformation script in YAML format offers big benefits in comparison to other tools like Terraform, Packr and Troposphere.
 
The script has been kept in the location **/Cloud_infrastructure_templates/cloudformation-redis.yml** of this project
 
```yaml
# Alternative Cloudformation template to spin up redis server using cloudformation yml
Parameters:
  SecurityGroupDescription:
    Description: Security Group Description (Simple parameter)
    Type: String
  EnvironmentName:
    Description: Environment Name
    Type: String
    AllowedValues: [development, production]
    ConstraintDescription: Must be development or production
  SecurityGroupIngressCIDR:
    Description: The IP address range that can be used to communicate to the EC2 instances
    Type: String
    MinLength: '9'
    MaxLength: '18'
    Default: 0.0.0.0/0
    AllowedPattern: (\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})
    ConstraintDescription: must be a valid IP CIDR range of the form x.x.x.x/x.
  SecurityGroupPort1:
    Description: Simple Description of a Number Parameter, with MinValue and MaxValue
    Type: Number
    MinValue: 10
    MaxValue: 65535
  SecurityGroupPort2:
    Description: Simple Description of a Number Parameter, with MinValue and MaxValue
    Type: Number
    MinValue: 10
    MaxValue: 65535
  KeyName:
    Description: Name of an existing EC2 KeyPair to enable SSH access to the instances. Linked to AWS Parameter
    Type: AWS::EC2::KeyPair::KeyName
    ConstraintDescription: must be the name of an existing EC2 KeyPair.
  MyVPC:
    Description: VPC to be used for operating in
    Type: AWS::EC2::VPC::Id

Mappings:
  RegionMap:
    us-west-1:
      AMI: "ami-925144f2"
    us-west-2:
      AMI: "ami-925144f2"
  EnvironmentToInstanceType:
    # Smaller instance in development
    development:
      instanceType: t2.micro
    # For spinning up a bigger instance type in production
    production:
      instanceType: t2.small
 
Resources:
  MyRedisEC2Instance:
    # Creating EC2 instance with ubuntu image 
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !FindInMap [EnvironmentToInstanceType, !Ref 'EnvironmentName', instanceType]
      ImageId: !FindInMap [RegionMap, !Ref "AWS::Region", AMI]
      KeyName: !Ref KeyName
      SubnetId: subnet-87f907dc
      # 172.31.16.0/20
      SecurityGroupIds:
        - !Ref InstanceSecurityGroup
      Tags:
        - Key: "name"
          Value: "MyRedisEC2Instance"
      UserData:
        Fn::Base64: |
           #!/bin/bash    
           apt-get update
           apt-get -y upgrade
           apt-get -y install redis-server
           systemctl -y enable redis-server.service
           sudo sed -i "s/127.0.0.1/0.0.0.0/i" /etc/redis/redis.conf

  MyEIP:
    # Optional to create elastic IP of redis server in case we do keep it in autoscaling group later
    Type: AWS::EC2::EIP
    Properties:
      InstanceId: !Ref MyRedisEC2Instance

  InstanceSecurityGroup:
    # Security group for redis-server
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: "RedisSG"
      GroupDescription: !Ref SecurityGroupDescription
      VpcId: !Ref MyVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          CidrIp: !Ref SecurityGroupIngressCIDR
          FromPort: !Ref SecurityGroupPort1
          ToPort: !Ref SecurityGroupPort1
        - IpProtocol: tcp
          CidrIp: !Ref SecurityGroupIngressCIDR
          FromPort: !Ref SecurityGroupPort2
          ToPort: !Ref SecurityGroupPort2
          IpProtocol: tcp
```
 










