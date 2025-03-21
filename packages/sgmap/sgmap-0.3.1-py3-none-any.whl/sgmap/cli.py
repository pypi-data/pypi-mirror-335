"""
Command line interface for sgmap
"""

import sys
import click
from typing import Optional

from sgmap.core import (
    get_security_groups,
    analyze_security_group_connections,
    generate_mermaid_diagram,
    generate_json_output
)


@click.command()
@click.option(
    '--vpc-id', '-v',
    required=True,
    help='VPC ID to analyze security groups from'
)
@click.option(
    '--security-group-id', '-s',
    help='Optional security group ID to filter'
)
@click.option(
    '--json', '-j',
    is_flag=True,
    help='Output in JSON format instead of mermaid diagram'
)
@click.option(
    '--with-vpc',
    is_flag=True,
    help='Include VPC in the mermaid diagram (default is to show only security groups and their connections)'
)
def main(vpc_id: str, security_group_id: Optional[str] = None, json: bool = False, with_vpc: bool = False) -> None:
    """
    AWS Security Group Mapping Tool.
    
    Analyzes security group connections within a VPC and outputs a visualization
    in mermaid diagram format or JSON.
    """
    try:
        # Get VPC and security groups
        vpc_and_sgs = get_security_groups(vpc_id, security_group_id)
        
        if not vpc_and_sgs['vpc']:
            click.echo(f"VPC not found: {vpc_id}")
            sys.exit(1)
            
        if not vpc_and_sgs['security_groups']:
            click.echo(f"No security groups found for VPC ID: {vpc_id}" +
                      (f" and security group ID: {security_group_id}" if security_group_id else ""))
            sys.exit(1)
        
        # Analyze connections
        connections = analyze_security_group_connections(vpc_and_sgs)
        
        # Generate output
        if json:
            output = generate_json_output(connections)
        else:
            output = generate_mermaid_diagram(connections, with_vpc)
        
        click.echo(output)
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()