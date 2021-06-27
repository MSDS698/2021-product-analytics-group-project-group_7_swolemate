import numpy as np
import math
import matplotlib.pyplot as plt
import json
import os
import argparse
import sys

from scipy.signal import medfilt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def split_num(s):
    head = s.rstrip('0123456789')
    tail = s[len(head):]
    return head, tail

def files_in_order(folderpath):
    npy_files = os.listdir(folderpath)

    no_extensions = [os.path.splitext(npy_file)[0] for npy_file in npy_files]

    splitted = [split_num(s) for s in no_extensions]

    splitted = np.array(splitted)

    indices = np.lexsort((splitted[:, 1].astype(int), splitted[:, 0]))

    npy_files = np.array(npy_files)
    return npy_files[indices]

# Generates binary labels (good=1, bad=0) given an array-like of filenames
def get_labels(array):
    labels = [1 if "good" in i else 0 for i in array]
    return np.array(labels)

def load_tester(path):
    with open(path) as f:
        data = json.load(f)
    return np.asarray(data)

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
        __truediv__(self, scalar)

    def __truediv__(self, scalar):
        if self.c is not None:
            return Part([self.x / scalar, self.y / scalar, self.c])
        return Part([self.x / scalar, self.y / scalar])  # , self.c])

    @staticmethod
    def dist(part1, part2):
        return np.sqrt(np.square(part1.x - part2.x) + np.square(part1.y - part2.y))

class Pose:
    # ********** Fix this part names array based on order of pose estimation coordinates ***********
    PART_NAMES = ['nose', 'neck', 'right_shoulder', 'right_elbow', 'right_wrist', 'left_shoulder', 'left_elbow',
                  'left_wrist', 'right_hip', 'right_knee', 'right_ankle', 'left_hip', 'left_knee', 'left_ankle',
                  'right_eye', 'left_eye', 'right_ear', 'left_ear']

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
            _ = "{}: {},{}".format(name, getattr(self, name).x, getattr(self, name).y)
            out = out + _ + "\n"
        return out

    def print(self, parts):
        out = ""
        for name in parts:
            if not name in self.PART_NAMES:
                raise NameError(name)
            _ = "{}: {},{}".format(name, getattr(self, name).x, getattr(self, name).y)
            out = out + _ + "\n"
        return out


class PoseSequence:
    """
    Chains pose estimations from each video frame
    """

    def __init__(self, sequence):
        self.poses = []  # sequence of poses where a pose is a coordinate for each part
        for parts in sequence:
            self.poses.append(Pose(parts))

        # normalize poses based on the average torso pixel length, from the article as described below:
        """
        to generalize our application to account for users with different body length measurements, distance 
            from the camera, as well as other relative factors
        we normalize the pose based on
            the torso’s length in pixels. The torso length is calculated
            by the average of the distance from the neck keypoint to the
            right and left hip keypoints. This normalization works extremely well: we observe that the torso length stays very
            constant through all the frames of input videos. Distances
            are thus represented as ratios of torso length: for instance,
            an upper arm length of 0.6 means that the upper arm is 0.6
            the length of the torso.
        """
        torso_lengths = np.array([Part.dist(pose.neck, pose.left_hip) for pose in self.poses if pose.neck.exists and pose.left_hip.exists] +
                                 [Part.dist(pose.neck, pose.right_hip) for pose in self.poses if pose.neck.exists and pose.right_hip.exists])
        mean_torso = np.mean(torso_lengths)

        for pose in self.poses:
            for attr, part in pose:
                setattr(pose, attr, part / mean_torso)  # the certain attribute of the pose should all be normalized

def load_ps(filename):
    """Load a PoseSequence object from a given numpy file.

    Args:
        filename: file name of the numpy file containing keypoints.

    Returns:
        PoseSequence object with normalized joint keypoints.
    """
    all_keypoints = np.load(filename)  # has all the keypoints
    return PoseSequence(all_keypoints)

