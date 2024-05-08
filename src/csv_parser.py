from io import StringIO
import csv

def arr_to_csv(arr:list[dict], write_headers=False, delimiter=','):
    keys = arr[0].keys()
    keys = sorted(keys)
    file = StringIO()
    dict_writer = csv.DictWriter(file, keys, delimiter=delimiter)
    if write_headers:
        dict_writer.writeheader()
    dict_writer.writerows(arr)
    return file.getvalue()