def join_bsddb(data_file, data_file_key_column, lookup_file, lookup_file_key_column, separator, print_all=True, bsddb=None):
    """
Join two files with the given key columns and separator. Read the lookup file in
fully to create a lookup table. Then iterate through the data file and if the
key column from data_file is found in the lookup table, then output a line for
each match in the lookup table. The columns output will be the join field, all
the columns from data_file followed by all the columns from lookup_file.

An iterator is returned. Each line does not have a trailing newline
"""
    lookup_table = bsddb.btopen(None, "c")
    for line in lookup_file:
        lookup_fields = line.rstrip("\n").split(separator)
        key = lookup_fields.pop(lookup_file_key_column).encode('utf8')
        lookup_table[key] = separator.join(lookup_fields).encode('utf8')

    for line in data_file:
        data_fields = line.rstrip("\n").split(separator)
        key_decoded = data_fields.pop(data_file_key_column)
        key = key_decoded.encode('utf8')

        if key not in lookup_table:
            if print_all:
                yield separator.join([key_decoded] + data_fields)
            continue

        (_key, value) = lookup_table.set_location(key)
        while key == _key:
            yield separator.join([key_decoded] + data_fields + [value.decode('utf8')])
            try:
                (_key, value) = lookup_table.next()
            except bsddb.db.DBNotFoundError:
                (_key, value) = (None, None)

    lookup_table.close()

def join_dict(data_file, data_file_key_column, lookup_file, lookup_file_key_column, separator, print_all=True):
    """
Join two files with the given key columns and separator. Read the lookup file in
fully to create a lookup table. Then iterate through the data file and if the
key column from data_file is found in the lookup table, then output a line for
each match in the lookup table. The columns output will be the join field, all
the columns from data_file followed by all the columns from lookup_file.

An iterator is returned. Each line does not have a trailing newline
"""

    from collections import defaultdict

    lookup_table = defaultdict(list)
    for line in lookup_file:
        lookup_fields = line.rstrip("\n").split(separator)
        key = lookup_fields.pop(lookup_file_key_column)
        lookup_table[key].append(lookup_fields)

    for line in data_file:
        data_fields = line.rstrip("\n").split(separator)
        key = data_fields.pop(data_file_key_column)
        if key not in lookup_table:
            if print_all:
                yield separator.join([key] + data_fields)
            continue

        for value in lookup_table[key]:
            yield separator.join([key] + data_fields + (value if value != [] else ['']))
