from django.http import Http404

from rest_framework.views import APIView

from pandas_drf_tools import mixins


class GenericDataFrameAPIView(APIView):
    """Base class for all other generic DataFrame views. It is based on GenericAPIView."""
    # You'll need to either set these attributes,
    # or override `get_dataframe()`/`get_serializer_class()`.
    # If you are overriding a view method, it is important that you call
    # `get_dataframe()` instead of accessing the `dataframe` property directly,
    # as `dataframe` will get evaluated only once, and those results are cached
    # for all subsequent requests.
    dataframe = None
    serializer_class = None

    # If you want to use object lookups other than index, set 'lookup_url_kwarg'.
    # For more complex lookup requirements override `get_object()`.
    lookup_url_kwarg = 'index'

    # The style to use for dataframe pagination.
    pagination_class = None

    def get_dataframe(self):
        """
        Get the DataFrame for this view.
        Defaults to using `self.dataframe`.

        This method should always be used rather than accessing `self.dataframe`
        directly, as `self.dataframe` gets evaluated only once, and those results
        are cached for all subsequent requests.

        You may want to override this if you need to provide different
        dataframes depending on the incoming request.
        """
        assert self.dataframe is not None, (
            "'%s' should either include a `dataframe` attribute, "
            "or override the `get_dataframe()` method."
            % self.__class__.__name__
        )

        dataframe = self.dataframe
        return dataframe

    def update_dataframe(self, dataframe):
        """
        Indicates that the dataframe needs to be updated. The default implementation
        just returns the argument. This method has to be ovewritten to make changing
        operations stick.
        """
        return dataframe

    def index_row(self, dataframe):
        """
        Indexes the row based on the request parameters.
        """
        return dataframe.loc[self.kwargs[self.lookup_url_kwarg]].to_frame().T

    def get_object(self):
        """
        Returns the row the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        dataframe = self.filter_dataframe(self.get_dataframe())

        assert self.lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, self.lookup_url_kwarg)
        )

        try:
            obj = self.index_row(dataframe)
        except (IndexError, KeyError, ValueError):
            raise Http404

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )

        return self.serializer_class

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def filter_dataframe(self, dataframe):
        """
        Given a dataframe, filter it.
        """
        return dataframe

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_dataframe(self, dataframe):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_dataframe(dataframe, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


# Concrete view classes that provide method handlers
# by composing the mixin classes with the base view.

class CreateAPIView(mixins.CreateDataFrameMixin,
                    GenericDataFrameAPIView):
    """
    Concrete view for creating a model instance.
    """
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListAPIView(mixins.ListDataFrameMixin,
                  GenericDataFrameAPIView):
    """
    Concrete view for listing a queryset.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RetrieveAPIView(mixins.RetrieveDataFrameMixin,
                      GenericDataFrameAPIView):
    """
    Concrete view for retrieving a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class DestroyAPIView(mixins.DestroyDataFrameMixin,
                     GenericDataFrameAPIView):
    """
    Concrete view for deleting a model instance.
    """
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UpdateAPIView(mixins.UpdateDataFrameMixin,
                    GenericDataFrameAPIView):
    """
    Concrete view for updating a model instance.
    """
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ListCreateAPIView(mixins.ListDataFrameMixin,
                        mixins.CreateDataFrameMixin,
                        GenericDataFrameAPIView):
    """
    Concrete view for listing a queryset or creating a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RetrieveUpdateAPIView(mixins.RetrieveDataFrameMixin,
                            mixins.UpdateDataFrameMixin,
                            GenericDataFrameAPIView):
    """
    Concrete view for retrieving, updating a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RetrieveDestroyAPIView(mixins.RetrieveDataFrameMixin,
                             mixins.DestroyDataFrameMixin,
                             GenericDataFrameAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(mixins.RetrieveDataFrameMixin,
                                   mixins.UpdateDataFrameMixin,
                                   mixins.DestroyDataFrameMixin,
                                   GenericDataFrameAPIView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
