#!/usr/bin/env python3
"""
PPCom Sequential Launch File

This launch file starts ppcom_router_new.py first, waits for initialization,
then starts ppcom_call_new.py using ROS2 launch system.
"""

from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.substitutions import FindExecutable
from pathlib import Path

def generate_launch_description():
    """Generate launch description for PPCom sequential services"""
    
    # Get the path to our sequential launcher script
    current_dir = Path(__file__).parent.parent.absolute()
    launcher_script = current_dir / "scripts" / "ppcom_sequential_launcher.py"
    
    # Use the sequential launcher script that handles conditional logic
    ppcom_sequential_launcher = ExecuteProcess(
        cmd=[
            FindExecutable(name='python3'),
            str(launcher_script)
        ],
        name='ppcom_sequential_launcher',
        output='screen',
        shell=False
    )
    
    return LaunchDescription([
        ppcom_sequential_launcher,
    ])