"""
Pytest configuration for sgmap tests
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_boto3_client():
    """
    Fixture to mock boto3.client
    """
    with patch('boto3.client') as mock_client:
        # Create a mock EC2 client
        mock_ec2 = MagicMock()
        mock_client.return_value = mock_ec2
        yield mock_ec2


@pytest.fixture
def sample_vpc_response():
    """
    Fixture for a sample VPC response
    """
    return {
        'Vpcs': [
            {
                'VpcId': 'vpc-12345678',
                'CidrBlock': '10.0.0.0/16',
                'Tags': [
                    {'Key': 'Name', 'Value': 'TestVPC'},
                    {'Key': 'Environment', 'Value': 'Test'}
                ]
            }
        ]
    }


@pytest.fixture
def sample_security_groups_response():
    """
    Fixture for a sample security groups response
    """
    return {
        'SecurityGroups': [
            {
                'GroupId': 'sg-11111111',
                'GroupName': 'WebServer',
                'Description': 'Web server security group',
                'VpcId': 'vpc-12345678',
                'Tags': [
                    {'Key': 'Name', 'Value': 'WebServer'},
                    {'Key': 'Role', 'Value': 'Web'}
                ],
                'IpPermissions': [
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'UserIdGroupPairs': [
                            {
                                'GroupId': 'sg-22222222',
                                'Description': 'Allow from LoadBalancer'
                            }
                        ],
                        'IpRanges': [
                            {
                                'CidrIp': '0.0.0.0/0',
                                'Description': 'Allow HTTP from anywhere'
                            }
                        ]
                    }
                ],
                'IpPermissionsEgress': [
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 3306,
                        'ToPort': 3306,
                        'UserIdGroupPairs': [
                            {
                                'GroupId': 'sg-33333333',
                                'Description': 'Allow to Database'
                            }
                        ],
                        'IpRanges': []
                    }
                ]
            },
            {
                'GroupId': 'sg-22222222',
                'GroupName': 'LoadBalancer',
                'Description': 'Load balancer security group',
                'VpcId': 'vpc-12345678',
                'Tags': [
                    {'Key': 'Name', 'Value': 'LoadBalancer'},
                    {'Key': 'Role', 'Value': 'LB'}
                ],
                'IpPermissions': [
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 443,
                        'ToPort': 443,
                        'UserIdGroupPairs': [],
                        'IpRanges': [
                            {
                                'CidrIp': '0.0.0.0/0',
                                'Description': 'Allow HTTPS from anywhere'
                            }
                        ]
                    }
                ],
                'IpPermissionsEgress': [
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'UserIdGroupPairs': [
                            {
                                'GroupId': 'sg-11111111',
                                'Description': 'Allow to WebServer'
                            }
                        ],
                        'IpRanges': []
                    }
                ]
            },
            {
                'GroupId': 'sg-33333333',
                'GroupName': 'Database',
                'Description': 'Database security group',
                'VpcId': 'vpc-12345678',
                'Tags': [
                    {'Key': 'Name', 'Value': 'Database'},
                    {'Key': 'Role', 'Value': 'DB'}
                ],
                'IpPermissions': [
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 3306,
                        'ToPort': 3306,
                        'UserIdGroupPairs': [
                            {
                                'GroupId': 'sg-11111111',
                                'Description': 'Allow from WebServer'
                            }
                        ],
                        'IpRanges': []
                    }
                ],
                'IpPermissionsEgress': [
                    {
                        'IpProtocol': '-1',
                        'FromPort': -1,
                        'ToPort': -1,
                        'UserIdGroupPairs': [],
                        'IpRanges': [
                            {
                                'CidrIp': '0.0.0.0/0',
                                'Description': 'Allow all outbound traffic'
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture
def sample_vpc_and_sgs(sample_vpc_response, sample_security_groups_response):
    """
    Fixture for a sample VPC and security groups data structure
    """
    return {
        'vpc': sample_vpc_response['Vpcs'][0],
        'security_groups': sample_security_groups_response['SecurityGroups']
    }