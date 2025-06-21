#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import time
import threading
from std_msgs.msg import String
from caric_mission.srv import CreatePPComTopic

# =============================================================================
# Simplified Configuration
# =============================================================================

# All nodes to be started (fixed configuration)
ALL_NODES = ["gcs", "jurong", "raffles", "changi", "sentosa", "nanyang"]

# Startup delay (seconds)
STARTUP_DELAY = 1.0

# PPCom service configuration
SERVICE_NAME = '/create_ppcom_topic'
SUCCESS_RESPONSE = "success"

# =============================================================================
# Basic Service Client
# =============================================================================

class SimpleServiceClient(Node):
    """Simplified PPCom service client base class"""
    
    def __init__(self, node_name: str):
        super().__init__(node_name + '_client')
        self.node_name = node_name
        self.client = None
        
    def setup_ppcom_service(self, source_name: str, targets: list, topic_name: str):
        """Setup PPCom service"""
        # Create service client
        self.client = self.create_client(CreatePPComTopic, SERVICE_NAME)
        
        # Wait for service to be available
        if not self.client.wait_for_service(timeout_sec=10.0):
            self.get_logger().error(f"PPCom service not available for {source_name}")
            return False
        
        # Prepare request
        request = CreatePPComTopic.Request()
        request.source = source_name
        request.targets = targets
        request.topic_name = topic_name
        request.package_name = "std_msgs"
        request.message_type = "String"
        
        # Call service
        try:
            future = self.client.call_async(request)
            rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
            
            if future.result() and future.result().result == SUCCESS_RESPONSE:
                self.get_logger().info(f"{source_name} PPCom service setup successful")
                return True
            else:
                self.get_logger().error(f"{source_name} PPCom service setup failed")
                return False
                
        except Exception as e:
            self.get_logger().error(f"{source_name} service call exception: {e}")
            return False


class SimpleGCSClient(SimpleServiceClient):
    """Simplified GCS client"""
    
    def __init__(self):
        super().__init__("gcs")
        self.cmd_pub = self.create_publisher(String, "/task_assign", 10)
        
    def initialize(self):
        """Initialize GCS communication"""
        success = self.setup_ppcom_service(
            source_name="gcs",
            targets=["all"],
            topic_name="/task_assign"
        )
        
        if success:
            # Start task publish timer
            self.create_timer(5.0, self.publish_task)
            
        return success
    
    def publish_task(self):
        """Publish task message"""
        task_msg = String()
        task_msg.data = f"task_assignment_from_gcs_at_{time.time()}"
        self.cmd_pub.publish(task_msg)
        self.get_logger().info("Published task assignment")


class SimpleAgentClient(SimpleServiceClient):
    """Simplified Agent client"""
    
    def __init__(self, agent_name: str):
        super().__init__(agent_name)
        self.agent_name = agent_name
        self.namespace = f"/{agent_name}"
        
    def initialize(self):
        """Initialize Agent communication"""
        return self.setup_ppcom_service(
            source_name=self.agent_name,
            targets=["all"],
            topic_name="/broadcast"
        )


# =============================================================================
# Simplified Multithread Manager
# =============================================================================

def run_client_thread(node_name: str):
    """Run a single client in a thread"""
    try:
        # Create corresponding client (ROS2 already initialized)
        if node_name == "gcs":
            client = SimpleGCSClient()
        else:
            client = SimpleAgentClient(node_name)
        
        # Initialize client
        if client.initialize():
            print(f"{node_name} started successfully")
            # Run client
            rclpy.spin(client)
        else:
            print(f"{node_name} failed to start")
            
    except KeyboardInterrupt:
        print(f"{node_name} shutting down...")
    except Exception as e:
        print(f"Error in {node_name}: {e}")
    finally:
        try:
            if 'client' in locals():
                client.destroy_node()
        except:
            pass


def start_all_clients():
    """Start all 6 clients"""
    print("=== Starting all PPCom service clients ===")
    print(f"Node list: {ALL_NODES}")
    print(f"Startup delay: {STARTUP_DELAY} seconds")
    print("")
    
    # Initialize ROS2 once in main thread
    rclpy.init()
    
    threads = []
    
    # Start each node in order
    for i, node_name in enumerate(ALL_NODES):
        print(f"[{i+1}/6] Starting {node_name}...")
        
        # Create and start thread
        thread = threading.Thread(
            target=run_client_thread,
            args=(node_name,),
            name=f"ppcom_{node_name}",
            daemon=True
        )
        thread.start()
        threads.append(thread)
        
        # Add delay (no delay for last one)
        if i < len(ALL_NODES) - 1:
            time.sleep(STARTUP_DELAY)
    
    print(f"\nAll {len(ALL_NODES)} clients started!")
    print("Press Ctrl+C to stop all clients...")
    
    try:
        # Wait for all threads
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n=== Shutting down all clients ===")
    finally:
        # Shutdown ROS2
        rclpy.shutdown()
    
    print("All clients stopped")


# =============================================================================
# Main function
# =============================================================================

def main():
    """Main function - directly start all 6 clients"""
    try:
        start_all_clients()
    except Exception as e:
        print(f"Startup failed: {e}")


if __name__ == '__main__':
    main()