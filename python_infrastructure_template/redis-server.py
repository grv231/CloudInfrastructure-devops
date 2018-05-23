from troposphere import Ref, Template, Parameter, Output, Join, GetAtt, Base64
import troposphere.ec2 as ec2

# Create the template object
t = Template()

# Add security group 
# Add ssh Key pair
# Add ami-id and instance type

sg = ec2.SecurityGroup("RedisSg")
sg.GroupDescription = "Allow access to ports 80, 22 and redis cli to EC2 server"

# Setup the ports access for security groups
sg.SecurityGroupIngress = [
    ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "22", ToPort = "22", CidrIp = "0.0.0.0/0"),
    ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "6379", ToPort = "6379", CidrIp = "0.0.0.0/0"),
]

# Informing the security group add resources to the template
# This is a method of Troposphere library, not cloudformation
t.add_resource(sg)

# Adding ssh Keypair externally as cannot be generated here
# These variables are NOT cloudformation attributes
keypair = t.add_parameter(Parameter(
        "KeyName",
        Description = "Name of SSH keypair that will be used to access the instance",
        Type = "String"
    ))

# Creating an instance variable for EC2 deployment
instance = ec2.Instance("dbserver")
instance.ImageId = "ami-925144f2"
instance.InstanceType = "t2.micro"

# Using the Ref module of troposphere for list values of various attributes
# Ref is defined in the Cloudformation template documentation
instance.SecurityGroups = [Ref(sg)]
instance.KeyName = Ref(keypair)

# User data section for running bash scripts on instance after instance creation
# Encoding binary data to Base 64 for successful transfer
# Replacing the redis.conf file for a telnet connection with autoscaled instances
ud = Base64(Join("\n", 
    [
        "#!/bin/bash",
        "sudo apt-get update",
        "sudo apt-get -y upgrade",
        "sudo apt-get -y install redis-server",
        "sudo systemctl -y enable redis-server.service",
        "sudo sed -i 's/127.0.0.1/0.0.0.0/i' /etc/redis/redis.conf"
    ]))

            
instance.UserData = ud

# Add the instance resources to the template
t.add_resource(instance)

# Adding output for better user experience
t.add_output(Output(
        "InstanceAccess",
        Description = "Command to access the instance using SSH",
        
        #Join function comes from Cloudformation to join separate strings together
        # GetAtt function is also given to us by Cloudformation
        Value = Join("",["ssh -i ~/.ssh/Redis-Key.pem ubuntu@",GetAtt(instance,"PublicDnsName")])
))

# This is used to output URL of the webserver
t.add_output(Output(
        "WebUrl",
        Description = "The URL of webserver",
        Value = Join("",["http://",GetAtt(instance,"PublicDnsName")])
))

print(t.to_json())