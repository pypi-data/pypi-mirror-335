def frequency_count_of_scores(y_true, scores):
    """
    Based on the paper: https://par.nsf.gov/biblio/10091768
    :param y_true: list of (n_samples) ground truth labels (0 is positive class -> legitimate user)
    :param scores: list of (n_samples) confidence levels for positive class of y_true.
    :return: frequency count of scores
    """
    legitimate_scores, illegitimate_scores = [], []
    for i, label in enumerate(y_true):
        if label == 0:
            legitimate_scores.append(scores[i])
        else:
            illegitimate_scores.append(scores[i])
    return {
        "legit_scores": [float(x) for x in legitimate_scores],
        "illegit_scores": [float(x) for x in illegitimate_scores],
    }
