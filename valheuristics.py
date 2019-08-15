from sklearn.metrics import classification_report
import pandas as pd

import labelanalysis

ASSESMENT_COLUMN = "manual_assessment"


def get_validation_report(assessed_dataframe):
    heuristic_dataframe_all = pd.read_csv(labelanalysis.CONSOLIDATED_CSV_FILE)

    consolidated_dataframe = pd.merge(assessed_dataframe, heuristic_dataframe_all,
                                      on=labelanalysis.REPOSITORY_URL_COLUMN)

    consolidated_dataframe.to_csv("consolidated_dataframe.csv")

    heuristic_results = consolidated_dataframe[labelanalysis.USING_PRIORITIES_COLUMN].astype(int)
    manual_validation = consolidated_dataframe[ASSESMENT_COLUMN].astype(int)

    target_names = ["not using priorities", "using priorities"]

    print(pd.crosstab(heuristic_results.values, manual_validation.values, rownames=["Heuristic"], colnames=["Manual"],
                      margins=False,
                      margins_name="Total"))

    print(classification_report(y_pred=heuristic_results, y_true=manual_validation,
                                target_names=target_names))


def consolidate_assesment_files():
    first_dataframe = pd.read_csv("assessed_sample.csv")
    first_dataframe = first_dataframe[["url", "Carlos: Using labels as priority?"]]
    first_dataframe = first_dataframe.rename(
        columns={"Carlos: Using labels as priority?": ASSESMENT_COLUMN,
                 "url": labelanalysis.REPOSITORY_URL_COLUMN})

    second_dataframe = pd.read_csv("assessed_sample_custom.csv")
    second_dataframe = second_dataframe[[labelanalysis.REPOSITORY_URL_COLUMN, "Carlos: Using Priorities?"]]
    second_dataframe = second_dataframe.rename(
        columns={"Carlos: Using Priorities?": ASSESMENT_COLUMN})

    consolidated_dataframe = pd.concat([first_dataframe, second_dataframe]).drop_duplicates().reset_index(drop=True)

    consolidated_dataframe[ASSESMENT_COLUMN] = consolidated_dataframe[
        ASSESMENT_COLUMN].map(
        {"FALSE": False,
         "TRUE": True,
         "NONE": None})

    filter = consolidated_dataframe[ASSESMENT_COLUMN].notnull()
    consolidated_dataframe = consolidated_dataframe[filter]

    return consolidated_dataframe


if __name__ == "__main__":
    consolidated_dataframe = consolidate_assesment_files()

    print(consolidated_dataframe.describe())

    get_validation_report(consolidated_dataframe)
