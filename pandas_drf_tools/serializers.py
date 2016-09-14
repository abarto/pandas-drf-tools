import pandas as pd

from rest_framework.serializers import Serializer


class DataFrameDictSerializer(Serializer):
    """
    A Serializer implementation that uses :func:`pandas.DataFrame.from_dict <pandas.DataFrame.from_dict>` and
    :func:`pandas.DataFrame.to_dict <pandas.DataFrame.to_dict>` to convert data to internal value and to
    external representation.
    """
    def to_internal_value(self, data):
        return pd.DataFrame.from_dict(data, orient='columns')

    def to_representation(self, instance):
        return instance.to_dict(orient='list')
