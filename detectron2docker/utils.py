import numpy as np
import os
import json

from scipy.signal import medfilt

from poses import PoseSequence


def split_num(s):
    head = s.rstrip("0123456789")
    tail = s[len(head) :]
    return head, tail


def files_in_order(folderpath):
    """
    Args:
        Folder with compressed npy save files of good and bad exercises

    Returns:
        npy_files (numpy.array): ordered array of good then bad exercises
    """
    npy_files = os.listdir(folderpath)
    no_extensions = [os.path.splitext(npy_file)[0] for npy_file in npy_files]
    splitted = [split_num(s) for s in no_extensions]
    splitted = np.array(splitted)
    indices = np.lexsort((splitted[:, 1].astype(int), splitted[:, 0]))
    npy_files = np.array(npy_files)
    return npy_files[indices]


def get_labels(array):
    """
    Args:
        array (numpy.array): Turns filenames into appropriate lables

    Returns:
        np.array(): numpy array of 1's and 0's
    """
    labels = [1 if "good" in i else 0 for i in array]
    return np.array(labels)


def load_tester(path):
    with open(path) as f:
        data = json.load(f)
    return np.asarray(data)


def load_ps(filename):
    """Load a PoseSequence object from a given numpy file.

    Args:
        filename: file name of the numpy file containing keypoints.

    Returns:
        PoseSequence object with normalized joint keypoints.
    """
    all_keypoints = np.load(filename)  # has all the keypoints
    return PoseSequence(all_keypoints)


def DTWDistance(s1, s2):
    """
    Dynamic Time Warping Distance, code from http://alexminnaar.com/,
    the Time Series clustering with python post. Does a recursive function to
    find the shortest path through matrix of distances between each element in
    s1 and s2 (so s1.len by s2.len shaped matrix).

    Args:
        s1 (np.array): first time series
        s2 (np.array): second time series

    Returns:
        (float): distance between
    """
    DTW = {}

    for i in range(len(s1)):
        DTW[(i, -1)] = float("inf")
    for i in range(len(s2)):
        DTW[(-1, i)] = float("inf")
    DTW[(-1, -1)] = 0

    for i in range(len(s1)):
        for j in range(len(s2)):
            dist = (s1[i] - s2[j]) ** 2
            DTW[(i, j)] = dist + min(DTW[(i - 1, j)], DTW[(i, j - 1)], DTW[(i - 1, j - 1)])

    return np.sqrt(DTW[len(s1) - 1, len(s2) - 1])


def load_features(names, data=None, side=None, bool_val=False, exercise="shoulderpress"):
    """

    Geometric interpretations
    Side --> encoded as left or right from user uploaded videos (without confidence encoded)

    Args:
        names (list): list of either filenames gotten from files_in_order (set bool_val to False)
        data (np.array): numpy array of keypoints
        side (str): 'left' or 'right, for which side is seen in the video
        bool_val (Boolean): T/F for whether data and side are used (should refactor this out)
        exercise (str): 'bicep', 'shoulderpress', or 'frontraise' accepted - what body angles to output

    Returns:
        output1 (list): list of key skeletal angle, e.g. upper arm torso angle for bicep curls
        output2 (list): list of second key skeletal angle
    """
    output1 = []  # List of upper arm torso angles
    output2 = []  # List of forearm upper arm angles

    for filename in names:
        if not bool_val:
            ps = load_ps("poses_compressed/shoulderpress/" + filename)
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
            right_present = [
                1
                for pose in poses
                if pose.right_shoulder.exists and pose.right_elbow.exists and pose.right_wrist.exists
            ]  # check if right poses exist
            left_present = [
                1 for pose in poses if pose.left_shoulder.exists and pose.left_elbow.exists and pose.left_wrist.exists
            ]  # check if left poses exist
            right_count = sum(right_present)
            left_count = sum(left_present)
            side = "right" if right_count > left_count else "left"

        if side == "right":
            joints = [
                (pose.right_shoulder, pose.right_elbow, pose.right_wrist, pose.right_hip, pose.neck) for pose in poses
            ]
        else:
            joints = [
                (pose.left_shoulder, pose.left_elbow, pose.left_wrist, pose.left_hip, pose.neck) for pose in poses
            ]

        # filter datapoints missing a part
        joints = [joint for joint in joints if all(part.exists for part in joint)]
        joints_ = np.array(joints)

        back_vec = np.array([(joint[4].x - joint[3].x, joint[4].y - joint[3].y) for joint in joints])[:, 0]

        elbow, neck = joints_[:, 1], joints_[:, 4]
        elbow_x = np.array([joint.x for joint in elbow])
        neck_x = np.array([joint.x for joint in neck])

        arm_vec = elbow_x - neck_x if side == "right" else neck_x - elbow_x

        # Shoulder to elbow (upper arm)
        upper_arm_vecs = np.array([(joint[0].x - joint[1].x, joint[0].y - joint[1].y) for joint in joints])
        # Elbow to wrist (forearm)
        forearm_vecs = np.array([(joint[2].x - joint[1].x, joint[2].y - joint[1].y) for joint in joints])

        # normalize portion: SAME FOR ALL EXERCISES
        upper_arm_vecs = upper_arm_vecs / np.expand_dims(np.linalg.norm(upper_arm_vecs, axis=1), axis=1)
        forearm_vecs = forearm_vecs / np.expand_dims(np.linalg.norm(forearm_vecs, axis=1), axis=1)

        # get all the angles and median filter them
        """
        A drawback with DTW is that it’s not robust to noise. When
            OpenPose generates noisy keypoints, this would affect the
            performance of DTW. To accommodate for this, we run the
            a keypoint sequence through a size 5 median filter twice before computing the DTW measures
        """

        upper_arm_forearm_angle = np.degrees(
            np.arccos(np.clip(np.sum(np.multiply(upper_arm_vecs, forearm_vecs), axis=1), -1.0, 1.0))
        )
        upper_arm_forearm_angle_filtered = medfilt(
            medfilt(upper_arm_forearm_angle, 5), 5
        )  # size 5 median filter twice

        output1.append(back_vec.tolist())
        output2.append(upper_arm_forearm_angle_filtered.tolist())
    return output1, output2


def kmeans_test(names, X_train_1, X_train_2, y_train, data=None, side=None, bool_val=False):
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
        good_score = np.mean(f1_good) + np.mean(f2_good)
        bad_score = np.mean(f1_bad) + np.mean(f2_bad)

        # if distance is closer to good form exercises
        if good_score < bad_score:
            predictions.append(1)
            analysis.append("Exercise Performed Correctly")
        else:  # distance close to bad form exercises
            predictions.append(0)
            analysis.append("Exercise needs some work")
    return analysis, predictions
