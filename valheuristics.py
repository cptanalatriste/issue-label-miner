from sklearn.metrics import classification_report
import pandas as pd

import labelanalysis

ASSESMENT_COLUMN = "Carlos: Using labels as priority?"


def get_validation_report(assessment_csv="assessed_sample.csv"):
    assessed_dataframe = pd.read_csv(assessment_csv)
    heuristic_dataframe = pd.read_csv(labelanalysis.CONSOLIDATED_CSV_FILE)

    manual_validation = assessed_dataframe[ASSESMENT_COLUMN]
    heuristic_results = []
    target_names = ["using priorities", "not using priorities"]

    print(classification_report(y_pred=heuristic_results, y_true=manual_validation, target_names=target_names))


if __name__ == "__main__":
    get_validation_report()
