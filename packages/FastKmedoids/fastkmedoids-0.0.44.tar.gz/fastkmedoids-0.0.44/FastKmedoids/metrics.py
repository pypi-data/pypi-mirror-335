import numpy as np
from itertools import permutations

#####################################################################################################################

def adjusted_accuracy(y_pred, y_true):
    """
    Computes the adjusted accuracy as the maximum accuracy  of the ones obtained for all the possible permutations of the cluster labels (`y_pred`).

    Parameters (inputs)
    ----------
    y_pred: a numpy array with the predictions of the response.
    y_true: a numpy array with the true values of the response.

    Returns (outputs)
    -------
    adj_accuracy: the value of the best accuracy.
    adj_cluster_labels: the clusters labels associated to the best accuracy.
    """

    permutations_list = list(permutations(np.unique(y_pred)))
    accuracy, permuted_cluster_labels = [], {}
    for per in permutations_list:
        permutation_dict = dict(zip(np.unique(y_pred), per))
        permuted_cluster_labels[per] = np.array([permutation_dict[x] for x in y_pred])
        accuracy.append(np.mean(permuted_cluster_labels[per] == y_true))
    accuracy = np.array(accuracy)
    best_permutation = permutations_list[np.argmax(accuracy)]
    adj_cluster_labels = permuted_cluster_labels[best_permutation]
    adj_accuracy = np.max(accuracy)
  
    return adj_accuracy, adj_cluster_labels