import re

def make_compare(key, value, instance):
    "Map a key name to a specific comparison function"
    if '__' not in key:
        # If no __ exists, default to doing an "exact" comparison
        key, comp = key, 'exact'
    else:
        key, comp = key.rsplit('__', 1)
    # Check if comp is valid
    if hasattr(Compare, comp):
        return getattr(Compare, comp)(key, value, instance)
    raise AttributeError("No comparison '%s'" % comp)


class Compare(object):
    "Private class, namespacing comparison functions."

    @staticmethod
    def exact(key, value, instance):
        try:
            return getattr(instance, key) == value
        except AttributeError, e:
            # Fall back to checking tags
            if hasattr(instance, 'tags'):
                for tag in instance.tags:
                    if key == tag.lower():
                        return instance.tags[tag] == value
            # There is no tag found either
            raise e

    @staticmethod
    def iexact(key, value, instance):
        value = value.lower()
        try:
            return getattr(instance, key).lower() == value
        except AttributeError, e:
            # Fall back to checking tags
            if hasattr(instance, 'tags'):
                for tag in instance.tags:
                    if key == tag.lower():
                        return instance.tags[tag].lower() == value
            # There is no tag found either
            raise e

    @staticmethod
    def like(key, value, instance):
        if isinstance(value, basestring):
            # If a string is passed in, we want to convert it to a pattern object
            value = re.compile(value)
        try:
            return bool(value.match(getattr(instance, key)))
        except AttributeError, e:
            # Fall back to checking tags
            if hasattr(instance, 'tags'):
                for tag in instance.tags:
                    if key == tag.lower():
                        return bool(value.match(instance.tags[tag]))
            # There is no tag found either
            raise e
    # Django alias
    regex = like

    @staticmethod
    def ilike(key, value, instance):
        return Compare.like(key, re.compile(value, re.I), instance)
    # Django alias
    iregex = ilike

    @staticmethod
    def contains(key, value, instance):
        try:
            return value in getattr(instance, key)
        except AttributeError, e:
            # Fall back to checking tags
            if hasattr(instance, 'tags'):
                for tag in instance.tags:
                    if key == tag.lower():
                        return value in instance.tags[tag]
            # There is no tag found either
            raise e

    @staticmethod
    def icontains(key, value, instance):
        value = value.lower()
        try:
            return value in getattr(instance, key).lower()
        except AttributeError, e:
            # Fall back to checking tags
            if hasattr(instance, 'tags'):
                for tag in instance.tags:
                    if key == tag.lower():
                        return value in instance.tags[tag]
            # There is no tag found either
            raise e

    @staticmethod
    def startswith(key, value, instance):
        try:
            return getattr(instance, key).startswith(value)
        except AttributeError, e:
            # Fall back to checking tags
            if hasattr(instance, 'tags'):
                for tag in instance.tags:
                    if key == tag.lower():
                        return instance.tags[tag].startswith(value)
            # There is no tag found either
            raise e

    @staticmethod
    def istartswith(key, value, instance):
        value = value.lower()
        try:
            return getattr(instance, key).startswith(value)
        except AttributeError, e:
            # Fall back to checking tags
            if hasattr(instance, 'tags'):
                for tag in instance.tags:
                    if key == tag.lower():
                        return instance.tags[tag].lower().startswith(value)
            # There is no tag found either
            raise e

    @staticmethod
    def endswith(key, value, instance):
        try:
            return getattr(instance, key).endswith(value)
        except AttributeError, e:
            # Fall back to checking tags
            if hasattr(instance, 'tags'):
                for tag in instance.tags:
                    if key == tag.lower():
                        return instance.tags[tag].endswith(value)
            # There is no tag found either
            raise e

    @staticmethod
    def iendswith(key, value, instance):
        value = value.lower()
        try:
            return getattr(instance, key).endswith(value)
        except AttributeError, e:
            # Fall back to checking tags
            if hasattr(instance, 'tags'):
                for tag in instance.tags:
                    if key == tag.lower():
                        return instance.tags[tag].lower().endswith(value)
            # There is no tag found either
            raise e