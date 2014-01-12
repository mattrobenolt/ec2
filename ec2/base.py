"""
ec2.base
~~~~~~~~

:copyright: (c) 2014 by Matt Robenolt.
:license: BSD, see LICENSE for more details.
"""

from ec2.helpers import make_compare


class _EC2MetaClass(type):
    "Metaclass for all EC2 filter type classes"

    def __new__(cls, name, bases, attrs):
        # Append MultipleObjectsReturned and DoesNotExist exceptions
        for contrib in ('MultipleObjectsReturned', 'DoesNotExist'):
            attrs[contrib] = type(contrib, (Exception,), {})
        return super(_EC2MetaClass, cls).__new__(cls, name, bases, attrs)


class objects_base(object):
    "Base class for all EC2 filter type classes"

    __metaclass__ = _EC2MetaClass

    @classmethod
    def all(cls):
        """
        Wrapper around _all() to cache and return all results of something

        >>> ec2.instances.all()
        [ ... ]
        """
        if not hasattr(cls, '_cache'):
            cls._cache = cls._all()
        return cls._cache

    @classmethod
    def get(cls, **kwargs):
        """
        Generic get() for one item only

        >>> ec2.instances.get(name='production-web-01')
        <Instance: ...>
        """
        things = cls.filter(**kwargs)
        if len(things) > 1:
            # Raise an exception if more than one object is matched
            raise cls.MultipleObjectsReturned
        elif len(things) == 0:
            # Rase an exception if no objects were matched
            raise cls.DoesNotExist
        return things[0]

    @classmethod
    def filter(cls, **kwargs):
        """
        The meat. Filtering using Django model style syntax.

        All kwargs are translated into attributes on the underlying objects.
        If the attribute is not found, it looks for a similar key
        in the tags.

        There are a couple comparisons to check against as well:
            exact: check strict equality
            iexact: case insensitive exact
            like: check against regular expression
            ilike: case insensitive like
            contains: check if string is found with attribute
            icontains: case insensitive contains
            startswith: check if attribute value starts with the string
            istartswith: case insensitive startswith
            endswith: check if attribute value ends with the string
            iendswith: case insensitive startswith
            isnull: check if the attribute does not exist

        >>> ec2.instances.filter(name__startswith='production')
        [ ... ]
        """
        qs = cls.all()
        for key in kwargs:
            qs = filter(lambda i: make_compare(key, kwargs[key], i), qs)
        return qs

    @classmethod
    def clear(cls):
        "Clear the cached instances"
        try:
            del cls._cache
        except AttributeError:
            pass
