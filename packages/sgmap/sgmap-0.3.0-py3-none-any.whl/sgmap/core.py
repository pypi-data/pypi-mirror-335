"""
Core functionality for sgmap
"""

import json
import boto3
from typing import Dict, List, Optional, Any


def get_name_from_tags(tags: List[Dict[str, str]]) -> str:
    """
    Get name from tags.
    
    Args:
        tags: List of tag dictionaries
        
    Returns:
        Name from tags or empty string if not found
    """
    for tag in tags:
        if tag.get('Key') == 'Name':
            return tag.get('Value', '')
    return ''


def get_security_groups(vpc_id: str, security_group_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get security groups and VPC info for a given VPC ID and optionally filter by security group ID.
    
    Args:
        vpc_id: The VPC ID to filter security groups
        security_group_id: Optional security group ID to filter
        
    Returns:
        Dictionary with VPC info and security groups
    """
    ec2 = boto3.client('ec2')
    
    # Get VPC info
    vpc_response = ec2.describe_vpcs(VpcIds=[vpc_id])
    vpc_info = vpc_response['Vpcs'][0] if vpc_response['Vpcs'] else None
    
    # Get security groups
    filters = [{'Name': 'vpc-id', 'Values': [vpc_id]}]
    
    if security_group_id:
        filters.append({'Name': 'group-id', 'Values': [security_group_id]})
    
    sg_response = ec2.describe_security_groups(Filters=filters)
    
    return {
        'vpc': vpc_info,
        'security_groups': sg_response['SecurityGroups']
    }


def analyze_security_group_connections(vpc_and_sgs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze security group connections and build a connection map.
    
    Args:
        vpc_and_sgs: Dictionary with VPC info and security groups
        
    Returns:
        Dictionary with VPC info and security group connections
    """
    vpc_info = vpc_and_sgs['vpc']
    security_groups = vpc_and_sgs['security_groups']
    
    # Create a mapping of security group ID to name for easier reference
    sg_id_to_name = {sg['GroupId']: sg['GroupName'] for sg in security_groups}
    
    # Initialize connection map
    connections = {
        'vpc': {
            'id': vpc_info['VpcId'],
            'cidr': vpc_info.get('CidrBlock', ''),
            'name': get_name_from_tags(vpc_info.get('Tags', [])),
            'tags': vpc_info.get('Tags', [])
        },
        'security_groups': {}
    }
    
    for sg in security_groups:
        sg_id = sg['GroupId']
        connections['security_groups'][sg_id] = {
            'name': sg['GroupName'],
            'description': sg.get('Description', ''),
            'tags': sg.get('Tags', []),
            'inbound': [],
            'outbound': []
        }
        
        # Process inbound rules (ingress)
        for rule in sg.get('IpPermissions', []):
            for group in rule.get('UserIdGroupPairs', []):
                if 'GroupId' in group:
                    target_sg_id = group['GroupId']
                    connections['security_groups'][sg_id]['inbound'].append({
                        'type': 'security_group',
                        'id': target_sg_id,
                        'name': sg_id_to_name.get(target_sg_id, target_sg_id),
                        'protocol': rule.get('IpProtocol', 'all'),
                        'from_port': rule.get('FromPort', 'all'),
                        'to_port': rule.get('ToPort', 'all'),
                        'description': group.get('Description', '')
                    })
            
            # Add CIDR connections
            for cidr in rule.get('IpRanges', []):
                connections['security_groups'][sg_id]['inbound'].append({
                    'type': 'cidr',
                    'id': cidr.get('CidrIp', 'unknown'),
                    'name': cidr.get('Description', cidr.get('CidrIp', 'unknown')),
                    'protocol': rule.get('IpProtocol', 'all'),
                    'from_port': rule.get('FromPort', 'all'),
                    'to_port': rule.get('ToPort', 'all'),
                    'description': cidr.get('Description', '')
                })
        
        # Process outbound rules (egress)
        for rule in sg.get('IpPermissionsEgress', []):
            for group in rule.get('UserIdGroupPairs', []):
                if 'GroupId' in group:
                    target_sg_id = group['GroupId']
                    connections['security_groups'][sg_id]['outbound'].append({
                        'type': 'security_group',
                        'id': target_sg_id,
                        'name': sg_id_to_name.get(target_sg_id, target_sg_id),
                        'protocol': rule.get('IpProtocol', 'all'),
                        'from_port': rule.get('FromPort', 'all'),
                        'to_port': rule.get('ToPort', 'all'),
                        'description': group.get('Description', '')
                    })
            
            # Add CIDR connections
            for cidr in rule.get('IpRanges', []):
                connections['security_groups'][sg_id]['outbound'].append({
                    'type': 'cidr',
                    'id': cidr.get('CidrIp', 'unknown'),
                    'name': cidr.get('Description', cidr.get('CidrIp', 'unknown')),
                    'protocol': rule.get('IpProtocol', 'all'),
                    'from_port': rule.get('FromPort', 'all'),
                    'to_port': rule.get('ToPort', 'all'),
                    'description': cidr.get('Description', '')
                })
    
    return connections

def generate_mermaid_diagram(connections: Dict[str, Any], include_vpc: bool = False) -> str:
    """
    Generate a mermaid diagram from security group connections.
    
    Args:
        connections: Dictionary with VPC info and security group connections
        include_vpc: Whether to include VPC in the diagram (default: True)
        
    Returns:
        Mermaid diagram as a string
    """
    mermaid = ["```mermaid", "flowchart LR"]
    
    # Track link indices
    link_index = 0
    vpc_links = []
    inbound_links = []
    outbound_links = []
    
    vpc = connections['vpc']
    vpc_id = vpc['id']
    vpc_node_id = f"VPC_{vpc_id.replace('-', '_')}"
    
    # Add VPC node if include_vpc is True
    if include_vpc:
        vpc_name = vpc['name'] if vpc['name'] else vpc_id
        vpc_label = f"{vpc_name}\\n({vpc_id})\\n{vpc['cidr']}"
        mermaid.append(f"    {vpc_node_id}[\"🌐 {vpc_label}\"]")
    
    # Add security group nodes
    for sg_id, sg_data in connections['security_groups'].items():
        node_id = f"SG_{sg_id.replace('-', '_')}"
        
        # Add tag information if available
        tag_info = ""
        for tag in sg_data['tags']:
            if tag.get('Key') != 'Name':  # Name is already in the label
                tag_info += f"\\n{tag.get('Key')}: {tag.get('Value')}"
        
        node_label = f"{sg_data['name']}\\n({sg_id}){tag_info}"
        mermaid.append(f"    {node_id}[\"{node_label}\"]")
        
        # Add VPC to security group connection if include_vpc is True
        if include_vpc:
            mermaid.append(f"    {vpc_node_id} -->|belongs to| {node_id}")
            vpc_links.append(link_index)
            link_index += 1
    
    # Add security group connections
    for sg_id, sg_data in connections['security_groups'].items():
        source_node = f"SG_{sg_id.replace('-', '_')}"
        
        # Add inbound connections (security group <- 許可している接続元)
        for conn in sg_data['inbound']:
            if conn['type'] == 'security_group':
                target_node = f"SG_{conn['id'].replace('-', '_')}"
                protocol = conn['protocol']
                ports = f"{conn['from_port']}-{conn['to_port']}" if conn['from_port'] != 'all' else 'all'
                label = f"inbound: {protocol}/{ports}"
                mermaid.append(f"    {target_node} -->|{label}| {source_node}")
                inbound_links.append(link_index)
                link_index += 1
            elif conn['type'] == 'cidr':
                # Create a CIDR node for external connections
                cidr_id = conn['id'].replace('.', '_').replace('/', '_')
                cidr_node = f"CIDR_{cidr_id}"
                cidr_label = conn['id']
                if conn['description']:
                    cidr_label += f"\\n({conn['description']})"
                
                # Add CIDR node
                mermaid.append(f"    {cidr_node}[\"🔌 {cidr_label}\"]")
                
                protocol = conn['protocol']
                ports = f"{conn['from_port']}-{conn['to_port']}" if conn['from_port'] != 'all' else 'all'
                label = f"inbound: {protocol}/{ports}"
                mermaid.append(f"    {cidr_node} -->|{label}| {source_node}")
                inbound_links.append(link_index)
                link_index += 1
        
        # Add outbound connections (security group -> 許可している接続先)
        for conn in sg_data['outbound']:
            if conn['type'] == 'security_group':
                target_node = f"SG_{conn['id'].replace('-', '_')}"
                protocol = conn['protocol']
                ports = f"{conn['from_port']}-{conn['to_port']}" if conn['from_port'] != 'all' else 'all'
                label = f"outbound: {protocol}/{ports}"
                mermaid.append(f"    {source_node} -->|{label}| {target_node}")
                outbound_links.append(link_index)
                link_index += 1
            elif conn['type'] == 'cidr':
                # Create a CIDR node for external connections
                cidr_id = conn['id'].replace('.', '_').replace('/', '_')
                cidr_node = f"CIDR_{cidr_id}"
                cidr_label = conn['id']
                if conn['description']:
                    cidr_label += f"\\n({conn['description']})"
                
                # Add CIDR node
                mermaid.append(f"    {cidr_node}[\"🔌 {cidr_label}\"]")
                
                protocol = conn['protocol']
                ports = f"{conn['from_port']}-{conn['to_port']}" if conn['from_port'] != 'all' else 'all'
                label = f"outbound: {protocol}/{ports}"
                mermaid.append(f"    {source_node} -->|{label}| {cidr_node}")
                outbound_links.append(link_index)
                link_index += 1
    
    # Add link styles
    if vpc_links:
        # VPC links can remain default color
        pass
    
    if inbound_links:
        mermaid.append(f"    linkStyle {','.join(map(str, inbound_links))} stroke:#cccccc,stroke-width:2")
    
    if outbound_links:
        mermaid.append(f"    linkStyle {','.join(map(str, outbound_links))} stroke:#555555,stroke-width:2")
    
    mermaid.append("```")
    return "\n".join(mermaid)
    return "\n".join(mermaid)


def generate_json_output(connections: Dict[str, Any]) -> str:
    """
    Generate JSON output from security group connections.
    
    Args:
        connections: Dictionary with VPC info and security group connections
        
    Returns:
        JSON string
    """
    return json.dumps(connections, indent=2)