#!/usr/bin/env python3
"""
Multi-Domain Bridge Launch File

Launch multiple domain bridges simultaneously for gcs, raffles, jurong, sentosa, changi and nanyang configurations.
Each bridge instance runs independently and bridges different domain pairs.

Usage:
ros2 launch caric_mission_ros2 multi_bridge.launch.py

This will start:
- GCS bridge: Domain 0 <-> Domain 99
- Jurong bridge: Domain 0 <-> Domain 1  
- Raffles bridge: Domain 0 <-> Domain 2
- Sentosa bridge: Domain 0 <-> Domain 3
- Changi bridge: Domain 0 <-> Domain 4
- Nanyang bridge: Domain 0 <-> Domain 5
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
    enable_gcs_bridge_arg = DeclareLaunchArgument(
        'enable_gcs_bridge',
        default_value='true',
        description='Enable gcs bridge (domain 0 <-> domain 99)'
    )
    enable_jurong_bridge_arg = DeclareLaunchArgument(
        'enable_jurong_bridge', 
        default_value='true',
        description='Enable jurong bridge (domain 0 <-> domain 1)'
    )
    enable_raffles_bridge_arg = DeclareLaunchArgument(
        'enable_raffles_bridge',
        default_value='true',
        description='Enable raffles bridge (domain 0 <-> domain 2)'
    )
    enable_sentosa_bridge_arg = DeclareLaunchArgument(
        'enable_sentosa_bridge',
        default_value='true',
        description='Enable sentosa bridge (domain 0 <-> domain 3)'
    )
    enable_changi_bridge_arg = DeclareLaunchArgument(
        'enable_changi_bridge',
        default_value='true',
        description='Enable changi bridge (domain 0 <-> domain 4)'
    )
    enable_nanyang_bridge_arg = DeclareLaunchArgument(
        'enable_nanyang_bridge',
        default_value='true',
        description='Enable nanyang bridge (domain 0 <-> domain 5)'
    )
    
    # Get launch configuration values
    package_name = LaunchConfiguration('package_name')
    enable_gcs_bridge = LaunchConfiguration('enable_gcs_bridge')
    enable_jurong_bridge = LaunchConfiguration('enable_jurong_bridge')
    enable_raffles_bridge = LaunchConfiguration('enable_raffles_bridge')
    enable_changi_bridge = LaunchConfiguration('enable_changi_bridge')
    enable_sentosa_bridge = LaunchConfiguration('enable_sentosa_bridge')
    enable_nanyang_bridge = LaunchConfiguration('enable_nanyang_bridge')


    # gcs Bridge: Domain 0 <-> Domain 99
    gcs_bridge = Node(
        package='domain_bridge',
        executable='domain_bridge',
        name='gcs_domain_bridge',
        arguments=[
            PathJoinSubstitution([
                FindPackageShare(package_name),
                'config',
                'gcs.yaml'
            ])
        ],
        condition=IfCondition(enable_gcs_bridge)
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
    # sentosa Bridge: Domain 0 <-> Domain 3
    sentosa_bridge = Node(
        package='domain_bridge',
        executable='domain_bridge',
        name='sentosa_domain_bridge',
        arguments=[
            PathJoinSubstitution([
                FindPackageShare(package_name),
                'config',
                'sentosa.yaml'
            ])
        ],
        condition=IfCondition(enable_sentosa_bridge)
    )
    # Changi Bridge: Domain 0 <-> Domain 4
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
    # nanyang Bridge: Domain 0 <-> Domain 5
    nanyang_bridge = Node(
        package='domain_bridge',
        executable='domain_bridge',
        name='nanyang_domain_bridge',
        arguments=[
            PathJoinSubstitution([
                FindPackageShare(package_name),
                'config',
                'nanyang.yaml'
            ])
        ],
        condition=IfCondition(enable_nanyang_bridge)
    )
    # Group all bridges for better organization
    bridge_group = GroupAction([
        gcs_bridge,
        raffles_bridge,
        jurong_bridge,
        changi_bridge,
        sentosa_bridge,
        nanyang_bridge
    ])

    return LaunchDescription([
        # Launch arguments
        package_name_arg,
        enable_gcs_bridge_arg,
        enable_raffles_bridge_arg,
        enable_jurong_bridge_arg,
        enable_changi_bridge_arg,
        enable_sentosa_bridge_arg,
        enable_nanyang_bridge_arg,


        # All bridges
        bridge_group,
    ])
