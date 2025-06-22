#!/usr/bin/env python3

import sys
import random
import string

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rotors_comm_msgs.msg import PPComTopology
from caric_mission.srv import CreatePPComTopic


class RafflesTalker(Node):
    """Raffles node talker for PPCom communication"""

    def __init__(self):
        super().__init__('raffles_talker')
        
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
            '/ping_message/raffles',
            self.ping_message_callback,
            10
        )
        
        # Create timer for periodic publishing
        self.timer = self.create_timer(1.0, self.timer_callback)
        
        self.get_logger().info("Raffles talker node started!")

    def register_topic(self):
        """Register the ping_message topic with PPCom router"""
        request = CreatePPComTopic.Request()
        request.source = 'raffles'
        request.targets = ['jurong', 'sentosa']
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
        BLUE = '\033[94m'
        RESET = '\033[0m'
        self.get_logger().info(f"{BLUE}*** RECEIVED ***{RESET}: {msg.data}")

    def timer_callback(self):
        """Timer callback for periodic message publishing"""
        # Generate random text
        length = random.randint(0, 20)
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        
        # Create and publish message
        msg = String()
        msg.data = f"test;/raffles;{result_str}"
        
        GREEN = '\033[92m'
        RESET = '\033[0m'
        self.get_logger().info(f"{GREEN}*** SENDING ***{RESET}: {msg.data}")
        self.msg_pub.publish(msg)


def main(args=None):
    """Main function"""
    rclpy.init(args=args)
    
    raffles_talker = RafflesTalker()
    
    try:
        rclpy.spin(raffles_talker)
    except KeyboardInterrupt:
        pass
    finally:
        raffles_talker.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
