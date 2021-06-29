import numpy as np
import os
import json
import sys

import matplotlib.pyplot as plt
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
    """
    Load the json file
    Arguments: 
        path(str): path to the json file
    """
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

def load_features(names, exercise='Bicep Curl', data=None, side=None, bool_val=False):
    """
    Given
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
    output1 = [] # List of upper arm torso angles
    output2 = [] # List of forearm upper arm angles

    for filename in names:
        if not bool_val: 
            ps = load_ps('poses_compressed/bicep/'+filename)
        else: 
            ps = PoseSequence(data)
        poses = ps.poses
        
        if not bool_val: 
            right_present = [1 for pose in poses 
                    if pose.right_shoulder.exists and pose.right_elbow.exists and pose.right_wrist.exists] # check if right poses exist
            left_present = [1 for pose in poses
                    if pose.left_shoulder.exists and pose.left_elbow.exists and pose.left_wrist.exists] # check if left poses exist
            right_count = sum(right_present)
            left_count = sum(left_present)
            side = 'right' if right_count > left_count else 'left'
        
        if side == 'right':
            joints = [(pose.right_shoulder, pose.right_elbow, pose.right_wrist, pose.right_hip, pose.neck) for pose in poses]
        else:
            joints = [(pose.left_shoulder, pose.left_elbow, pose.left_wrist, pose.left_hip, pose.neck) for pose in poses]

        # filter out data points where a part does not exist
        joints = [joint for joint in joints if all(part.exists for part in joint)]
        
        # for shoulderpress
        back_vec = np.array([(joint[4].x - joint[3].x, joint[4].y - joint[3].y) for joint in joints])[:, 0]
        
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

        if exercise == "Shoulder Press":
            output1.append(back_vec.tolist())
            output2.append(upper_arm_forearm_angle_filtered.tolist())

        if (exercise == "Bicep Curl") or (exercise == "Front Raise"):
            output1.append(upper_arm_torso_angle_filtered.tolist())
            output2.append(upper_arm_forearm_angle_filtered.tolist())
    return output1, output2

def kmeans_test(names, X_train_names, X_train_1, X_train_2, y_train, data=None, side=None, bool_val=False, exercise="Bicep Curl"):
    """
    Evaluating the given inputted exercise based on training data
    Arguments: 
        names(str): name of the file
        X_train_names(list): list of training file names
        X_train_1(list): list of values representing the first feature of the video exercise
        X_train_2(list): list of values representing the second feature of the video exercise
        y_train(list): Labels of the training samples as either good or bad form
        data(list): if loaded from external json file, data of json file is supplied here
        side(str): if loaded from external json file, must specify side as either left or right facing in the point of view 
            of the camera
        bool_val(boolean): whether loading from external json file (True), or taking from poses_compressed folder (False)
        exercise(str): what exercise is specified from dropdown in web page
    Returns: 
        percentage(float): 
        analysis(list): 
        predictions(list):  
        range_ang_1(float):  
        range_ang_2(float): 
        range_user_ang_1(float): 
        range_user_ang_2(float): 
        label(boolean): 
    """
    if not bool_val:
        X_test_1, X_test_2 = load_features(names, exercise=exercise)
    else:
        X_test_1, X_test_2 = load_features(names, exercise=exercise, data=data, side=side, bool_val=bool_val)
    predictions = []
    analysis = []
    if exercise == 'Bicep Curl': 
        label = 'Angles between Upper Arm and Torso'
    elif exercise == 'Shoulder Press': 
        label = 'Movement of Back'
    idx = np.nonzero(np.array(['good' in elem for elem in X_train_names], dtype=int))[0]
    X_train_names_arr = np.array(X_train_names)
    X_train_1_arr = np.array(X_train_1, dtype=object)
    X_train_2_arr = np.array(X_train_2, dtype=object)
    range_ang_1, range_ang_2 = plot_angles(X_train_names_arr[idx][0], X_train_1_arr[idx][0], X_train_2_arr[idx][0], label, exercise)
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
        
        # Plotting points
        plt.scatter(f1_good, f2_good, label='Distance to Good Form Ex.')
        plt.scatter(f1_bad, f2_bad, label='Distance to Bad Form Ex.')
        plt.xlabel("Distance using Upper Arm Torso Angle (in Degrees)")
        plt.ylabel("Distance using Upper Arm Forearm Angle (in Degrees)")
        plt.title(f"Distance between {names[example]} and Good/Bad Examples")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
        plt.savefig('app/static/assets/image.jpg', bbox_inches="tight")
        plt.close()

        good_score = np.mean(f1_good) + np.mean(f2_good)
        bad_score = np.mean(f1_bad) + np.mean(f2_bad)

        percentage = (good_score - bad_score) / bad_score * 100 * -1  # percentage
        percentage = round(percentage, 2)
        
        range_user_ang_1, range_user_ang_2 = plot_angles(['Demo'], X_test_1[0], X_test_2[0], exercise, label, str_val='Inputted_Form')
        
        # if distance is closer to good form exercises
        if good_score < bad_score:
            predictions.append(1)
            analysis.append("Exercise Performed Correctly")
        else:  # distance close to bad form exercises
            predictions.append(0)
            analysis.append("Exercise needs some work")
    return percentage, analysis, predictions, range_ang_1, range_ang_2, range_user_ang_1, range_user_ang_2, label

def plot_angles(name, angle_1, angle_2, exercise, label, str_val='Good_Form'):  
    # Generate plots
    # plt.scatter(np.arange(upper_arm_torso_angle.shape[0]),upper_arm_torso_angle, alpha=0.5)
    angle_1 = np.array(angle_1)
    range_ang_1 = np.max(angle_1)-np.min(angle_1)
    plt.scatter(np.arange(angle_1.shape[0]),angle_1, c='r', alpha=0.5)
    plt.title(f"{label} for {name}")
    plt.xlabel('Frames')
    plt.ylabel(label)
    # Set range on y-axis so the plots are consistent
    plt.ylim(0,90) 
    plt.savefig('app/static/assets/' + str_val + '1.jpg', bbox_inches="tight")
    plt.close()

    upper_forearm_angle_filtered = np.array(angle_2)
    range_ang_2 = np.min(upper_forearm_angle_filtered)
    plt.scatter(np.arange(upper_forearm_angle_filtered.shape[0]),upper_forearm_angle_filtered, c='b', alpha=0.5)
    plt.title(f"Angle between Upper Arm and Forearm for {name}")
    plt.xlabel('Frames')
    plt.ylabel('Angle between Upper Arm and Forearm')
    # Set range on y-axis so the plots are consistent
    plt.ylim(0,180) 
    plt.savefig('app/static/assets/' + str_val + '2.jpg', bbox_inches="tight")
    plt.close()
    return round(range_ang_1, 2), round(range_ang_2, 2)

if __name__ == "__main__":
    json_file_name = sys.argv[1]
    side = sys.argv[2]
    exercise = sys.argv[3]
    if side != 'left' and side != 'right': 
        print("Invalid side type, can only take on values: left or right")
        exit()
    data = load_tester(json_file_name)
    
    X_train_names = files_in_order('poses_compressed/bicep')
    y_train = get_labels(X_train_names)
    
    #new_data = load_tester('moh_bicep_curl_ex.json')
    
    X_train_1, X_train_2 = load_features(X_train_names)

    print(kmeans_test(['demo'], X_train_1=X_train_1, X_train_2=X_train_2, y_train=y_train, data=data, side=side, bool_val=True, exercise=exercise))