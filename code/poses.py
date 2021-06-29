import numpy as np


class Part:
    def __init__(self, vals):
        self.x = vals[0]
        self.y = vals[1]
        if len(vals) > 2:
            self.c = vals[2]
            self.exists = self.c != 0.0
        else:
            self.c = None
            self.exists = True

    def __floordiv__(self, scalar):
        '''Overwrites integer division operator "//"'''
        __truediv__(self, scalar)

    def __truediv__(self, scalar):
        """overwrite the division "/" operator"""
        if self.c is not None:
            return Part([self.x / scalar, self.y / scalar, self.c])
        return Part([self.x / scalar, self.y / scalar])  # , self.c])

    @staticmethod
    def dist(part1, part2):
        return np.sqrt(np.square(part1.x - part2.x) +
                       np.square(part1.y - part2.y))


class Pose:

    # **********
    # Fix this part names array based on order of pose estimation coordinates
    # ***********
    PART_NAMES = [
        "nose",
        "neck",
        "right_shoulder",
        "right_elbow",
        "right_wrist",
        "left_shoulder",
        "left_elbow",
        "left_wrist",
        "right_hip",
        "right_knee",
        "right_ankle",
        "left_hip",
        "left_knee",
        "left_ankle",
        "right_eye",
        "left_eye",
        "right_ear",
        "left_ear",
    ]

    def __init__(self, parts):
        """Construct a pose for one frame, given an array of parts

        Arguments:
            parts - 18 * 3 ndarray of x, y, confidence values
        """
        if type(parts) == dict:
            for name in self.PART_NAMES:
                setattr(self, name, Part(parts[name]))
        else:
            for name, vals in zip(self.PART_NAMES, parts):
                setattr(self, name, Part(vals))

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def __str__(self):
        out = ""
        for name in self.PART_NAMES:
            _ = "{}: {},{}".format(name, getattr(self, name).x,
                                   getattr(self, name).y)
            out = out + _ + "\n"
        return out

    def print(self, parts):
        out = ""
        for name in parts:
            if name not in self.PART_NAMES:
                raise NameError(name)
            _ = "{}: {},{}".format(name, getattr(self, name).x,
                                   getattr(self, name).y)
            out = out + _ + "\n"
        return out


class PoseSequence:
    """
    Creates a list of Poses from flattened
    """

    def __init__(self, sequence):
        self.poses = []  # seq of poses where pose is coordinate for each part
        for parts in sequence:
            self.poses.append(Pose(parts))

        # normalize poses based on the average torso pixel length,
        # from the article as described below:
        """
        to generalize our application to account for users with different
            body length measurements, distance from the camera,
            as well as other relative factors
        we normalize the pose based on
            the torso’s length in pixels. The torso length is calculated
            by the average of the distance from the neck keypoint to the
            right and left hip keypoints. This normalization works extremely
            well: we observe that the torso length stays very
            constant through all the frames of input videos. Distances
            are thus represented as ratios of torso length: for instance,
            an upper arm length of 0.6 means that the upper arm is 0.6
            the length of the torso.
        """
        torso_lengths = np.array(
            [Part.dist(pose.neck, pose.left_hip) for pose in self.poses
                if pose.neck.exists and pose.left_hip.exists]
            + [
                Part.dist(pose.neck, pose.right_hip)
                for pose in self.poses
                if pose.neck.exists and pose.right_hip.exists
            ]
        )
        mean_torso = np.mean(torso_lengths)

        for pose in self.poses:
            for attr, part in pose:
                # the certain attribute of the pose should all be normalized
                setattr(pose, attr, part / mean_torso)
