"""
Tests for sgmap.core module
"""

import json
from unittest.mock import patch, MagicMock

import pytest

from sgmap.core import (
    get_name_from_tags,
    get_security_groups,
    analyze_security_group_connections,
    generate_mermaid_diagram,
    generate_json_output
)


class TestGetNameFromTags:
    """Tests for get_name_from_tags function"""

    def test_get_name_from_tags_with_name(self):
        """Test get_name_from_tags with a Name tag"""
        tags = [
            {'Key': 'Environment', 'Value': 'Test'},
            {'Key': 'Name', 'Value': 'TestName'},
            {'Key': 'Project', 'Value': 'TestProject'}
        ]
        assert get_name_from_tags(tags) == 'TestName'

    def test_get_name_from_tags_without_name(self):
        """Test get_name_from_tags without a Name tag"""
        tags = [
            {'Key': 'Environment', 'Value': 'Test'},
            {'Key': 'Project', 'Value': 'TestProject'}
        ]
        assert get_name_from_tags(tags) == ''

    def test_get_name_from_tags_empty_list(self):
        """Test get_name_from_tags with an empty list"""
        assert get_name_from_tags([]) == ''


class TestGetSecurityGroups:
    """Tests for get_security_groups function"""

    def test_get_security_groups_with_vpc_id(self, mock_boto3_client, sample_vpc_response, sample_security_groups_response):
        """Test get_security_groups with VPC ID only"""
        # Setup mock responses
        mock_boto3_client.describe_vpcs.return_value = sample_vpc_response
        mock_boto3_client.describe_security_groups.return_value = sample_security_groups_response

        # Call the function
        result = get_security_groups('vpc-12345678')

        # Verify the result
        assert result['vpc'] == sample_vpc_response['Vpcs'][0]
        assert result['security_groups'] == sample_security_groups_response['SecurityGroups']

        # Verify the API calls
        mock_boto3_client.describe_vpcs.assert_called_once_with(VpcIds=['vpc-12345678'])
        mock_boto3_client.describe_security_groups.assert_called_once_with(
            Filters=[{'Name': 'vpc-id', 'Values': ['vpc-12345678']}]
        )

    def test_get_security_groups_with_vpc_and_sg_id(self, mock_boto3_client, sample_vpc_response, sample_security_groups_response):
        """Test get_security_groups with VPC ID and security group ID"""
        # Setup mock responses
        mock_boto3_client.describe_vpcs.return_value = sample_vpc_response
        mock_boto3_client.describe_security_groups.return_value = sample_security_groups_response

        # Call the function
        result = get_security_groups('vpc-12345678', 'sg-11111111')

        # Verify the result
        assert result['vpc'] == sample_vpc_response['Vpcs'][0]
        assert result['security_groups'] == sample_security_groups_response['SecurityGroups']

        # Verify the API calls
        mock_boto3_client.describe_vpcs.assert_called_once_with(VpcIds=['vpc-12345678'])
        mock_boto3_client.describe_security_groups.assert_called_once_with(
            Filters=[
                {'Name': 'vpc-id', 'Values': ['vpc-12345678']},
                {'Name': 'group-id', 'Values': ['sg-11111111']}
            ]
        )

    def test_get_security_groups_vpc_not_found(self, mock_boto3_client):
        """Test get_security_groups when VPC is not found"""
        # Setup mock responses
        mock_boto3_client.describe_vpcs.return_value = {'Vpcs': []}

        # Call the function
        result = get_security_groups('vpc-nonexistent')

        # Verify the result
        assert result['vpc'] is None


