from rest_framework.viewsets import ViewSetMixin

from pandas_drf_tools import generics, mixins


class GenericDataFrameViewSet(ViewSetMixin, generics.GenericDataFrameAPIView):
    """
    The GenericDataFrameViewSet class does not provide any actions by default,
    but does include the base set of generic view behavior, such as
    the `get_object` and `get_dataframe` methods.
    """
    pass


class ReadOnlyDataFrameViewSet(mixins.RetrieveDataFrameMixin,
                               mixins.ListDataFrameMixin,
                               GenericDataFrameViewSet):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """
    pass


class DataFrameViewSet(mixins.CreateDataFrameMixin,
                       mixins.RetrieveDataFrameMixin,
                       mixins.UpdateDataFrameMixin,
                       mixins.DestroyDataFrameMixin,
                       mixins.ListDataFrameMixin,
                       GenericDataFrameViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass
