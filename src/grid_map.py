from copy import copy
import rospy as rp
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import OccupancyGrid, Path
from visualization_msgs.msg import Marker


class GridMap(object):
    def __init__(self):
        self.map = None
        self.start = None
        self.end = None
        rp.init_node('graph_search', log_level=rp.DEBUG)
        rp.Subscriber('map', OccupancyGrid, self.map_callback)
        rp.Subscriber('point_start', Marker, self.set_start)
        rp.Subscriber('point_end', Marker, self.set_end)
        self.pub = rp.Publisher('map_visited', OccupancyGrid, queue_size=10)
        self.path_pub = rp.Publisher('path', Path, queue_size=10)
        while self.map is None or self.start is None or self.end is None:
            rp.sleep(0.1)
        print("Object initialized!")

    def map_callback(self, data):
        self.map = copy(data)
        self.map.data = list(self.map.data)

    def get_marker_xy(self, marker):
        mul = 1. / self.map.info.resolution
        x = int(marker.pose.position.y * mul)
        y = int(marker.pose.position.x * mul)
        return x, y

    def set_start(self, data):
        x, y = self.get_marker_xy(data)
        self.start = (x, y)

    def set_end(self, data):
        x, y = self.get_marker_xy(data)
        self.end = (x, y)

    def publish_visited(self):
        self.pub.publish(self.map)
        rp.sleep(0.5)

    def publish_path(self, path):
        path_msg = Path()
        path_msg.header.frame_id = 'map'
        for p in path:
            pose = PoseStamped()
            pose.pose.position.x = self.map.info.resolution * p[1] + 0.05
            pose.pose.position.y = self.map.info.resolution * p[0] + 0.05
            pose.pose.position.z = 0
            pose.pose.orientation.x = 0
            pose.pose.orientation.y = 0
            pose.pose.orientation.z = 0
            pose.pose.orientation.w = 1
            pose.header.frame_id = 'map'
            pose.header.stamp = rp.Time.now()
            path_msg.poses.append(pose)
        self.path_pub.publish(path_msg)

    def search(self):
        return NotImplementedError()