def load_features(names, data=None, side=None, bool_val=False):
    """
    Geometric interpretations
    Side --> encoded as left or right from user uploaded videos (without confidence encoded)
    """
    output1 = []  # List of upper arm torso angles
    output2 = []  # List of forearm upper arm angles

    for filename in names:
        if not bool_val:
            ps = load_ps('poses_compressed/frontraise/' + filename)
        else:
            ps = PoseSequence(data)
        poses = ps.poses

        """
        For certain exercises, we resolve the ambiguity in camera perspective. For example, the bicep curl exercise is
            recorded from the side of the body, and could be performed
            with either the left or right arm. We identify which arm is
            performing the exercise in the video by measuring which
            keypoints are most visible (left or right side keypoints)
            throughout all frames of the exercise. This accurately detects perspective all of our input videos
        """
        if not bool_val:
            right_present = [1 for pose in poses
                             if
                             pose.right_shoulder.exists and pose.right_elbow.exists and pose.right_wrist.exists]  # check if right poses exist
            left_present = [1 for pose in poses
                            if
                            pose.left_shoulder.exists and pose.left_elbow.exists and pose.left_wrist.exists]  # check if left poses exist
            right_count = sum(right_present)
            left_count = sum(left_present)
            side = 'right' if right_count > left_count else 'left'

        if side == 'right':
            joints = [(pose.right_shoulder, pose.right_elbow, pose.right_wrist, pose.right_hip, pose.neck) for pose in
                      poses]
        else:
            joints = [(pose.left_shoulder, pose.left_elbow, pose.left_wrist, pose.left_hip, pose.neck) for pose in
                      poses]

        # filter out data points where a part does not exist
        joints = [joint for joint in joints if all(part.exists for part in joint)]

        # Shoulder to elbow (upper arm)
        upper_arm_vecs = np.array([(joint[0].x - joint[1].x, joint[0].y - joint[1].y) for joint in joints])
        # Neck to hip (torso)
        torso_vecs = np.array([(joint[4].x - joint[3].x, joint[4].y - joint[3].y) for joint in joints])
        # Elbow to wrist (forearm)
        forearm_vecs = np.array([(joint[2].x - joint[1].x, joint[2].y - joint[1].y) for joint in joints])

        # normalize portion: SAME FOR ALL EXERCISES
        upper_arm_vecs = upper_arm_vecs / np.expand_dims(np.linalg.norm(upper_arm_vecs, axis=1), axis=1)
        torso_vecs = torso_vecs / np.expand_dims(np.linalg.norm(torso_vecs, axis=1), axis=1)
        forearm_vecs = forearm_vecs / np.expand_dims(np.linalg.norm(forearm_vecs, axis=1), axis=1)

        # get all the angles and median filter them
        """
        A drawback with DTW is that it’s not robust to noise. When
            OpenPose generates noisy keypoints, this would affect the
            performance of DTW. To accommodate for this, we run the
            a keypoint sequence through a size 5 median filter twice before computing the DTW measures
        """
        upper_arm_torso_angle = np.degrees(
            np.arccos(np.clip(np.sum(np.multiply(upper_arm_vecs, torso_vecs), axis=1), -1.0, 1.0)))
        upper_arm_torso_angle_filtered = medfilt(medfilt(upper_arm_torso_angle, 5), 5)  # size 5 median filter twice

        upper_arm_forearm_angle = np.degrees(
            np.arccos(np.clip(np.sum(np.multiply(upper_arm_vecs, forearm_vecs), axis=1), -1.0, 1.0)))
        upper_arm_forearm_angle_filtered = medfilt(medfilt(upper_arm_forearm_angle, 5), 5)  # size 5 median filter twice

        output1.append(upper_arm_torso_angle_filtered.tolist())
        output2.append(upper_arm_forearm_angle_filtered.tolist())
    return output1, output2


# Compute Dynamic Time Warp Distance of two sequences
# http://alexminnaar.com/time-series-classification-and-clustering-with-python.html
def DTWDistance(s1, s2):
    DTW = {}

    for i in range(len(s1)):
        DTW[(i, -1)] = float('inf')
    for i in range(len(s2)):
        DTW[(-1, i)] = float('inf')
    DTW[(-1, -1)] = 0

    for i in range(len(s1)):
        for j in range(len(s2)):
            dist = (s1[i] - s2[j]) ** 2
            DTW[(i, j)] = dist + min(DTW[(i - 1, j)], DTW[(i, j - 1)], DTW[(i - 1, j - 1)])

    return np.sqrt(DTW[len(s1) - 1, len(s2) - 1])


