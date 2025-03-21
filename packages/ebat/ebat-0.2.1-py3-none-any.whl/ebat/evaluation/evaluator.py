import json
import os
from abc import abstractmethod
from datetime import datetime
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    precision_recall_fscore_support,
    accuracy_score,
    det_curve,
    matthews_corrcoef,
    roc_curve,
    confusion_matrix,
    roc_auc_score,
)

from plotly import graph_objects as go

from ebat.evaluation.metrics.frequency_count_of_scores import (
    frequency_count_of_scores,
)


class ResultsBase:

    def __init__(self, approach_name, decimal_places=3):
        self.results = {}
        self.approach_name = approach_name
        self.decimal_places = decimal_places
        self.save_path = Path(os.getcwd()) / "results"

    def add_metric(self, name, value):
        self.results[name] = value

    def save_results(self):
        self.save_path.mkdir(exist_ok=True)
        file_name = (
            f"{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}_{self.approach_name}.json"
        )
        with open(self.save_path / file_name, "w") as save_file:
            json.dump(self.results, save_file)

    def retrieve_results(self, results_name):
        with open(self.save_path / results_name, "r") as save_file:
            self.results = json.load(save_file)


class OneoffResults(ResultsBase):

    def __init__(self, approach_name):
        super().__init__(approach_name)

    def metrics(self):
        print(f"Accuracy: {round(self.results['acc'], self.decimal_places)}")
        print(f"Precision: {round(self.results['prec'], self.decimal_places)}")
        print(f"Recall: {round(self.results['rec'], self.decimal_places)}")
        print(f"F1 Score: {round(self.results['f1'], self.decimal_places)}")
        print(
            f"Matthews Corr. Coef.: {round(self.results['mcc'], self.decimal_places)}"
        )

    def visualise(self):
        fig = go.Figure(
            data=go.Heatmap(
                x=[f"User {x + 1}" for x in range(len(self.results["cm"][0]))],
                y=[f"User {x + 1}" for x in range(len(self.results["cm"][0]))],
                z=self.results["cm"],
            )
        )
        fig.update_layout(
            {
                "title": "Per-user Confusion Matrix",
                "xaxis_title": "Predicted User",
                "yaxis_title": "True User",
            }
        )
        fig.show()


class ContinuousResults(ResultsBase):

    def __init__(self, approach_name):
        super().__init__(approach_name)

    def metrics(self):
        print(f"Equal Error Rate: {round(self.results['eer'], self.decimal_places)}")
        print(f"Gini Coef.: {round(self.results['gini'], self.decimal_places)}")

    def visualise(self):
        fig = go.Figure(
            data=go.Scatter(
                x=self.results["roc_curve"]["tpr"], y=self.results["roc_curve"]["fpr"]
            ),
        )
        fig.update_layout(
            {
                "title": "Receiver Operating Characteristic Curve",
                "xaxis_title": "False Positive Rate",
                "xaxis_range": [0, 1],
                "yaxis_title": "True Positive Rate",
                "yaxis_range": [0, 1],
            }
        )
        fig.show()

        fig = go.Figure(
            data=go.Scatter(
                x=self.results["det_curve"]["far"], y=self.results["det_curve"]["frr"]
            )
        )
        fig.update_layout(
            {
                "title": "Detection Error Tradeoff Curve",
                "xaxis_title": "False Positive Rate",
                "xaxis_range": [0, 1],
                "yaxis_title": "False Negative Rate",
                "yaxis_range": [0, 1],
            }
        )
        fig.show()

        fig = go.Figure(
            data=[
                go.Scatter(
                    x=self.results["det_curve"]["thresholds"],
                    y=self.results["det_curve"]["far"],
                    name="FAR",
                ),
                go.Scatter(
                    x=self.results["det_curve"]["thresholds"],
                    y=self.results["det_curve"]["frr"],
                    name="FRR",
                ),
            ]
        )
        fig.update_layout(
            {
                "title": "FAR vs. FRR Curves",
                "xaxis_title": "Threshold",
                "xaxis_range": [0, 1],
                "yaxis_title": "Rates",
                "yaxis_range": [0, 1],
            }
        )
        fig.show()

        # Automatically calculate the number of bins
        nbins = (
            (
                len(self.results["fcs"]["legit_scores"])
                + len(self.results["fcs"]["illegit_scores"])
            )
            // 2
            // 10
        )
        fig = go.Figure(
            data=[
                go.Histogram(
                    x=self.results["fcs"]["legit_scores"],
                    name="Legitimate",
                    nbinsx=nbins,
                ),
                go.Histogram(
                    x=self.results["fcs"]["illegit_scores"],
                    name="Illegitimate",
                    nbinsx=nbins,
                ),
            ]
        )
        fig.update_layout(
            {
                "title": "Frequency Count of Scores",
                "xaxis_title": "Score",
                "yaxis_title": "Frequency Count",
                "barmode": "overlay",
            }
        )
        fig.update_traces({"opacity": 0.75})
        fig.show()


