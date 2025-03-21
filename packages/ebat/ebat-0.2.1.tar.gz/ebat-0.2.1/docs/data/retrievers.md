**Retriever Classes Documentation**
=====================================

### Overview

This module provides a set of classes for retrieving and processing datasets for behavioral biometrics analysis. The main classes are `Retriever`, `MedbaRetriever`, `HmogRetriever`, and `UciharRetriever`.

### Retriever Class
-------------------

#### Description

The `Retriever` class is the base class for all retriever classes. It provides methods for loading datasets, retrieving identification, verification, and authentication data.

#### Methods

*   `__init__(config)`: Initializes the retriever with a configuration dictionary.
*   `load_datasets()`: Loads the datasets according to the configuration. This method must be implemented in each retriever class.
*   `retrieve_identification()`: Retrieves the identification data.
*   `retrieve_verification(auth_user)`: Retrieves the verification data for a given authentication user.
*   `retrieve_authentication()`: Retrieves the authentication data.
*   `_generate_lookback(X, y)`: Generates lookback data for a given dataset.

### MedbaRetriever Class
-------------------------

#### Description

The `MedbaRetriever` class is a retriever for the Medba dataset.

#### Methods

*   `__init__(config)`: Initializes the Medba retriever with a configuration dictionary.
*   `load_datasets()`: Loads the Medba datasets according to the configuration.
*   `_download()`: Downloads the Medba dataset if it is not already downloaded.
*   `_init_users()`: Initializes the users for the Medba dataset.
*   `_init_adver()`: Initializes the adversarial users for the Medba dataset.
*   `_cast_datetime(data)`: Casts the datetime column of a dataset to a datetime format.
*   `_pointcloud_feature_extraction(xyz)`: Extracts features from a point cloud dataset.
*   `_load_dataset(partition)`: Loads a Medba dataset for a given partition.

### HmogRetriever Class
-------------------------

#### Description

The `HmogRetriever` class is a retriever for the HMOG dataset.

#### Methods

*   `__init__(config)`: Initializes the HMOG retriever with a configuration dictionary.
*   `load_datasets()`: Loads the HMOG datasets according to the configuration.
*   `_check_if_downloaded()`: Checks if the HMOG dataset is downloaded and extracts it if necessary.
*   `_init_users()`: Initializes the users for the HMOG dataset.
*   `_init_adver()`: Initializes the adversarial users for the HMOG dataset.
*   `_load_dataset(partition)`: Loads an HMOG dataset for a given partition.

### UciharRetriever Class
-------------------------

#### Description

The `UciharRetriever` class is a retriever for the UCI HAR dataset.

#### Methods

*   `__init__(config)`: Initializes the UCI HAR retriever with a configuration dictionary.
*   `load_datasets()`: Loads the UCI HAR datasets according to the configuration.
*   `_check_if_downloaded()`: Checks if the UCI HAR dataset is downloaded and extracts it if necessary.
*   `_init_users()`: Initializes the users for the UCI HAR dataset.
*   `_init_adver()`: Initializes the adversarial users for the UCI HAR dataset.
*   `_load_dataset(X, y)`: Loads a UCI HAR dataset for given features and labels.

### EbatDataset Class
----------------------

#### Description

The `EbatDataset` class is a dataset class for behavioral biometrics data.

#### Methods

*   `__init__(X, y)`: Initializes the dataset with features and labels.
*   `__len__()`: Returns the length of the dataset.
*   `__getitem__(item)`: Returns a feature and label pair for a given index.

### Example Usage
-----------------

```python
ret = MedbaRetriever({"user_num": 3})
ret.load_datasets()
ret.retrieve_identification()
print()
ret.retrieve_verification(1)
print()
ret.retrieve_authentication()
```

### Configuration Options
-------------------------

The configuration options for each retriever class are as follows:

*   `MedbaRetriever`:
    *   `user_num`: The number of users to select from the dataset.
    *   `users`: A list of user IDs to select from the dataset.
    *   `exp_device`: The device to use for the experiment (e.g., "comp").
    *   `task`: The task to perform (e.g., "Typing").
    *   `window`: The window size for the dataset.
    *   `window_step`: The window step size for the dataset.
    *   `train`: A dictionary containing the training session and difficulty.
    *   `valid`: A dictionary containing the validation session and difficulty.
    *   `test`: A dictionary containing the test session and difficulty.
    *   `adver`: A dictionary containing the adversarial session and difficulty.
*   `HmogRetriever`:
    *   `user_num`: The number of users to select from the dataset.
    *   `users`: A list of user IDs to select from the dataset.
    *   `task`: The task to perform (e.g., "read_sit").
    *   `window`: The window size for the dataset.
    *   `window_step`: The window step size for the dataset.
    *   `train`: A dictionary containing the training session.
    *   `valid`: A dictionary containing the validation session.
    *   `test`: A dictionary containing the test session.
    *   `adver`: A dictionary containing the adversarial session.
*   `UciharRetriever`:
    *   `user_num`: The number of users to select from the dataset.
    *   `users`: A list of user IDs to select from the dataset.
    *   `scale`: A boolean indicating whether to scale the dataset.
    *   `lookback`: The lookback size for the dataset.
[Warning: Text generated by GPT@JRC using Generative AI technology - Please assess this text critically before using it]