import cv2
import numpy as np
from airhockey.vision.color import ColorRange
from airhockey.geometry import PointF


class DebugWindow(object):
    def __init__(self, *, name, translator, table_size, color_ranges: list['ColorRange']):
        self.name = name
        self.translator = translator
        self.table_size = table_size
        self.color_ranges = color_ranges
        cv2.namedWindow(self.name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.name, 600, 600)
        self.frame = None
        self.hsv = None

        for r in color_ranges:
            cv2.createTrackbar('{name} H Low'.format(name=r.name), self.name, 0, 179, lambda x: r.set_h_low(x))
            cv2.setTrackbarPos('{name} H Low'.format(name=r.name), self.name, r.h_low)
            cv2.createTrackbar('{name} H High'.format(name=r.name), self.name, 0, 179, lambda x: r.set_h_high(x))
            cv2.setTrackbarPos('{name} H High'.format(name=r.name), self.name, r.h_high)
            cv2.createTrackbar('{name} SV Low'.format(name=r.name), self.name, 0, 255, lambda x: r.set_sv_low(x))
            cv2.setTrackbarPos('{name} SV Low'.format(name=r.name), self.name, r.sv_low)

    def set_frame(self, frame, hsv):
        self.frame = frame
        self.hsv = hsv

    def draw(self, queries: list):
        for query in queries:
            query.draw(self)
        cv2.rectangle(self.frame, self.translator.w2f(PointF(0, 0)).tuple(), self.translator.w2f(PointF(self.table_size)).tuple(), (0, 255, 255), 2)
        cv2.imshow(self.name, self.frame)

        # for r in self.color_ranges:
        #     lower_color = np.array([r.h_low, r.sv_low, r.sv_low])
        #     upper_color = np.array([r.h_high, 255, 255])
        #     mask = cv2.inRange(self.hsv, lower_color, upper_color)
        #     cv2.imshow(r.name, mask)

        cv2.waitKey(1)

    def draw_circle(self, world_coordinates, color):
        hsv_color = np.uint8([[color]])
        bgr_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2BGR)[0][0]
        bgr_color = (int(bgr_color[0]), int(bgr_color[1]), int(bgr_color[2]))
        bgr_color = (0, 0, 255)
        c = self.translator.w2f(world_coordinates)
        cv2.circle(self.frame, (c.x, c.y), 10, bgr_color, -1)


class Debug(object):
    def __init__(self, translator, robot):
        self.translator = translator
        self.robot = robot

    def draw(self, *, frame, world_debug, robot_position, robot_dst, fps, video_stream):
        # table
        cv2.rectangle(frame, self.translator.w2f((0, 0)), self.translator.w2f(world_debug['table_size']), (0, 255, 255), 2)

        # trajectory
        for intersection in world_debug['trajectory']:
            point, velocity = intersection
            cv2.circle(frame, self.translator.w2f(point), 10, (0, 0, 255), -1)
            # cv2.putText(frame, str(velocity), translator.w2f(point), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 127, 255), thickness=3)

        # puck center
        if world_debug['puck_info'] is not None:
            cv2.circle(
                frame,
                self.translator.w2f(world_debug['puck_info'].position),
                10, (255, 0, 0), -1)

            # puck vector
            cX, cY = self.translator.w2f(world_debug['puck_info'].position)
            vX, vY = world_debug['puck_info'].vector
            velocity = world_debug['puck_info'].velocity
            line_len = 200
#             if velocity > 10:
#                 line_len = velocity * 2
            cv2.line(frame, (cX, cY), (int(cX + vX * line_len), int(cY + vY * line_len)), (0, 255, 0), 7)

        # robot position
        if robot_position is not None:
            cv2.circle(frame, self.translator.w2f(robot_position), 10, (255, 0, 255), -1)
            if self.robot.destination is not None:
                (rX, rY) = robot_position
                (rdX, rdY) = robot_dst
                cv2.line(frame, self.translator.w2f(robot_position), self.translator.w2f((int(rdX), int(rdY))), (0, 255, 0), 7)

        cv2.putText(frame, str("FPS: {0:.2f}".format(fps)), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness=3)
        cv2.putText(frame, str("Stream: {0}/{1:.2f} fps".format(video_stream.frames_grabbed, video_stream.stream_fps())), (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness=3)
        cv2.putText(frame, str("Processed: {0}/{1:.2f} fps".format(video_stream.frames_read, video_stream.read_fps())), (10, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness=3)
        # debug
        #cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('frame', 600, 600)
        cv2.imshow('frame', frame)