def Kmeans_test(names, X_train_1, X_train_2, data=None, side=None, bool_val=False, n_neighbors=3): 
    if not bool_val:
        X_test_1, X_test_2 = load_features(names)
    else: 
        X_test_1, X_test_2 = load_features(names, data, side, bool_val=bool_val)
    predictions = []
    analysis = []
    for example in range(len(names)):
        # Store the average distance to good and bad training examples
        f1_good, f1_bad, f2_good, f2_bad = [[] for i in range(4)]

        # Compare distance of current test example with all training examples
        for i in range(len(X_train_1)):
            dist1 = DTWDistance(X_train_1[i], X_test_1[example])
            dist2 = DTWDistance(X_train_2[i], X_test_2[example])
            if y_train[i]:
                f1_good.append(dist1)
                f2_good.append(dist2)
            else:
                f1_bad.append(dist1)
                f2_bad.append(dist2)
                
        f1_good = np.array(f1_good)
        f2_bad = np.array(f2_bad)
        f2_good = np.array(f2_good)
        f1_bad = np.array(f1_bad)
                
        # sort good indices in first dimension
        good_idx_sort = np.argsort(f1_good)
        bad_idx_sort = np.argsort(f1_bad)
        
        f1_good = f1_good[good_idx_sort]
        f2_good = f2_good[good_idx_sort]
        f1_bad = f1_bad[bad_idx_sort]
        f2_bad = f2_bad[bad_idx_sort]
        
        # Plotting points, DO WE NEED?
        """plt.scatter(f1_good, f2_good, label='Distance to Good Form Ex.')
        plt.scatter(f1_bad, f2_bad, label='Distance to Bad Form Ex.')
        plt.xlabel("Distance using Upper Arm Torso Angle (in Degrees)")
        plt.ylabel("Distance using Upper Arm Forearm Angle (in Degrees)")
        plt.title(f"Distance between {names[example]} and Good/Bad Examples")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
        plt.show()"""
        
        good_score = np.mean(f1_good[:n_neighbors]) + np.mean(f2_good[:n_neighbors])
        bad_score = np.mean(f1_bad[:n_neighbors]) + np.mean(f2_bad[:n_neighbors])
        
        percentage = (good_score - bad_score) / bad_score * 100 * -1 # percentage
        
        if percentage > 0: 
            print(f"How good the form is in terms of percentage: {round(percentage, 2)}%")
        else: 
            print(f"How bad the form is in terms of percentage: {round(percentage, 2)}%")

        # if distance is closer to good form exercises
        if good_score < bad_score:
            predictions.append(1)
            analysis.append("Exercise Performed Correctly")
        else: # distance close to bad form exercises
            predictions.append(0)
            analysis.append("Exercise needs some work")
            
        # If we are plotting, add this print statement below
        # print("-------------------------------------------------------------------------------------------------------------------")
    return analysis, predictions


if __name__ == "__main__":
    json_file_name = sys.argv[1]
    side = sys.argv[2]
    if side != 'left' and side != 'right': 
        print("Invalid side type, can only take on values: left or right")
        exit()
    data = load_tester(json_file_name)
    
    X_train_names = files_in_order('poses_compressed/frontraise')
    y_train = get_labels(X_train_names)
    
    new_data = load_tester('tao_frontraise_ex.json')
    
    X_train_1, X_train_2 = load_features(X_train_names)
    
    # adding new data
    """inp_seq_1, inp_seq_2 = load_features(['demo'], new_data, side, bool_val=True)
    X_train_1.append(inp_seq_1[0])
    X_train_2.append(inp_seq_2[0])
    y_train = np.append(y_train, 1)"""
    
    print(Kmeans_test(['demo'], X_train_1, X_train_2, data, side, True))
