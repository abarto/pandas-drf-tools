pandas\_drf\_tools
==================

Introduction
------------

pandas-drf-tools is a set of viewsets, serializers and mixins to allow
using `Pandas <http://pandas.pydata.org/>`__ DataFrames with `Django
REST Framework <http://www.django-rest-framework.org/>`__ sites.

Installation
------------

The package can be installed using ``pip`` from
`PyPI <https://pypi.python.org/pypi>`__:

::

    $ pip install pandas-drf-tools

An you can also install it from source cloning the project's GitHub
repository:

::

    $ git clone git://github.com/abarto/pandas-drf-tools.git
    $ cd pandas-drf-tools
    $ python setup.py install

Usage
-----

How you use pandas-drf-tools depends on the level of integration you
need. The simplest use-case are regular DRF views that expose a
DataFrame. pandas-drf-tools provides several Serializers that turn a
DataFrame into its JSON representation using ``to_*`` methods in the
DataFrame API and a little bit of data processing. You can also parse
(and validate) data sent to the view into a DataFrame using the provided
Serializers. For example:

.. code:: python

    class DataFrameIndexSerializerTestView(views.APIView):
        def get_serializer_class(self):
            return DataFrameIndexSerializer

        def get(self, request, *args, **kwargs):
            sample = get_some_dataframe().sample(20)
            serializer = self.get_serializer_class()(sample)
            return response.Response(serializer.data)

        def post(self, request, *args, **kwargs):
            serializer = self.get_serializer_class()(data=request.data)
            serializer.is_valid(raise_exception=True)
            data_frame = serializer.validated_data
            data = {
                'columns': list(data_frame.columns),
                'len': len(data_frame)
            }
            return response.Response(data)

The ``APIView`` above uses ``DataFrameIndexSerializer`` to serialize the
DataFrame sample on the ``get`` method, and to de-serialize the request
payload on the ``post`` method. It also provide basic validation. Here's
the code for ``DataFrameIndexSerializer``:

.. code:: python

    class DataFrameIndexSerializer(Serializer):
        def to_internal_value(self, data):
            try:
                data_frame = pd.DataFrame.from_dict(data, orient='index').rename(index=int)
                return data_frame
            except ValueError as e:
                raise ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [str(e)]})

        def to_representation(self, instance):
            instance = instance.rename(index=str)
            return instance.to_dict(orient='index')

As you can see, the brunt of the work is done by ``DataFrame.to_dict``.
These are all the Serializers available:

-  DataFrameReadOnlyToDictRecordsSerializer: A read-only (it doesn't
   implement ``to_internal_value``) serializer that uses
   ``DataFrame.to_dict`` with ``records`` orientation.
-  DataFrameListSerializer: A serializer that uses ``DataFrame.to_dict``
   with ``list`` orientation for serialization and ``columns`` for
   de-serialization.
-  DataFrameIndexSerializer: A serializer that uses
   ``DataFrame.to_dict`` with ``index`` orientation for serialization
   and de-serialization. Due to the restrictions imposed on keys by the
   JSON format, the index is converted to ``str`` on serialization and
   to ``int`` on deseralization.
-  DataFrameRecordsSerializer: A serializer that uses
   ``DataFrame.to_records`` for serialization and
   ``DataFrame.from_records`` de-serialization.

Besides serializers, pandas-drf-tools also provides a
``GenericDataFrameAPIView`` to expose a DataFrame using a view, the same
way DRF's ``GenericAPIView`` does it with Django's querysets. This class
will rarely be used directly. Same as with DRF, pandas-drf-tools also
provides a ``GenericDataFrameViewSet`` class that, combined with custom
list, retrieve, create, and update mixins turn into ``DataFrameViewSet``
(and ``ReadOnlyDataFrameViewSet``) which mimics the behaviour of
``ModelViewSet``.

Instead of setting a ``queryset`` field of overriding ``get_queryset``,
users of ``DataFrameViewSet`` need to set a ``dataframe`` field or
override the ``get_dataframe`` method. Another difference is that, by
default, write operations do not change the original dataframe. The
``create``, ``update``, and ``destroy`` methods defined in the mixins
return a **new** DataFrame based on the one set by ``get_dataframe``. In
order to give the users the chance of doing something with the new
DataFrame, we provide an ``update_dataframe`` callback that is called
whenever a write operation is called. Take a look at the
``CreateDataFrameMixin`` class:

.. code:: python

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

We call ``append`` on the original dataframe and we pass the result onto
``update_dataframe``. The default behaviour of ``update_dataframe`` is
just returning whatever was passed onto it, so all operations are
basically read-only. Here's an example of how to integrate all the
components:

.. code:: python

    import pandas as pd

    class TestDataFrameViewSet(DataFrameViewSet):
        serializer_class = DataFrameRecordsSerializer

        def get_dataframe(self):
            return pd.read_pickle('test.pkl')

        def update_dataframe(self, dataframe):
            dataframe.read_pickle('test.pkl')
            return dataframe

This viewset can then be used the same way as regular DRF viewset. For
instance, we could use a router:

.. code:: python

    from rest_framework.routers import DefaultRouter

    router = DefaultRouter()
    router.register(r'test', TestDataFrameViewSet, base_name='test')

The only caveat is that, since there's no queryset (nor model)
associated with the viewset, DRF cannot guess the base name, so it has
to be set explicitly.

That's everything you need. Now you API is ready to receive regular REST
calls (POST for create, PUT for update, etc.) that will read or change
the DataFrame.

Whenever possible, I followed DRF's existing architecture so most things
should feel natural if you already have experience with the framework.

Example
-------

A complete example that uses the US Census Data is available on
`GitHub <https://github.com/abarto/pandas-drf-tools-test>`__.

What's missing?
---------------

-  No unit tests. Although the package is fully functional, I wouldn't
   use it in any production environment yet as I haven't had time to
   fully test it just.
-  No validation. The serializers just use pandas' methods without
   checking payload thoroughly. I'm still looking for ways on improving
   this, probably using the columns dtypes to validate each serialized
   cell.
-  No filtering backends. If you need filtering, you can override the
   ``filter_dataframe`` method, which is does the same as the
   ``filter_queryset`` method. I'm planning on implementing some filters
   (like the ``SearchFilter``) to provide guidance if you want to build
   your own.
-  No page pagination. Only ``LimitOffsetPagination`` is provided.
-  Proper documentation.

Feedback
--------

Comments, tickets and pull requests are welcomed. I'll allocate time to
this project based on the community's interest on it. You can also hit
me up on Twitter at `@m4rgin4l <https://twitter.com/m4rgin4l>`__ if you
have specific questions.
