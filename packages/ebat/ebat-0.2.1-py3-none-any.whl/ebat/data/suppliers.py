import json
import os
import random
import shutil
import tarfile
from abc import abstractmethod
from datetime import timedelta, datetime
from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile

import numpy as np
import pgeof
from pandas import to_datetime, get_dummies, read_csv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import Dataset


class EbatDataset(Dataset):
    def __init__(self, X, y):
        self.X = np.nan_to_num(X)
        self.y = np.nan_to_num(y)
        self.classes = list(np.unique(np.argmax(y, axis=1)))

    def __len__(self):
        return len(self.y)

    def __getitem__(self, item):
        return self.X[item], self.y[item]


class Supplier:

    def __init__(self, config):
        if "seed" in config.keys():
            random.seed(config["seed"])
        else:
            random.seed(42)
        if "verbose" not in config.keys():
            config["verbose"] = 0
        self.config = config
        self.data_path = Path(os.getcwd()) / "data/"

        self.train_data = None
        self.valid_data = None
        self.test_data = None
        self.adver_data = None

    @abstractmethod
    def load_datasets(
        self,
    ) -> None:
        """
        This method loads all necessary data according to the given configuration. It must be implemented in each
        retriever class.
        """
        raise NotImplementedError("Implement this method in children.")

    def _generate_lookback(self, X, y):
        X_lookback, y_lookback, X_window, y_window = [], [], [], []
        for X_curr, y_curr in zip(X, y):
            if len(X_window) < self.config["lookback"]:
                X_window.append(X_curr)
                y_window.append(y_curr)
            else:
                if len(set(y_window)) == 1:
                    X_lookback.append(X_window.copy())
                    y_lookback.append(y_window[0])

                X_window.append(X_curr)
                X_window.pop(0)
                y_window.append(y_curr)
                y_window.pop(0)

        if len(set(y_window)) == 1:
            X_lookback.append(X_window.copy())
            y_lookback.append(y_window[0])

        return np.array(X_lookback), np.array(y_lookback)

    def fetch_and_split_identification(self):
        if not self.train_data:
            raise ValueError(
                "In order to retrieve identification data, first load everything with the load_datasets method."
            )
        if self.config["verbose"]:
            print(
                f"Train dataset size: {self.train_data.X.shape} {self.train_data.y.shape}"
            )
            print(
                f"Validation dataset size: {self.valid_data.X.shape} {self.valid_data.y.shape}"
            )
            print(
                f"Test dataset size: {self.test_data.X.shape} {self.test_data.y.shape}"
            )
            print(
                f"Adver dataset size: {self.adver_data.X.shape} {self.adver_data.y.shape}"
            )
        return self.train_data, self.valid_data, self.test_data, self.adver_data

    def fetch_and_split_verification(self, auth_user):
        """
        Generate datasets that mark data from auth user as the positive class and
        data from other legitimate users as the negative class. In the case of adver dataset,
        the data from other users (attackers) form the negative class. All datasets are
        kept balanced between positive and negative class.
        """
        if not self.train_data:
            raise ValueError(
                "In order to retrieve verification data, first load everything with the load_datasets method."
            )
        train = self._load_verification_legitimate(self.train_data, auth_user)
        valid = self._load_verification_legitimate(self.valid_data, auth_user)
        test = self._load_verification_legitimate(self.test_data, auth_user)
        adver = self._load_verification_attacker(
            self.test_data, self.adver_data, auth_user
        )
        if self.config["verbose"]:
            print(f"Train dataset size: {train.X.shape} {train.y.shape}")
            print(f"Validation dataset size: {valid.X.shape} {valid.y.shape}")
            print(f"Test dataset size: {test.X.shape} {test.y.shape}")
            print(f"Adver dataset size: {adver.X.shape} {adver.y.shape}")

        return train, valid, test, adver

    def _load_verification_legitimate(self, dataset, auth_user):
        try:
            positive_labels = np.array(
                [1 if x[auth_user] == 1 else 0 for x in dataset.y]
            )
        except IndexError:
            raise ValueError(
                f"Auth user index ({auth_user}) greater than number of users in the datasets ({len(dataset.y[0])})."
            )

        # Get auth data
        X_auth = dataset.X[positive_labels == 1]
        y_auth = np.zeros(len(X_auth))

        # Get adver data
        X_adver = dataset.X[positive_labels == 0]
        y_adver = np.ones(len(X_adver))
        ratio = 1 / (len(dataset.y[0]) - 1)
        # Keep the dataset balanced
        _, X_adver, _, y_adver = train_test_split(
            X_adver, y_adver, test_size=ratio, stratify=y_adver
        )

        return EbatDataset(
            np.concatenate((X_auth, X_adver)),
            get_dummies(np.concatenate((y_auth, y_adver))),
        )

    def _load_verification_attacker(self, test_dataset, adver_dataset, auth_user):
        positive_labels = np.array(
            [1 if x[auth_user] == 1 else 0 for x in test_dataset.y]
        )

        # Get auth data
        X_auth = test_dataset.X[positive_labels == 1]
        y_auth = np.zeros(len(X_auth))

        # Get adver data
        ratio = 1 / len(adver_dataset.y[0])
        _, X_adver = train_test_split(
            adver_dataset.X, test_size=ratio, stratify=adver_dataset.y
        )
        y_adver = np.ones(len(X_adver))

        return EbatDataset(
            np.concatenate((X_auth, X_adver)),
            get_dummies(np.concatenate((y_auth, y_adver))),
        )

    def fetch_and_split_authentication(self):
        """
        For authentication, we merge the test and adver datasets and add a new binary ground
        truth -- either the data is legitimate or adversarial.
        """
        if not self.train_data:
            raise ValueError(
                "In order to retrieve authentication data, first load everything with the load_dataset method."
            )
        adver_data = EbatDataset(
            np.concatenate((self.test_data.X, self.adver_data.X)),
            get_dummies(
                np.concatenate(
                    (
                        np.zeros(len(self.test_data.X)),
                        np.ones(len(self.adver_data.X)),
                    )
                )
            ),
        )
        if self.config["verbose"]:
            print(
                f"Train dataset size: {self.train_data.X.shape} {self.train_data.y.shape}"
            )
            print(
                f"Validation dataset size: {self.valid_data.X.shape} {self.valid_data.y.shape}"
            )
            print(
                f"Test dataset size: {self.test_data.X.shape} {self.test_data.y.shape}"
            )
            print(f"Adver dataset size: {adver_data.X.shape} {adver_data.y.shape}")
        return self.train_data, self.valid_data, self.test_data, adver_data


class MedbaSupplier(Supplier):

    def __init__(self, config):
        super().__init__(config)

        self.data_path = self.data_path / "medba"
        if not os.path.exists(self.data_path):
            self._download()

        if not "user_num" in self.config.keys() and not "users" in self.config.keys():
            self.config["user_num"] = 15
        elif not "user_num" in self.config.keys():
            self.config["user_num"] = len(self.config["users"])
        if "users" not in self.config.keys():
            self._init_users()
        elif "adv_users" not in self.config.keys():
            self._init_adver()

        if "task" not in self.config.keys():
            self.config["task"] = "Number Comparison"
        if "exp_device" not in self.config.keys():
            self.config["exp_device"] = "comp"
        if "train" not in self.config.keys():
            self.config["train"] = {"session": 0, "diff": 0}
        if "valid" not in self.config.keys():
            self.config["valid"] = {"session": 1, "diff": 1}
        if "test" not in self.config.keys():
            self.config["test"] = {"session": 1, "diff": 2}
        self.config["adver"] = self.config["test"]

        if "window" not in self.config.keys():
            self.config["window"] = 1
        if "window_step" not in self.config.keys():
            self.config["window_step"] = 0.5

        if "lookback" not in self.config.keys():
            self.config["lookback"] = 0
        if "scale" not in self.config.keys():
            self.config["scale"] = True

        if "iot_data" not in self.config.keys():
            self.config["iot_data"] = True
        if "radar_data" not in self.config.keys():
            self.config["radar_data"] = False

        self.DIFFICULTIES = ["lo", "md", "hg"]
        self.user_classes = None

    def _download(self):
        """
        This is our own data and downloading comes out of the box. No additional steps required.
        """
        print("Downloading Medba data...", end="")
        try:
            os.makedirs(self.data_path, exist_ok=False)
        except FileExistsError:
            print(
                f"\nFiles already downloaded.\nIf corrupted, delete the {self.data_path} folder and try again."
            )
            print("")
        urlretrieve(
            "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/Behaviouralbiometrics/iot_dataset.zip",
            self.data_path / "medba.zip",
        )
        print("DONE")
        print("Extracting Medba data...", end="")
        with ZipFile(self.data_path / "medba.zip", "r") as zip_ref:
            zip_ref.extractall(self.data_path)
        os.remove(self.data_path / "medba.zip")
        print("DONE")

    def _init_users(self):
        all_users = [x for x in range(1, 55)]
        all_users.remove(3)
        self.config["users"] = random.sample(all_users, self.config["user_num"])
        self._init_adver()

    def _init_adver(self):
        all_users = [x for x in range(1, 55)]
        all_users.remove(3)
        for user in self.config["users"]:
            all_users.remove(user)
        self.config["adv_users"] = random.sample(all_users, self.config["user_num"])

    def _cast_datetime(self, data):
        try:
            data["time"] = to_datetime(data["time"])
        except ValueError:
            # Some dates are malformed, therefore, we fix the issue here.
            timedates = data["time"].tolist()
            for i, x in enumerate(timedates):
                if len(x) != 32:
                    timedates[i] = x[:19] + ".000000+00:00"
            data["time"] = to_datetime(timedates)
        return data

    def _pointcloud_feature_extraction(self, xyz):
        xyz.insert(0, [0, 0, 0])
        xyz = np.array(xyz).astype(np.float32)
        radius = 0.2
        k = 3
        try:
            knn, _ = pgeof.radius_search(xyz, xyz, radius, k)
        except ValueError:
            return np.repeat(0, 11)

        # Converting radius neighbors to CSR format
        nn_ptr = np.r_[0, (knn >= 0).sum(axis=1).cumsum()]
        nn = knn[knn >= 0]

        # You may need to convert nn/nn_ptr to uint32 arrays
        nn_ptr = nn_ptr.astype("uint32")
        nn = nn.astype("uint32")

        features = pgeof.compute_features(xyz, nn, nn_ptr)
        return features[0]

    def _load_dataset(self, partition):
        # We split the dataset in two parts for the purpose of validation/test split.
        # Also generate an adversarial dataset consisting of the same number of other users.
        users = (
            self.config["users"] if partition != "adver" else self.config["adv_users"]
        )
        X, y = [], []
        for user in users:
            seances = os.listdir(self.data_path / f"{str(user).zfill(3)}")
            iot_data = read_csv(
                self.data_path
                / f"{str(user).zfill(3)}/{seances[self.config[partition]['session']]}"
                / f"{self.config['exp_device']}/{self.config['task']}"
                / f"{self.DIFFICULTIES[self.config[partition]['diff']]}/iot_records.csv"
            )
            iot_data = self._cast_datetime(iot_data)

            radar_data = read_csv(
                self.data_path
                / f"{str(user).zfill(3)}/{seances[self.config[partition]['session']]}"
                / f"{self.config['exp_device']}/{self.config['task']}"
                / f"{self.DIFFICULTIES[self.config[partition]['diff']]}/radar_records.csv"
            )
            radar_data = self._cast_datetime(radar_data)
            radar_data["radar pointcloud"] = radar_data["radar pointcloud"].apply(
                json.loads
            )
            radar_data["radar features"] = radar_data["radar pointcloud"].apply(
                self._pointcloud_feature_extraction
            )

            curr_time = iot_data["time"].min()
            end_time = iot_data["time"].max()
            window = timedelta(seconds=self.config["window"])
            window_step = timedelta(seconds=self.config["window_step"])

            while True:
                if "iot_data" not in self.config.keys() or self.config["iot_data"]:
                    curr_data = iot_data[
                        (iot_data["time"] >= curr_time)
                        & (iot_data["time"] <= curr_time + window)
                    ]
                    curr_data = (
                        curr_data.groupby("sensor id").mean().values.T[0].tolist()
                    )
                    if len(curr_data) != 28:
                        # This sometimes occur at the very end of the session.
                        # In that case, we discard the data for the remainder of the session.
                        # print(f"Data for user {user} has only {len(curr_data)} sensors.")
                        break

                if "radar_data" in self.config.keys() and self.config["radar_data"]:
                    rad_data = radar_data[
                        (radar_data["time"] >= curr_time)
                        & (radar_data["time"] <= curr_time + window)
                    ]
                    try:
                        rad_data = rad_data["radar features"].values[0].tolist()
                    except IndexError:
                        rad_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    if self.config["iot_data"]:
                        curr_data.extend(rad_data)
                    else:
                        curr_data = rad_data

                X.append(curr_data)
                y.append(users.index(user))
                curr_time += window_step
                if curr_time > end_time:
                    break
        if self.config["scale"]:
            X = MinMaxScaler().fit_transform(X)
        if self.config["lookback"]:
            X, y = self._generate_lookback(X, y)
        y = get_dummies(np.array(y), dtype=float).values
        return np.array(X), y

    def load_datasets(self):
        if self.train_data:
            print("Datasets already loaded, you need to call this method only once.")
            return
        print("Loading the datasets...", end="")
        s = datetime.now()

        X_train, y_train = self._load_dataset("train")
        X_valid, y_valid = self._load_dataset("valid")
        X_test, y_test = self._load_dataset("test")
        X_adver, y_adver = self._load_dataset("adver")
        print(f"DONE ({datetime.now() - s})")

        if self.config["verbose"]:
            print(f"Train dataset size: {X_train.shape} {y_train.shape}")
            print(f"Validation dataset size: {X_valid.shape} {y_valid.shape}")
            print(f"Test dataset size: {X_test.shape} {y_test.shape}")
            print(f"Adver dataset size: {X_adver.shape} {y_adver.shape}")
        self.user_classes = [i for i in range(y_train.shape[1])]

        self.train_data = EbatDataset(X_train, y_train)
        self.valid_data = EbatDataset(X_valid, y_valid)
        self.test_data = EbatDataset(X_test, y_test)
        self.adver_data = EbatDataset(X_adver, y_adver)


class HmogSupplier(Supplier):
    def __init__(self, config):
        super().__init__(config)

        if not (self.data_path / "hmog/").exists():
            self._check_if_downloaded()

        if not "user_num" in self.config.keys():
            self.config["user_num"] = 15
        if "users" not in self.config.keys():
            self._init_users()
        elif "adv_users" not in self.config.keys():
            self._init_adver(self.config["users"])

        if "task" not in self.config.keys():
            self.config["task"] = "read_sit"
        if self.config["task"] == "read_sit":
            self.sessions = [1, 7, 13, 19]
        elif self.config["task"] == "read_walk":
            self.sessions = [2, 8, 14, 20]
        elif self.config["task"] == "write_sit":
            self.sessions = [3, 9, 15, 21]
        elif self.config["task"] == "write_walk":
            self.sessions = [4, 10, 16, 22]
        elif self.config["task"] == "map_sit":
            self.sessions = [5, 11, 17, 23]
        elif self.config["task"] == "map_walk":
            self.sessions = [6, 12, 18, 24]
        else:
            raise ValueError("Invalid task set in config.")

        if "train" not in self.config.keys():
            self.config["train"] = {"session": 0}
        if "valid" not in self.config.keys():
            self.config["valid"] = {"session": 1}
        if "test" not in self.config.keys():
            self.config["test"] = {"session": 2}
        self.config["adver"] = self.config["test"]

        if "window" not in self.config.keys():
            self.config["window"] = 1
        if "window_step" not in self.config.keys():
            self.config["window_step"] = 0.5

        if "scale" not in self.config.keys():
            self.config["scale"] = True
        if "lookback" not in self.config.keys():
            self.config["lookback"] = 0

    def _check_if_downloaded(self):
        """
        As we do not own the dataset, the user should do it themselves to review and agree to the TOCs imposed by the
        authors of the dataset. Here we display the instructions on how to download and set up the dataset.
        """
        if not (self.data_path / "hmog_dataset.zip").exists():
            os.makedirs(self.data_path, exist_ok=True)
            raise ValueError(
                "The HMOG dataset is not yet downloaded/placed in the proper folder. If not yet downloaded, please visit "
                "https://hmog-dataset.github.io/hmog/ and download the hmog_dataset.zip. Next, place the zip file in the "
                "data/ folder in the directory from which the retriever is being run."
            )
        else:
            hmog_path = self.data_path / "hmog"
            print("Extracting HMOG data...", end="")
            with ZipFile(self.data_path / "hmog_dataset.zip", "r") as zip_ref:
                zip_ref.extractall(hmog_path)

            users = os.listdir(hmog_path / "public_dataset")
            users.remove("data_description.pdf")
            for user in users:
                with ZipFile(hmog_path / "public_dataset" / user, "r") as zip_ref:
                    zip_ref.extractall(hmog_path)

            shutil.rmtree(hmog_path / "public_dataset")
            shutil.rmtree(hmog_path / "__MACOSX")
            os.remove(self.data_path / "hmog_dataset.zip")
            print("DONE")

    def _init_users(self):
        users = os.listdir(self.data_path / "hmog")
        self.config["users"] = random.sample(users, self.config["user_num"])
        self._init_adver()

    def _init_adver(self):
        users = os.listdir(self.data_path / "hmog")
        for user in self.config["users"]:
            users.remove(user)
        self.config["adv_users"] = random.sample(users, self.config["user_num"])

    def _load_dataset(self, partition):
        users = (
            self.config["users"] if partition != "adver" else self.config["adv_users"]
        )
        X, y = [], []
        session = self.sessions[self.config[partition]["session"]]
        for user in users:
            session_path = (
                self.data_path
                / "hmog"
                / user.split(".")[0]
                / (user.split(".")[0] + f"_session_{session}")
            )
            acc = read_csv(session_path / "Accelerometer.csv", header=None)
            gyr = read_csv(session_path / "Gyroscope.csv", header=None)
            mag = read_csv(session_path / "Magnetometer.csv", header=None)
            curr_time = min(acc.iloc[0, 0], gyr.iloc[0, 0], mag.iloc[0, 0])
            end_time = max(acc.iloc[-1, 0], gyr.iloc[-1, 0], mag.iloc[-1, 0])

            # Time is given in milliseconds in the dataset.
            window = self.config["window_step"] * 1000
            window_step = self.config["window_step"] * 1000

            while True:
                acc_data = acc[
                    (acc.iloc[:, 0] >= curr_time)
                    & (acc.iloc[:, 0] <= curr_time + window)
                ]
                gyr_data = gyr[
                    (gyr.iloc[:, 0] >= curr_time)
                    & (gyr.iloc[:, 0] <= curr_time + window)
                ]
                mag_data = mag[
                    (mag.iloc[:, 0] >= curr_time)
                    & (mag.iloc[:, 0] <= curr_time + window)
                ]
                curr_data = (
                    acc_data.mean().values[3:6].tolist()
                    + gyr_data.mean().values[3:6].tolist()
                    + mag_data.mean().values[3:6].tolist()
                )
                X.append(curr_data)
                y.append(users.index(user))
                curr_time += window_step
                if curr_time > end_time:
                    break
        if self.config["scale"]:
            X = MinMaxScaler().fit_transform(X)
        if self.config["lookback"]:
            X, y = self._generate_lookback(X, y)
        y = get_dummies(np.array(y), dtype=float).values
        return np.array(X), np.array(y)

    def load_datasets(self):
        print("Loading the datasets...", end="")

        s = datetime.now()
        X_train, y_train = self._load_dataset("train")
        X_valid, y_valid = self._load_dataset("valid")
        X_test, y_test = self._load_dataset("test")
        X_adver, y_adver = self._load_dataset("adver")
        print(f"DONE ({datetime.now() - s})")

        if self.config["verbose"]:
            print(f"Train dataset size: {X_train.shape} {y_train.shape}")
            print(f"Validation dataset size: {X_valid.shape} {y_valid.shape}")
            print(f"Test dataset size: {X_test.shape} {y_test.shape}")
            print(f"Adver dataset size: {X_adver.shape} {y_adver.shape}")
        self.user_classes = [i for i in range(y_train.shape[1])]

        self.train_data = EbatDataset(X_train, y_train)
        self.valid_data = EbatDataset(X_valid, y_valid)
        self.test_data = EbatDataset(X_test, y_test)
        self.adver_data = EbatDataset(X_adver, y_adver)


