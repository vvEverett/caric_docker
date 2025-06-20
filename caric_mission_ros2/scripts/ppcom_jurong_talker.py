#!/usr/bin/env python3

import sys
import random
import string

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rotors_comm_msgs.msg import PPComTopology
from caric_mission.srv import CreatePPComTopic


class JurongTalker(Node):
    """Jurong node talker for PPCom communication"""

    def __init__(self):
        super().__init__('jurong_talker')
        
        # Wait for service to be available
        self.create_topic_client = self.create_client(CreatePPComTopic, 'create_ppcom_topic')
        
        self.get_logger().info("Waiting for create_ppcom_topic service...")
        while not self.create_topic_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Service not available, waiting...")
        
        # Register the topic with ppcom router
        self.register_topic()
        
        # Create publisher and subscriber
        self.msg_pub = self.create_publisher(String, '/ping_message', 10)
        self.ping_sub = self.create_subscription(
            String,
            '/ping_message/jurong',
            self.ping_message_callback,
            10
        )
        
        # Create timer for periodic publishing
        self.timer = self.create_timer(1.0, self.timer_callback)
        
        self.get_logger().info("Jurong talker node started!")

    def register_topic(self):
        """Register the ping_message topic with PPCom router"""
        request = CreatePPComTopic.Request()
        request.source = 'jurong'
        request.targets = ['all']
        request.topic_name = '/ping_message'
        request.package_name = 'std_msgs'
        request.message_type = 'String'
        
        future = self.create_topic_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result() is not None:
            self.get_logger().info(f"Registration response: {future.result().result}")
        else:
            self.get_logger().error("Failed to register topic")

    def ping_message_callback(self, msg):
        """Handle received ping messages"""
        self.get_logger().info(f"Received: {msg.data}")

    def timer_callback(self):
        """Timer callback for periodic message publishing"""
        # Generate random text
        length = random.randint(0, 20)
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        
        # Create and publish message
        msg = String()
        msg.data = f"{self.get_name()} says hello at time {self.get_clock().now().to_msg().sec}.{self.get_clock().now().to_msg().nanosec}. Random Text: {result_str}!"
        
        self.get_logger().info(f"SENDING: {msg.data}")
        self.msg_pub.publish(msg)


def main(args=None):
    """Main function"""
    rclpy.init(args=args)
    
    jurong_talker = JurongTalker()
    
    try:
        rclpy.spin(jurong_talker)
    except KeyboardInterrupt:
        pass
    finally:
        jurong_talker.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
