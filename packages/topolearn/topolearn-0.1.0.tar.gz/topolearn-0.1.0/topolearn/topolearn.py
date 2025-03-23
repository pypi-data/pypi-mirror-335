import numpy as np
import pandas as pd
import pickle
import pkg_resources
import logging
from ripser import ripser
from gtda.diagrams import PersistenceEntropy
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TopoLearn():
    def __init__(self, model_path="topolearn.pkl") -> None:
        """Class to compute the TopoLearn score using persistent homology.

        Args:
            X (numpy array): The numeric representation of a dataset.
            sim_metric (string): Distance metric used by ripser for PH computation.
        """
        package_model_path = pkg_resources.resource_filename(
            __name__, model_path)
        with open(package_model_path, 'rb') as f:
            self.model = pickle.load(f)
            self.train_distance_metrics = ["jaccard", "euclidean"]
            self.features = ['b_0', 'b_1', 'b_0_norm', 'b_1_norm', 'ph_entr_0', 'ph_entr_1', 'lifetimes_min_0',
                             'norm_lifetimes_min_0', 'lifetimes_max_0', 'norm_lifetimes_max_0', 'lifetimes_mean_0',
                             'norm_lifetimes_mean_0', 'lifetimes_var_0', 'norm_lifetimes_var_0', 'lifetimes_sum_0',
                             'norm_lifetimes_sum_0', 'midlifes_min_0', 'norm_midlifes_min_0', 'midlifes_max_0',
                             'norm_midlifes_max_0', 'midlifes_mean_0', 'norm_midlifes_mean_0', 'midlifes_var_0',
                             'norm_midlifes_var_0', 'midlifes_sum_0', 'norm_midlifes_sum_0', 'lifetimes_min_1',
                             'norm_lifetimes_min_1', 'lifetimes_max_1', 'norm_lifetimes_max_1', 'lifetimes_mean_1',
                             'norm_lifetimes_mean_1', 'lifetimes_var_1', 'norm_lifetimes_var_1', 'lifetimes_sum_1',
                             'norm_lifetimes_sum_1', 'midlifes_min_1', 'norm_midlifes_min_1', 'midlifes_max_1',
                             'norm_midlifes_max_1', 'midlifes_mean_1', 'norm_midlifes_mean_1', 'midlifes_var_1',
                             'norm_midlifes_var_1', 'midlifes_sum_1', 'norm_midlifes_sum_1']

    def _compute_lifetime_stats(self, dgm, h_dim, suffix=""):
        # Normal persistence lifetimes
        dgm = dgm[~np.isinf(dgm).any(1)]
        descriptors = {}
        aggs = [np.min, np.max, np.mean, np.var, np.sum]

        # Lifetime descriptors
        lifetimes = dgm[:, 1] - dgm[:, 0]
        if lifetimes.shape[0] > 0:
            norm_lifetimes = lifetimes / lifetimes.sum()
            for agg in aggs:
                descriptors[f"lifetimes_{agg.__name__}_{h_dim}{suffix}"] = agg(
                    lifetimes)
                descriptors[f"norm_lifetimes_{agg.__name__}_{h_dim}{suffix}"] = agg(
                    norm_lifetimes)

        else:
            for agg in aggs:
                descriptors[f"lifetimes_{agg.__name__}_{h_dim}{suffix}"] = np.nan
                descriptors[f"norm_lifetimes_{agg.__name__}_{h_dim}{suffix}"] = np.nan

        # Midlife descriptors
        midlifes = (dgm[:, 1] + dgm[:, 0]) / 2
        if midlifes.shape[0] > 0:
            norm_midlifes = midlifes / midlifes.sum()
            for agg in aggs:
                descriptors[f"midlifes_{agg.__name__}_{h_dim}{suffix}"] = agg(
                    midlifes)
                descriptors[f"norm_midlifes_{agg.__name__}_{h_dim}{suffix}"] = agg(
                    norm_midlifes)

        else:
            for agg in aggs:
                descriptors[f"midlifes_{agg.__name__}_{h_dim}{suffix}"] = np.nan
                descriptors[f"norm_midlifes_{agg.__name__}_{h_dim}{suffix}"] = np.nan
        return descriptors

    def _compute_betti(self, dgm):
        b = dgm.shape[0]
        return b

    def _compute_betti_norm(self, X, dgm):
        b_norm = dgm.shape[0] / X.shape[0]
        return b_norm

    def _compute_persistence_entropy(self, dgms, idx=0):
        # Align the format for ripser with giotto-tda
        q_pad = np.concatenate(
            [dgms[idx], np.full((dgms[idx].shape[0], 1), idx)], axis=1)
        dgms_giotto = np.expand_dims(q_pad, 0)
        PE = PersistenceEntropy(n_jobs=-1)
        return PE.fit_transform(dgms_giotto)

    def _compute_ph_features(self, X, dgms):
        features = {}
        features["b_0"] = self._compute_betti(dgms[0])
        features["b_1"] = self._compute_betti(dgms[1])
        features["b_0_norm"] = self._compute_betti_norm(X, dgms[0])
        features["b_1_norm"] = self._compute_betti_norm(X, dgms[1])

        if len(dgms[0]) > 0:
            ph_entr_0 = self._compute_persistence_entropy(dgms, idx=0)[0][0]
        else:
            ph_entr_0 = np.nan
        if len(dgms[1]) > 0:
            ph_entr_1 = self._compute_persistence_entropy(dgms, idx=1)[0][0]
        else:
            ph_entr_1 = np.nan

        features["ph_entr_0"] = ph_entr_0
        features["ph_entr_1"] = ph_entr_1
        features = features | self._compute_lifetime_stats(dgms[0], h_dim=0)
        features = features | self._compute_lifetime_stats(dgms[1], h_dim=1)
        return features

    def compute_score(self, X, sim_metric, clip=True):
        """Computes the TopoLearn score using persistent homology
           and a RandomForest regressor trained on 12 datasets along with
           26 different representations. 

        Args:
            X (np.array): Numeric representation for an entire dataset with 
                          shape (n_samples, n_features)
            sim_metric (str): Similarity metric used by ripser. 'jaccard' and 
                            'euclidean' are the two options for the current model.
            clip (bool): If clipping into range [0, 1] is applied on the prediction.
        Returns:
            float: Relative RMSE prediction score, if no clipping is used it
                    may also fall outside the range [0, 1].
        """
        if isinstance(X, pd.DataFrame):
            logging.info("Converting input dataframe to numpy array.")
            X = X.values
        if sim_metric not in self.train_distance_metrics:
            logging.warn("This version of topolearn was only trained on data using "
                         f"{self.train_distance_metrics} as distance metrics. Other measures "
                         "might lead to unexpected results.")
        dgms = ripser(X, metric=sim_metric)['dgms']
        features = self._compute_ph_features(X, dgms)
        feature_vector = np.array(list(features.values())).reshape(1, -1)
        feature_df = pd.DataFrame.from_records(
            feature_vector, columns=self.features)

        # Check if feature ordering is the same
        assert all([i == j for i, j in zip(self.features, features)])

        # Get model prediction
        pred = self.model.predict(feature_df)[0]
        if clip:
            return max(0, min(pred, 1))
        else:
            return pred
