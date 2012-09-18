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
    def clear(cls):
        "Clear the cached instances"
        try:
            del cls._cache
        except AttributeError:
            pass
