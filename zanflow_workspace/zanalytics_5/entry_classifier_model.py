Entry Classifier Model
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
# entry_classifier_model.py
# Scaffolds ML-driven entry confidence scoring engine

import numpy as np
import pandas as pd

class EntryClassifier:
    def __init__(self, model=None):
        self.model = model  # could be a sklearn model or custom callable

    def extract_features(self, context):
        """
        Converts a dictionary of entry context (e.g. structure, volume, sweep, rr) into a feature vector
        Example input context:
        {
            "rr_ratio": 2.5,
            "distance_to_ob": 4.2,
            "volume_score": 0.8,
            "has_choch": 1,
            "liquidity_tag": "sweep"
        }
        """
        features = [
            context.get("rr_ratio", 0),
            context.get("distance_to_ob", 0),
            context.get("volume_score", 0),
            context.get("has_choch", 0),
            1 if context.get("liquidity_tag") == "sweep" else 0
        ]
        return np.array(features).reshape(1, -1)

    def score(self, context):
        if self.model is None:
            return 0.5  # Neutral fallback score
        features = self.extract_features(context)
        prob = self.model.predict_proba(features)[0][1]  # assumes binary classifier
        return prob


if __name__ == "__main__":
    clf = EntryClassifier()
    mock_context = {
        "rr_ratio": 2.1,
        "distance_to_ob": 3.7,
        "volume_score": 0.92,
        "has_choch": 1,
        "liquidity_tag": "sweep"
    }
    score = clf.score(mock_context)
    print(f"Entry score: {score:.2f}")

