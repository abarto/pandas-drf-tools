import pandas as pd

from collections import OrderedDict

from rest_framework.serializers import (CharField, JSONField, ListField, Serializer,
                                        ValidationError, api_settings)


class DataFrameReadOnlyToDictRecordsSerializer(Serializer):
    """
    A read-only Serializer implementation that uses
    :func:`pandas.DataFrame.to_dict <pandas.DataFrame.to_dict>` to convert data to external
    representation with 'records' orientation. This serializer is useful when a list of dictionaries
    is required.
    """
    def to_internal_value(self, data):
        raise NotImplementedError('`to_representation()` must be implemented.')

    def to_representation(self, instance):
        return {'records': instance.to_dict(orient='records')}


class DataFrameListSerializer(Serializer):
    """
    A Serializer implementation that uses
    :func:`pandas.DataFrame.from_dict <pandas.DataFrame.from_dict>` and
    :func:`pandas.DataFrame.to_dict <pandas.DataFrame.to_dict>` to convert data to internal value
    and to external representation with orientation 'columns' and 'list'.
    """
    def to_internal_value(self, data):
        try:
            return pd.DataFrame.from_dict(data, orient='columns')
        except ValueError as e:
            raise ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [str(e)]})

    def to_representation(self, instance):
        return instance.to_dict(orient='list')


class DataFrameIndexSerializer(Serializer):
    """
    A Serializer implementation that uses
    :func:`pandas.DataFrame.from_dict <pandas.DataFrame.from_dict>` and
    :func:`pandas.DataFrame.to_dict <pandas.DataFrame.to_dict>` to convert data to internal value
    and to external representation with orientation 'index'.
    """
    def to_internal_value(self, data):
        try:
            data_frame = pd.DataFrame.from_dict(data, orient='index').rename(index=int)
            return data_frame
        except ValueError as e:
            raise ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [str(e)]})

    def to_representation(self, instance):
        instance = instance.rename(index=str)
        return instance.to_dict(orient='index')


class DataFrameRecordsSerializer(Serializer):
    """
    A Serializer implementation that uses
    :func:`pandas.DataFrame.from_dict <pandas.DataFrame.from_records>` and
    :func:`pandas.DataFrame.to_dict <pandas.DataFrame.to_records>` to convert data to internal
    value and to external representation.
    """
    columns = ListField(child=CharField())
    data = ListField(child=JSONField())

    def to_internal_value(self, data):
        validated_data = super().to_internal_value(data)

        try:
            data_frame = pd.DataFrame.from_records(validated_data['data'], index='index',
                                                   columns=validated_data['columns'])
            return data_frame
        except ValueError as e:
            raise ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [str(e)]})

    def to_representation(self, instance):
        recarray = instance.to_records(index=True)
        return OrderedDict([('columns', recarray.dtype.names), ('data', recarray.tolist())])