class UciharSupplier(Supplier):

    def __init__(self, config):
        super().__init__(config)

        if not (self.data_path / "ucihar").exists():
            self._check_if_downloaded()

        if not "user_num" in self.config.keys():
            self.config["user_num"] = 15
        if "users" not in self.config.keys():
            self._init_users()
        elif "adv_users" not in self.config.keys():
            self._init_adver(self.config["users"])

        if "scale" not in self.config.keys():
            self.config["scale"] = True
        if "lookback" not in self.config.keys():
            self.config["lookback"] = 0

    def _check_if_downloaded(self):
        if not (
            self.data_path / "human+activity+recognition+using+smartphones.zip"
        ).exists():
            os.makedirs(self.data_path, exist_ok=True)
            raise ValueError(
                "The UCI HAR dataset is not yet downloaded/placed in the proper folder. If not yet downloaded, please visit "
                "hhttps://archive.ics.uci.edu/dataset/240/human+activity+recognition+using+smartphones and download the dataset. "
                "Next, place the zip file in the data/ folder in the directory from which the retriever is being run."
            )
        else:
            print("Extracting UciHar data...", end="")
            ucihar_path = self.data_path / "ucihar"
            with ZipFile(
                self.data_path / "human+activity+recognition+using+smartphones.zip", "r"
            ) as zip_ref:
                zip_ref.extractall(ucihar_path)
            with ZipFile(ucihar_path / "UCI HAR Dataset.zip", "r") as zip_ref:
                zip_ref.extractall(ucihar_path)
            os.remove(
                self.data_path / "human+activity+recognition+using+smartphones.zip"
            )
            os.remove(ucihar_path / "UCI HAR Dataset.zip")
            print("DONE")

    def _init_users(self):
        users = list(np.arange(30))
        self.config["users"] = random.sample(users, self.config["user_num"])
        self._init_adver()

    def _init_adver(self):
        users = list(np.arange(30))
        for user in self.config["users"]:
            users.remove(user)
        self.config["adv_users"] = random.sample(users, self.config["user_num"])

    def _load_dataset(self, X, y):
        if self.config["scale"]:
            X = MinMaxScaler().fit_transform(X)
        if self.config["lookback"]:
            X, y = self._generate_lookback(X, y)
        y = get_dummies(y, dtype=float).values
        return X, y

    def load_datasets(self):
        if self.train_data:
            print("Datasets already loaded, you need to call this method only once.")
            return
        print("Loading the datasets...", end="")
        s = datetime.now()
        X = np.concatenate(
            (
                np.loadtxt(self.data_path / "ucihar/UCI HAR Dataset/train/X_train.txt"),
                np.loadtxt(self.data_path / "ucihar/UCI HAR Dataset/test/X_test.txt"),
            )
        )
        y = np.concatenate(
            (
                np.loadtxt(
                    self.data_path / "ucihar/UCI HAR Dataset/train/subject_train.txt"
                ),
                np.loadtxt(
                    self.data_path / "ucihar/UCI HAR Dataset/test/subject_test.txt"
                ),
            )
        )
        # The user classes start with 1, we fix it here.
        y -= 1
        X_legit, X_adver, y_legit, y_adver = [], [], [], []
        for X_tmp, y_tmp in zip(X, y):
            if y_tmp in self.config["users"]:
                X_legit.append(X_tmp)
                y_legit.append(y_tmp)
            elif y_tmp in self.config["adv_users"]:
                X_adver.append(X_tmp)
                y_adver.append(y_tmp)
        X_train, X_test, y_train, y_test = train_test_split(
            X_legit, y_legit, test_size=0.3, stratify=y_legit
        )
        X_valid, X_test, y_valid, y_test = train_test_split(
            X_test, y_test, test_size=0.67, stratify=y_test
        )
        # We sample from the adversarial part of the data to keep the test-adver ratio balanced.
        X_adver, _, y_adver, _ = train_test_split(
            X_adver, y_adver, test_size=0.799, stratify=y_adver
        )
        X_train, y_train = self._load_dataset(X_train, y_train)
        X_valid, y_valid = self._load_dataset(X_valid, y_valid)
        X_test, y_test = self._load_dataset(X_test, y_test)
        X_adver, y_adver = self._load_dataset(X_adver, y_adver)
        print(f"DONE ({datetime.now() - s}")

        if self.config["verbose"]:
            print(f"Train dataset size: {X_train.shape} {y_train.shape}")
            print(f"Validation dataset size: {X_valid.shape} {y_valid.shape}")
            print(f"Test dataset size: {X_test.shape} {y_test.shape}")
            print(f"Adver dataset size: {X_adver.shape} {y_adver.shape}")
        self.user_classes = [i for i in range(y_train.shape[1])]

        self.train_data = EbatDataset(X_train, y_train)
        self.valid_data = EbatDataset(X_valid, y_valid)
        self.test_data = EbatDataset(X_test, y_test)
        self.adver_data = EbatDataset(X_adver, y_adver)


if __name__ == "__main__":
    # ret = MedbaRetriever(
    #     {
    #         "users": [5, 6, 22, 24, 27, 31, 38, 41, 43, 45, 49, 50, 51, 53, 54],
    #         "exp_device": "comp",
    #         "task": "Typing",
    #         "window": 1,
    #         "window_step": 0.5,
    #         "train": {"seance": 0, "diff": 0},
    #         "valid": {"seance": 0, "diff": 0},
    #         "test": {"seance": 0, "diff": 0},
    #         "adver": {"seance": 0, "diff": 0},
    #     }
    # )
    # ret = MedbaRetriever({"user_num": 3})
    ret = HmogSupplier({"window": 1, "window_step": 1})
    # ret = UciharRetriever({"user_num": 3})
    ret.load_datasets()
    ret.fetch_and_split_identification()
    print()
    ret.fetch_and_split_verification(1)
    print()
    ret.fetch_and_split_authentication()