# Calculation of evaluation metrics


def evaluate_identification(identifier, id_data, approach_name="identifier"):
    X_test = id_data.X
    y_test = list(np.argmax(id_data.y, axis=1))
    y_pred = np.argmax(identifier.identification(X_test), axis=1)

    results = OneoffResults(approach_name)
    results.add_metric("cm", confusion_matrix(y_test, y_pred).tolist())
    results.add_metric("acc", accuracy_score(y_test, y_pred))
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average="macro", zero_division=0
    )
    results.add_metric("prec", prec)
    results.add_metric("rec", rec)
    results.add_metric("f1", f1)
    results.add_metric("mcc", matthews_corrcoef(y_test, y_pred))
    return results


def calculate_continuous(y_true, y_pred, approach_name):
    results = ContinuousResults(approach_name)

    fpr, tpr, thresholds_roc = roc_curve(y_true, y_pred)
    results.add_metric(
        "roc_curve",
        {
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "thresholds": thresholds_roc.tolist(),
        },
    )
    results.add_metric(
        "gini", 2 * roc_auc_score([0 if x == 1 else 1 for x in y_true], y_pred) - 1
    )
    far, frr, thresholds_det = det_curve(y_true, y_pred, pos_label=0)
    results.add_metric(
        "det_curve",
        {
            "far": far.tolist(),
            "frr": frr.tolist(),
            "thresholds": thresholds_det.tolist(),
        },
    )
    results.add_metric("fcs", frequency_count_of_scores(y_true, y_pred))

    deltas = [abs(x - y) for x, y in zip(far, frr)]
    min_i = np.argmin(deltas)
    results.add_metric("eer", (far[min_i] + frr[min_i]) / 2)
    return results


def evaluate_verification(verifier, auth_data, approach_name="verifier"):
    # 0, 1 vector of ground truth (0 — auth user, 1 attackers)
    y_true = np.argmax(auth_data.y, axis=1)
    y_scores = verifier.verification(auth_data.X)
    # Probability of positive class (auth user) as required by curve functions.
    y_pred = [x[0] for x in y_scores]
    return calculate_continuous(y_true, y_pred, approach_name)


def evaluate_authentication(authenticator, auth_data, approach_name="authenticator"):
    y_true = np.argmax(auth_data.y, axis=1)
    y_scores = authenticator.authentication(auth_data.X)
    y_pred = [x[0] for x in y_scores]
    return calculate_continuous(y_true, y_pred, approach_name)


def compare_results(results):
    roc_data, det_data = [], []
    for i, result in enumerate(results):
        roc_data.append(
            go.Scatter(
                x=result.results["roc_curve"]["tpr"],
                y=result.results["roc_curve"]["fpr"],
                name=result.approach_name,
            )
        )
        det_data.append(
            go.Scatter(
                x=result.results["det_curve"]["far"],
                y=result.results["det_curve"]["frr"],
                name=result.approach_name,
            )
        )
    fig = go.Figure(data=roc_data)
    fig.update_layout(
        {
            "title": "Receiver Operating Characteristic Curve",
            "xaxis_title": "False Positive Rate",
            "xaxis_range": [0, 1],
            "yaxis_title": "True Positive Rate",
            "yaxis_range": [0, 1],
        }
    )
    fig.show()

    fig = go.Figure(data=det_data)
    fig.update_layout(
        {
            "title": "Detection Error Tradeoff Curve",
            "xaxis_title": "False Positive Rate",
            "xaxis_range": [0, 1],
            "yaxis_title": "False Negative Rate",
            "yaxis_range": [0, 1],
        }
    )
    fig.show()
