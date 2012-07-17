import veritable
import json
import sys
import os
from copy import deepcopy
from veritable.utils import (clean_data, split_rows, clean_predictions)
from veritable.exceptions import VeritableError
from collections import Counter

DATA_FILE = os.path.join(os.path.dirname(__file__),'data.json')
SCHEMA_FILE = os.path.join(os.path.dirname(__file__),'schema.json')
VERITABLE_API_KEY = os.getenv('VERITABLE_API_KEY')
PRED_COUNT = 100
TABLE_ID = 'heart-disease-example'

def main():
    API = veritable.connect(ssl_verify=False)

    print("Loading and preparing data...")
    # load the data and schema describing all column datatypes
    with open(DATA_FILE, 'rb') as fd:
        data = json.loads(fd.read())

    with open(SCHEMA_FILE, 'rb') as fd:
        master_schema = json.loads(fd.read())

    # divide the data into a training and test set, and ensure data is
    # of the correct type for each column
    train_data, test_data = split_rows(data, .8)
    clean_data(train_data, master_schema, remove_extra_fields=True,
        assign_ids=True)

    # we have to account for the possibility that the training data doesn't
    # contain all of the columns in the master schema
    schema = subset_schema(master_schema, train_data)

    # use the subset of the schema to clean the test data - make sure we don't
    # condition test predictions on columns or categorical values that aren't
    # present in the training data
    clean_data(test_data, schema, remove_extra_fields=True, assign_ids=True)
    validate_test_categoricals(test_data, train_data, schema)

    # we'll run the analysis twice: one with the original multinomial target
    # column, and once converting it to a binary column
    def binary_transform(x):
        transform = {'0': False, '1': True, '2': True, '3': True, '4': True}
        return transform[x]

    # make the binary dataset and schema
    binary_train_data = deepcopy(train_data)
    binary_test_data = deepcopy(test_data)
    binary_schema = deepcopy(schema)
    binary_schema['target']['type'] = 'boolean'
    for d in (binary_train_data, binary_test_data):
        for r in d:
            if 'target' in r:
                r['target'] = binary_transform(r['target'])

    # delete existing tables if present
    if API.table_exists(TABLE_ID):
        print("Deleting old table '%s'" %TABLE_ID)
        API.delete_table(TABLE_ID)
    if API.table_exists(TABLE_ID+"-binary"):
        print("Deleting old table '%s'" %(TABLE_ID+"-binary"))
        API.delete_table(TABLE_ID+"-binary")

    # upload the data and start the analyses
    print("Uploading data and running analyses...")
    table = API.create_table(TABLE_ID)
    table.batch_upload_rows(train_data)
    analysis = table.create_analysis(schema)

    binary_table = API.create_table(TABLE_ID+"-binary")
    binary_table.batch_upload_rows(binary_train_data)
    binary_analysis = binary_table.create_analysis(binary_schema)

    # now we'll make predictions for each test row, collecting the
    # predicted values for the target column
    analysis.wait()
    print("Making predictions....")
    results = predict_known_target_column(test_data, analysis, schema,
        'target')

    # and for the binary table
    binary_analysis.wait()
    binary_results = predict_known_target_column(binary_test_data,
        binary_analysis, binary_schema, 'target')

    # summarize the results
    print("multinomial dataset, raw predictions: " \
    "{0}% test error".format(test_error(results, 'target') * 100))
    print("multinomial dataset, binary transform: " \
    "{0}% test error".format(test_error(results, 'target',
        transform=binary_transform) * 100))
    print("binary dataset, raw predictions: " \
    "{0}% test error".format(test_error(binary_results, 'target') * 100))


def subset_schema(master, data):
    # returns a new schema with only those columns that appear in the data
    cols = set()
    for r in data:
        cols = cols.union(set(r.keys()))
    schema = {}
    for col in cols:
        if not col == '_id':
            schema[col] = master[col]
    return schema


def predict_known_target_column(data, analysis, schema, target):
    # make predictions for each row of a test dataset, for some known target
    # columns, and collect one dict for each row contining the actual value
    # and the predictions object
    results = []
    rows = [row for row in deepcopy(data) if target in row]
    prediction_requests = deepcopy(rows)    
    clean_predictions(prediction_requests, schema)
    for prediction_request in prediction_requests:
        prediction_request[target] = None
    prediction_results = list(analysis.batch_predict(prediction_requests))
    results = []
    for i in range(len(prediction_requests)):
        result = {'actual': rows[i][target],
                  'predicted': prediction_results[i]}
        results.append(result)
    return results


def test_error(results, target, transform=lambda x: x,
               uncertainty=1):
    # use the output of predict_known_target_column to calculate the
    # proportion of incorrect predictions, subject to some transform, for
    # predictions with uncertainty below some threshold, for a target column
    t = 0
    f = 0
    for r in results:
        if r['predicted'].uncertainty[target] < uncertainty:
            if transform(r['predicted'][target]) == transform(r['actual']):
                t += 1
            else:
                f += 1
    if (t + f) > 0:
        return 1 - float(t) / (t + f)
    else:
        return None

def validate_test_categoricals(test, train, schema):
    # check that test contains no categorical values that do not appear in
    # train, and remove any if found
    for col in schema.keys():
        if schema[col]['type'] == "categorical":
            vals = set()
            for r in train:
                if col in r:
                    vals.add(r[col])
            for r in test:
                if col in r:
                    if r[col] not in vals:
                        del r[col]


if __name__ == '__main__':
    main()
