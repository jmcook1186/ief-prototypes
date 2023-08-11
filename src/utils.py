import pandas as pd
import numpy as np
import warnings


def lookup_number(value, data, filter, target):
    """
    this function looks up numeric values in the aws dataframe
    it returns the value from the `target` column where the entry in the `filter` column matches `value`.
    If there is more than one value in the `filter` matching the given `value`, then the int(mean) of the retrieved values is returned.
    If `value` yields no valid values, the most common value in `target` is returned
    A warning is emitted in the latter case.
    """
    result = pd.to_numeric(data[data[filter] == value][target].values)
    if len(result) == 0 or result == None:
        # there are invalid entries in the original data that contain multiple commas separated values where there should be one int.
        # let's filter them out
        filtered_data = pd.to_numeric(
            data[target][data[target].astype("str").str.contains(",") == False].values
        )
        # now we'll use the most common value as a stand in for our missing data
        vals, counts = np.unique(filtered_data, return_counts=True)
        warnings.warn(
            "{} not recognized, using most common value for {} from all {} in database".format(
                value, target, filter
            )
        )
        return vals[np.argmax(counts)]
    else:
        return int(result.mean())
