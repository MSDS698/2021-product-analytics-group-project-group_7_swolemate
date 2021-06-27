import numpy as np
import sys

from scipy.signal import medfilt
from sklearn.model_selection import train_test_split

from utils import files_in_order, get_labels, load_tester, load_features, kmeans_test


if __name__ == "__main__":
    json_file_name = sys.argv[1]
    side = sys.argv[2] if len(sys.argv) >= 3 else "left"  # focuses on only one arm
    data = load_tester(json_file_name)

    files = files_in_order("poses_compressed/shoulderpress")
    X_train_names, X_test_names = train_test_split(files, test_size=0.4, random_state=42)
    y_train = get_labels(X_train_names)

    new_data = load_tester("elyse_shoulderpress_ex.json")

    X_train_1, X_train_2 = load_features(X_train_names)
    X_test_1, X_test_2 = load_features(X_test_names)

    # adding new data
    inp_seq_1, inp_seq_2 = load_features(["demo"], new_data, "left", bool_val=True)
    X_train_1.append(inp_seq_1[0])
    X_train_2.append(inp_seq_2[0])
    y_train = np.append(y_train, 1)

    print(kmeans_test(["demo"], X_train_1, X_train_2, y_train, data, side, True))
