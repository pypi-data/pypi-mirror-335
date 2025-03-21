from abc import abstractmethod

import numpy as np
import torch
from torch.utils.data import DataLoader

from src.ebat.data.suppliers import MedbaRetriever, HmogRetriever, UciharRetriever
from src.ebat.evaluation.evaluator import (
    evaluate_identification,
    evaluate_authentication,
    evaluate_verification,
    compare_results,
    ContinuousResults,
)


class BaseClassifier:

    def __init__(self):
        self.model = None

    @abstractmethod
    def identification(self, X_test):
        pass

    @abstractmethod
    def verification(self, X_test):
        pass

    @abstractmethod
    def authentication(self, X_auth):
        pass


class MLPModel(torch.nn.Module):
    def __init__(self, input_nodes, output_nodes, middle_layer_size):
        super().__init__()
        self.linear1 = torch.nn.Linear(input_nodes, middle_layer_size)
        self.activation = torch.nn.ReLU()
        self.dropout = torch.nn.Dropout(0.5)
        self.linear2 = torch.nn.Linear(middle_layer_size, output_nodes)
        self.softmax = torch.nn.Softmax(dim=1)

    def forward(self, x):
        x = self.linear1(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.linear2(x)
        x = self.softmax(x)
        return x


class SimpleMLP(BaseClassifier):
    def __init__(self, input_nodes, output_nodes, middle_layer_size=1024):
        super().__init__()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = MLPModel(input_nodes, output_nodes, middle_layer_size).to(
            self.device
        )
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.0001)
        if output_nodes > 2:
            self.loss = torch.nn.CrossEntropyLoss()
        else:
            self.loss = torch.nn.BCELoss()

    def __str__(self):
        return "Simple MLP Classifier"

    def training(self, train_data):
        train_data = DataLoader(
            train_data,
            batch_size=32,
            shuffle=True,
            drop_last=True,
        )
        self.model.train()
        for e in range(10):
            for X, y in train_data:
                X, y = (
                    X.to(self.device).float(),
                    y.to(self.device).float(),
                )
                y_pred = self.model(X)
                loss = self.loss(y_pred, y)

                loss.backward()
                self.optimizer.step()

    def identification(self, X_id):
        self.model.eval()
        X_id = torch.tensor(X_id).to(self.device).float()
        return self.model(X_id).detach().cpu().numpy()

    def verification(self, X_ver):
        self.model.eval()
        X_ver = torch.tensor(X_ver).to(self.device).float()
        return self.model(X_ver).detach().cpu().numpy()

    def authentication(self, X_auth):
        """
        Take the max probability and use it as a probability of successful authentication.
        """
        self.model.eval()
        X_auth = torch.tensor(X_auth).to(self.device).float()
        y_scores = self.model(X_auth).detach().cpu().numpy()
        return [[x, 1 - x] for x in np.max(y_scores, axis=1)]


if __name__ == "__main__":
    # Load all required data
    NN_SIZE = 1024
    config = {"user_num": 3, "window": 2, "window_step": 0.1}
    ret = MedbaRetriever(config)
    # ret = HmogRetriever(config)
    # ret = UciharRetriever(config)
    ret.load_datasets()

    # Train and evaluate identification
    id_train, _, id_test, _ = ret.retrieve_identification()
    identifier = SimpleMLP(
        input_nodes=28, output_nodes=config["user_num"], middle_layer_size=NN_SIZE
    )
    identifier.training(id_train)
    result = evaluate_identification(identifier, id_test)
    result.metrics()
    result.visualise()

    # Use the identification model to also evaluate authentication
    _, _, _, auth_adver = ret.retrieve_authentication()
    result = evaluate_authentication(identifier, auth_adver)
    result.metrics()
    result.visualise()
    # result.save_results()

    # # Train, evaluate, and compare verification
    results = []
    for i in range(config["user_num"]):
        ver_train, _, ver_test, ver_adver = ret.retrieve_verification(i)
        verifier = SimpleMLP(input_nodes=28, output_nodes=2, middle_layer_size=NN_SIZE)
        verifier.training(ver_train)
        result = evaluate_verification(verifier, ver_adver)
        results.append(result)
    compare_results(results)

    # a = ContinuousResults("Approach 1")
    # a.retrieve_results("2025-03-06T09-23-35_authenticator.json")
    # b = ContinuousResults("Approach 2")
    # b.retrieve_results("2025-03-06T09-26-23_authenticator.json")
    # compare_results((a, b))
