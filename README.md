# Introduction

In this example we use Veritable to predict which patients have heart disease. The dataset for this example is standard, part of the UC Irvine machine learning repository (http://archive.ics.uci.edu/ml/datasets/Heart+Disease).

This is a _classification_ problem. We predict the `target` column, a measure of the presence of heart disease in the patient. This column has five possible values, and it's unclear from the data dictionary whether they should be understood as _ordinal_ (measures of the severity of heart disease) or as _categorical_ (different forms of heart disease). All the published studies have focused on the binary classification problem of distinguishing absence (value 0) from presence of heart disease (values 1, 2, 3, and 4). This script runs both the binary and multiway classification problems.

# Files

* `heart_disease/run.py`: A Python script that divides the data into train and test sets, runs an analysis on the training set, and makes predictions for the target column on the test set.
* `heart_disease/data.json`: A json file containing the preprocessed data from the `hungarian.data`, `long-beach-va.data`, and `switzerland.data` files.
* `heart_disease/schema.json`: A json file containing a schema with column types for the data.
* `original_data/`: A directory containing the original data files; note that the `cleveland.data` file is excluded, as this file is reportedly corrupt.
* `original_data/preprocess.py`: A Python script that converts the original data file format into Veritable-ready data and schema files; also produces a csv data file for convenience.
* `original_data/column_info.py`: A Python file containing the column names; used by `preprocess.py` to create `data.json` and `schema.json`.

# Dataset

The `combined.data` file contains the concatenation of the three original dataset files that are included in the `original_data` directory.

- 617 rows
- 75 columns
- some missing values
- all column types: boolean, categorical, real, and count
- target column is `target`: whether the patient developed heart disease

# Usage

    $ python heart_disease/run.py
    
# Example Output

    multinomial dataset, raw predictions: 41.9% test error
    multinomial dataset, binary transform: 21.0% test error
    binary dataset, raw predictions: 17.7% test error
