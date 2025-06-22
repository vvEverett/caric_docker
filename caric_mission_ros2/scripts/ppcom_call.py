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
            
            if future.done() and future.result() and future.result().result == SUCCESS_RESPONSE:
                self.get_logger().info(f"PPCom service setup successful for {source_name}")
                return True
            else:
                # ### MODIFIED ### - Added more detail to error log
                response_result = future.result().result if future.done() and future.result() else "No response/timeout"
                self.get_logger().error(f"PPCom service setup failed for {source_name}. Response: '{response_result}'")
                return False
                
        except Exception as e:
            self.get_logger().error(f"{source_name} service call exception: {e}")
            return False


class SimpleGCSClient(SimpleServiceClient):
    """Simplified GCS client"""
    
    def __init__(self):
        super().__init__("gcs")
        # ### MODIFIED ### - Removed publisher, it's not needed for a one-off task
        
    def initialize(self):
        """Initialize GCS communication"""
        success = self.setup_ppcom_service(
            source_name="gcs",
            targets=["all"],
            topic_name="/task_assign"
        )
        
        # ### MODIFIED ### - Removed timer and task publishing logic
        return success
    
    # ### MODIFIED ### - Removed publish_task method


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
    """Run a single client in a thread to call the service"""
    client = None # Define client here to ensure it's available in finally block
    try:
        # Create corresponding client
        if node_name == "gcs":
            client = SimpleGCSClient()
        else:
            client = SimpleAgentClient(node_name)
        
        # Initialize client (this calls the service)
        if client.initialize():
            print(f"Service call for node '{node_name}' SUCCEEDED.")
        else:
            print(f"Service call for node '{node_name}' FAILED.")

        # ### MODIFIED ###
        # We DO NOT call rclpy.spin() here because we want the thread to exit
        # after the service call is complete.
            
    except Exception as e:
        print(f"An error occurred in thread for {node_name}: {e}")
    finally:
        # Clean up the node after the task is done
        if client:
            client.destroy_node()


def start_all_clients():
    """Start all clients to perform their task and then exit"""
    print("=== Starting all PPCom service clients for a one-off task ===")
    print(f"Node list: {ALL_NODES}")
    print(f"Startup delay: {STARTUP_DELAY} seconds")
    print("")
    
    # Initialize ROS2 once in main thread
    rclpy.init()
    
    threads = []
    
    # Start each node in order
    for i, node_name in enumerate(ALL_NODES):
        print(f"[{i+1}/{len(ALL_NODES)}] Dispatching task for {node_name}...")
        
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
    
    print("\nAll client tasks dispatched. Waiting for completion...")
    
    try:
        # Wait for all threads to complete their service call
        for thread in threads:
            thread.join() # This will now work because threads will terminate
    except KeyboardInterrupt:
        print("\n=== Interrupted by user. Shutting down. ===")
    finally:
        # Shutdown ROS2
        rclpy.shutdown()
    
    print("\nAll client tasks are complete. Program exiting.")


# =============================================================================
# Main function
# =============================================================================

def main():
    """Main function"""
    try:
        start_all_clients()
    except Exception as e:
        print(f"A critical error occurred during startup: {e}")


if __name__ == '__main__':
    main()