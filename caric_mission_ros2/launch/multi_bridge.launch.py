#!/usr/bin/env python3
"""
Multi-Domain Bridge Launch File

Launch multiple domain bridges simultaneously for raffles, jurong, and changi configurations.
Each bridge instance runs independently and bridges different domain pairs.

Usage:
ros2 launch caric_mission_ros2 multi_bridge.launch.py

This will start:
- Jurong bridge: Domain 0 <-> Domain 1  
- Raffles bridge: Domain 0 <-> Domain 2
- Changi bridge: Domain 0 <-> Domain 3
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """Generate launch description for multiple domain bridges."""
    
    # Package name argument
    package_name_arg = DeclareLaunchArgument(
        'package_name',
        default_value='caric_mission_ros2',
        description='Name of the package containing the config files'
    )
    
    enable_jurong_bridge_arg = DeclareLaunchArgument(
        'enable_jurong_bridge', 
        default_value='true',
        description='Enable jurong bridge (domain 0 <-> domain 1)'
    )
    
    # Enable/disable specific bridges
    enable_raffles_bridge_arg = DeclareLaunchArgument(
        'enable_raffles_bridge',
        default_value='true',
        description='Enable raffles bridge (domain 0 <-> domain 2)'
    )
    
    enable_changi_bridge_arg = DeclareLaunchArgument(
        'enable_changi_bridge',
        default_value='true',
        description='Enable changi bridge (domain 0 <-> domain 3)'
    )

    # Get launch configuration values
    package_name = LaunchConfiguration('package_name')
    enable_raffles_bridge = LaunchConfiguration('enable_raffles_bridge')
    enable_jurong_bridge = LaunchConfiguration('enable_jurong_bridge')
    enable_changi_bridge = LaunchConfiguration('enable_changi_bridge')

    # Raffles Bridge: Domain 0 <-> Domain 2
    raffles_bridge = Node(
        package='domain_bridge',
        executable='domain_bridge',
        name='raffles_domain_bridge',
        arguments=[
            PathJoinSubstitution([
                FindPackageShare(package_name),
                'config',
                'raffles.yaml'
            ])
        ],
        condition=IfCondition(enable_raffles_bridge)
    )

    # Jurong Bridge: Domain 0 <-> Domain 1
    jurong_bridge = Node(
        package='domain_bridge',
        executable='domain_bridge',
        name='jurong_domain_bridge',
        arguments=[
            PathJoinSubstitution([
                FindPackageShare(package_name),
                'config',
                'jurong.yaml'
            ])
        ],
        condition=IfCondition(enable_jurong_bridge)
    )

    # Changi Bridge: Domain 0 <-> Domain 3
    changi_bridge = Node(
        package='domain_bridge',
        executable='domain_bridge',
        name='changi_domain_bridge',
        arguments=[
            PathJoinSubstitution([
                FindPackageShare(package_name),
                'config',
                'changi.yaml'
            ])
        ],
        condition=IfCondition(enable_changi_bridge)
    )

    # Group all bridges for better organization
    bridge_group = GroupAction([
        raffles_bridge,
        jurong_bridge,
        changi_bridge,
    ])

    return LaunchDescription([
        # Launch arguments
        package_name_arg,
        enable_raffles_bridge_arg,
        enable_jurong_bridge_arg,
        enable_changi_bridge_arg,
        
        # All bridges
        bridge_group,
    ])
