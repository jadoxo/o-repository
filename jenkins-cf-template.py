"""FROM"""
from ipaddress import ip_network

from ipify import get_ip

from troposphere import (
Base64,
ec2,
GetAtt,
Join,
Output,
Parameter,
Ref,
Template,
)

from troposphere.iam import (
InstanceProfile,
PolicyType as IAMPolicy,
Role,
)

from awacs.aws import (
Action,
Allow,
Policy,
Principal,
Statement,
)

from awacs.sts import AssumeRole

"""variables"""

ApplicationPort = "8080"
ApplicationName="jenkins"

PublicIpCidr=str(ip_network(get_ip()))

t=Template()

t.add_description("Effective DevOps in AWS: HelloWorld web application")


"""KeyPair Parameter"""

t.add_parameter(Parameter(
"KeyPair",
Description="KeyPair parameter",
Type="AWS::EC2::KeyPair::KeyName",
ConstraintDescription="must be the name of an existing EC2 KeyPair.",
))

""""Security Group creation"""

t.add_resource(ec2.SecurityGroup(
"TropoSecuritygroup",
GroupDescription="Allow SSH and TCP/{} access".format(ApplicationPort),
SecurityGroupIngress=[
	ec2.SecurityGroupRule(
	IpProtocol="tcp",
	FromPort="22",
	ToPort="22",
	CidrIp=PublicIpCidr,
),
	ec2.SecurityGroupRule(
	IpProtocol="tcp",
	FromPort=ApplicationPort,
	ToPort=ApplicationPort,
	CidrIp="0.0.0.0",
),

		     ],
))


"""UserData value"""

ud = Base64(Join('\n', [
"#!/bin/bash",
"sudo yum install --enablerepo=epel -y nodejs",
"wget http://bit.ly/2vESNuc -O /home/ec2-user/helloworld.js",
"wget http://bit.ly/2vVvT18 -O /etc/init/helloworld.conf",
"start helloworld"
]))

"""********ADD ROLE"""

t.add_resource(Role(
	"Role",
	AssumeRolePolicyDocument=Policy(
		Statement=[
			Statement(
			Effect=Allow,
			Action=[AssumeRole],
			Principal=Principal("Service", ["ec2.amazonaws.com"])
			)
		]
	)
))

"""********Instance Profile *********"""

t.add_resource(InstanceProfile(
	"InstanceProfile",
	Path="/",
	Roles=[Ref("Role")]
))

"""********EC2 Resource creation Creation"""

t.add_resource(
	ec2.Instance(
		"instance",
		InstanceType="t2.micro",
		SecurityGroups=[Ref("TropoSecuritygroup")],
		ImageId="mi-a4c7edb2",
		KeyName=Ref("KeyPair"),
		UserData=ud,
		IamInstanceProfile=Ref("InstanceProfile"),
	)
),
t.add_output(
	Output(
		"myOutputPublicIP",
		Value=GetAtt("instance", "PublicIp"),
	)
),

t.add_output(
	Output(
		"PublicIPAddress",
		Value=GetAtt("instance", "PublicDnsName"),
	)
),
print t.to_json()
