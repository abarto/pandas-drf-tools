import pandas as pd

from rest_framework.serializers import Serializer


class DataFrameDictSerializer(Serializer):
    def __init__(self, *args, from_dict_kwargs={}, to_dict_kwargs={}, **kwargs):
        """
        A Serializer implementation that uses :func:`pandas.DataFrame.from_dict <pandas.DataFrame.from_dict>` and
        :func:`pandas.DataFrame.to_dict <pandas.DataFrame.to_dict>` to convert data to internal value and to
        external representation.
        :param args: Positional arguments for :func:`rest_framework.serializers.Serializer.__init__ <rest_framework.serializers.Serializer.__init__>`
        :param from_dict_kwargs: Keyword arguments for :func:`pandas.DataFrame.from_dict <pandas.DataFrame.from_dict>`
        :param to_dict_kwargs: Keyword arguments for :func:`pandas.DataFrame.from_dict <pandas.DataFrame.to_dict>`
        :param kwargs: Keyword arguments for :func:`rest_framework.serializers.Serializer.__init__ <rest_framework.serializers.Serializer.__init__>`
        """
        super().__init__(*args, **kwargs)
        self._from_dict_kwargs = from_dict_kwargs
        self._to_dict_kwargs = to_dict_kwargs

    def to_internal_value(self, data):
        return pd.DataFrame.from_dict(data, **self._from_dict_kwargs)

    def to_representation(self, instance):
        return instance.to_dict(**self._to_dict_kwargs)
