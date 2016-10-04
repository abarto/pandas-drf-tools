"""
Basic building blocks for generic class based views.

We don't bind behaviour to http method handlers yet,
which allows mixin classes to be composed in interesting ways.
"""
from __future__ import unicode_literals

from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings


class CreateDataFrameMixin(object):
    """
    Adds a row to the dataframe.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        dataframe = self.get_dataframe()
        return self.update_dataframe(dataframe.append(serializer.validated_data))

    def get_success_headers(self, data):
        try:
            return {'Location': data[api_settings.URL_FIELD_NAME]}
        except (TypeError, KeyError):
            return {}


class ListDataFrameMixin(object):
    """
    List the contents of a dataframe.
    """
    def list(self, request, *args, **kwargs):
        dataframe = self.filter_dataframe(self.get_dataframe())

        page = self.paginate_dataframe(dataframe)
        if page is not None:
            serializer = self.get_serializer(page)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(dataframe)
        return Response(serializer.data)


class RetrieveDataFrameMixin(object):
    """
    Retrieve a dataframe row.
    """
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UpdateDataFrameMixin(object):
    """
    Update a dataframe row.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(instance, serializer)
        return Response(serializer.data)

    def perform_update(self, instance, serializer):
        validated_data = serializer.validated_data
        instance.ix[validated_data.index, validated_data.columns] = validated_data[:]
        dataframe = self.get_dataframe()
        dataframe.ix[instance.index] = instance
        return self.update_dataframe(dataframe)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class DestroyDataFrameMixin(object):
    """
    Destroy a dataframe row.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        dataframe = self.get_dataframe()
        return self.update_dataframe(dataframe.drop(instance.index))
