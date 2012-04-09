import sys
import csv
import json
from column_info import COLUMN_INFO


def main(filename):
    column_names = [c['name'] for c in COLUMN_INFO]
    
    with open(filename, 'rb') as fd:
        rd = csv.reader(fd, delimiter=' ')

        rows = []
        row_data = []
        for line in rd:
            if len(line) == 0:
                continue
            
            # Missing values are coded as -9 in the original data
            row_data += [None if (x == "-9" or x == "-9.") else x for x in line]

            # Individual records span several lines in the original data, with each 
            # record terminated by a field containing the string "name"
            if line[-1] == 'name':
                rows.append(dict([(column, value) 
                    for column, value in zip(column_names, row_data)]))
                row_data = []
        
    # write data to json
    with open('data.json', 'wb') as fd:
        fd.write(json.dumps(rows, indent=2))
    
    # write data to csv
    with open('data.csv', 'wb') as fd:
        wr = csv.writer(fd, delimiter=',')
        wr.writerow(column_names)
        for row in rows:
            row_list = [row[column] for column in column_names]
            wr.writerow(row_list)
    
    # write schema to json
    schema = {}
    for column in COLUMN_INFO:
        if 'type' in column:
            schema[column['name']] = {'type': column['type']}
    with open('schema.json', 'wb') as fd:
        fd.write(json.dumps(schema, indent=2))


if __name__ == '__main__':
    main(sys.argv[1])
    