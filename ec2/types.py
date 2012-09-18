from ec2.connection import get_connection
from ec2.helpers import make_compare
from ec2.base import objects_base

class instances(objects_base):
    """Singleten to stem off queries for instances"""

    @classmethod
    def _all(cls):
        """
        Grab all AWS instances and cache them for future filters

        >>> ec2.instances.all()
        [ ... ]
        """
        return [i for r in get_connection().get_all_instances() for i in r.instances]

    @classmethod
    def filter(cls, **kwargs):
        """
        The meat. Filter instances using Django model style syntax.

        All kwargs are translated into attributes on instance objects.
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

        >>> ec2.instances.filter(state='running', name__startswith='production')
        [ ... ]
        """
        instances = cls.all()
        for key in kwargs:
            instances = filter(lambda i: make_compare(key, kwargs[key], i), instances)
        return instances


class security_groups(objects_base):
    @classmethod
    def all(cls):
        if not hasattr(cls, '_cache'):
            cls._cache = get_connection().get_all_security_groups()
        return cls._cache

    @classmethod
    def filter(cls, **kwargs):
        groups = cls.all()
        for key in kwargs:
            groups = filter(lambda i: make_compare(key, kwargs[key], i), groups)
        return groups
