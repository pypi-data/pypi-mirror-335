"""
sgmap - AWS Security Group Mapping Tool

This module provides both a CLI tool and a library for analyzing and visualizing
AWS security group connections within a VPC.

Example:
    >>> import sgmap
    >>> vpc_and_sgs = sgmap.get_security_groups('vpc-12345678')
    >>> connections = sgmap.analyze_security_group_connections(vpc_and_sgs)
    >>> mermaid_diagram = sgmap.generate_mermaid_diagram(connections)
    >>> json_output = sgmap.generate_json_output(connections)
"""

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0.dev0"

# Public API
from .core import (
    get_security_groups,
    analyze_security_group_connections,
    generate_mermaid_diagram,
    generate_json_output
)

__all__ = [
    'get_security_groups',
    'analyze_security_group_connections',
    'generate_mermaid_diagram',
    'generate_json_output'
]