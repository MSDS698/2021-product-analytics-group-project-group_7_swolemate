import numpy as np
import sys

from scipy.signal import medfilt

from poses import PoseSequence
from utils import files_in_order, get_labels, load_tester, load_ps, DTWDistance


def load_features(names, data=None, side=None, bool_val=False):
    """
    Geometric interpretations
    Side --> encoded as left or right from user uploaded videos (without confidence encoded)
    """
    output1 = []  # List of upper arm torso angles
    output2 = []  # List of forearm upper arm angles

    for filename in names:
        if not bool_val:
            ps = load_ps("poses_compressed/frontraise/" + filename)
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
            np.arccos(np.clip(np.sum(np.multiply(upper_arm_vecs, torso_vecs), axis=1), -1.0, 1.0))
        )
        upper_arm_torso_angle_filtered = medfilt(medfilt(upper_arm_torso_angle, 5), 5)  # size 5 median filter twice

        upper_arm_forearm_angle = np.degrees(
            np.arccos(np.clip(np.sum(np.multiply(upper_arm_vecs, forearm_vecs), axis=1), -1.0, 1.0))
        )
        upper_arm_forearm_angle_filtered = medfilt(
            medfilt(upper_arm_forearm_angle, 5), 5
        )  # size 5 median filter twice

        output1.append(upper_arm_torso_angle_filtered.tolist())
        output2.append(upper_arm_forearm_angle_filtered.tolist())
    return output1, output2


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

        percentage = (good_score - bad_score) / bad_score * 100 * -1  # percentage

        if percentage > 0:
            print(f"How good the form is in terms of percentage: {round(percentage, 2)}%")
        else:
            print(f"How bad the form is in terms of percentage: {round(percentage, 2)}%")

        # if distance is closer to good form exercises
        if good_score < bad_score:
            predictions.append(1)
            analysis.append("Exercise Performed Correctly")
        else:  # distance close to bad form exercises
            predictions.append(0)
            analysis.append("Exercise needs some work")

        # If we are plotting, add this print statement below
        # print("-------------------------------------------------------------------------------------------------------------------")
    return analysis, predictions


if __name__ == "__main__":
    json_file_name = sys.argv[1]
    side = sys.argv[2]
    if side != "left" and side != "right":
        print("Invalid side type, can only take on values: left or right")
        exit()
    data = load_tester(json_file_name)

    X_train_names = files_in_order("poses_compressed/frontraise")
    y_train = get_labels(X_train_names)

    new_data = load_tester("tao_frontraise_ex.json")

    X_train_1, X_train_2 = load_features(X_train_names)

    # adding new data
    """inp_seq_1, inp_seq_2 = load_features(['demo'], new_data, side, bool_val=True)
    X_train_1.append(inp_seq_1[0])
    X_train_2.append(inp_seq_2[0])
    y_train = np.append(y_train, 1)"""

    print(Kmeans_test(["demo"], X_train_1, X_train_2, data, side, True))
