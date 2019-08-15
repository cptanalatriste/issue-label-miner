from sklearn.metrics import classification_report
import pandas as pd

import labelanalysis

ASSESMENT_COLUMN = "Carlos: Using labels as priority?"
REPOSITORY_URL_COLUM = "url"


def get_validation_report(assessment_csv="assessed_sample.csv", assessment_column=ASSESMENT_COLUMN):
    assessed_dataframe = pd.read_csv(assessment_csv)
    heuristic_dataframe_all = pd.read_csv(labelanalysis.CONSOLIDATED_CSV_FILE)

    assessed_dataframe[assessment_column] = assessed_dataframe[assessment_column].map(
        {"FALSE": False,
         "TRUE": True,
         "NONE": None})

    filter = assessed_dataframe[assessment_column].notnull()
    assessed_dataframe = assessed_dataframe[filter]

    consolidated_dataframe = pd.merge(assessed_dataframe, heuristic_dataframe_all, left_on=REPOSITORY_URL_COLUM,
                                      right_on=labelanalysis.REPOSITORY_URL_COLUMN)

    heuristic_results = consolidated_dataframe[labelanalysis.USING_PRIORITIES_COLUMN].astype(int)
    manual_validation = consolidated_dataframe[assessment_column].astype(int)

    target_names = ["not using priorities", "using priorities"]

    print(pd.crosstab(heuristic_results.values, manual_validation.values, rownames=["Heuristic"], colnames=["Manual"],
                      margins=False,
                      margins_name="Total"))

    print(classification_report(y_pred=heuristic_results, y_true=manual_validation,
                                target_names=target_names))


def consolidate_assesment_files() :

    first_dataframe =  pd.read_csv("assessed_sample.csv")
    first_dataframe = first_dataframe[["url", "Carlos: Using labels as priority?"]]

    print(first_dataframe.head())

if __name__ == "__main__":
    # get_validation_report()

    consolidate_assesment_files()