class TestAnalyzeSecurityGroupConnections:
    """Tests for analyze_security_group_connections function"""

    def test_analyze_security_group_connections(self, sample_vpc_and_sgs):
        """Test analyze_security_group_connections with sample data"""
        # Call the function
        result = analyze_security_group_connections(sample_vpc_and_sgs)

        # Verify the result structure
        assert 'vpc' in result
        assert 'security_groups' in result

        # Verify VPC info
        assert result['vpc']['id'] == 'vpc-12345678'
        assert result['vpc']['cidr'] == '10.0.0.0/16'
        assert result['vpc']['name'] == 'TestVPC'

        # Verify security groups
        assert 'sg-11111111' in result['security_groups']
        assert 'sg-22222222' in result['security_groups']
        assert 'sg-33333333' in result['security_groups']

        # Verify WebServer security group connections
        web_server = result['security_groups']['sg-11111111']
        assert web_server['name'] == 'WebServer'
        assert len(web_server['inbound']) == 2  # From LoadBalancer and from 0.0.0.0/0
        assert len(web_server['outbound']) == 1  # To Database

        # Verify LoadBalancer security group connections
        load_balancer = result['security_groups']['sg-22222222']
        assert load_balancer['name'] == 'LoadBalancer'
        assert len(load_balancer['inbound']) == 1  # From 0.0.0.0/0
        assert len(load_balancer['outbound']) == 1  # To WebServer

        # Verify Database security group connections
        database = result['security_groups']['sg-33333333']
        assert database['name'] == 'Database'
        assert len(database['inbound']) == 1  # From WebServer
        assert len(database['outbound']) == 1  # To 0.0.0.0/0


class TestGenerateMermaidDiagram:
    """Tests for generate_mermaid_diagram function"""

    def test_generate_mermaid_diagram_with_vpc(self, sample_vpc_and_sgs):
        """Test generate_mermaid_diagram with VPC included"""
        # First analyze the connections
        connections = analyze_security_group_connections(sample_vpc_and_sgs)

        # Then generate the diagram
        diagram = generate_mermaid_diagram(connections, include_vpc=True)

        # Verify the diagram structure
        assert diagram.startswith('```mermaid')
        assert diagram.endswith('```')
        assert 'flowchart LR' in diagram

        # Verify VPC node is included
        assert 'VPC_vpc_12345678' in diagram
        assert 'TestVPC' in diagram

        # Verify security group nodes are included
        assert 'SG_sg_11111111' in diagram
        assert 'SG_sg_22222222' in diagram
        assert 'SG_sg_33333333' in diagram

        # Verify connections are included
        assert 'inbound: tcp/80' in diagram
        assert 'outbound: tcp/3306' in diagram

    def test_generate_mermaid_diagram_without_vpc(self, sample_vpc_and_sgs):
        """Test generate_mermaid_diagram without VPC included"""
        # First analyze the connections
        connections = analyze_security_group_connections(sample_vpc_and_sgs)

        # Then generate the diagram
        diagram = generate_mermaid_diagram(connections, include_vpc=False)

        # Verify the diagram structure
        assert diagram.startswith('```mermaid')
        assert diagram.endswith('```')
        assert 'flowchart LR' in diagram

        # Verify VPC node is not included
        assert 'VPC_vpc_12345678' not in diagram
        assert 'belongs to' not in diagram
        
        # Verify security group nodes are included
        assert 'SG_sg_11111111' in diagram
        assert 'SG_sg_22222222' in diagram
        assert 'SG_sg_33333333' in diagram


class TestGenerateJsonOutput:
    """Tests for generate_json_output function"""

    def test_generate_json_output(self, sample_vpc_and_sgs):
        """Test generate_json_output with sample data"""
        # First analyze the connections
        connections = analyze_security_group_connections(sample_vpc_and_sgs)

        # Then generate the JSON output
        json_output = generate_json_output(connections)

        # Verify the JSON structure
        parsed_json = json.loads(json_output)
        assert 'vpc' in parsed_json
        assert 'security_groups' in parsed_json

        # Verify VPC info
        assert parsed_json['vpc']['id'] == 'vpc-12345678'
        assert parsed_json['vpc']['cidr'] == '10.0.0.0/16'
        assert parsed_json['vpc']['name'] == 'TestVPC'

        # Verify security groups
        assert 'sg-11111111' in parsed_json['security_groups']
        assert 'sg-22222222' in parsed_json['security_groups']
        assert 'sg-33333333' in parsed_json['security_groups']