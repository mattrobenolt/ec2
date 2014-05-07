"""
ec2.helpers
~~~~~~~~~~~

:copyright: (c) 2014 by Matt Robenolt.
:license: BSD, see LICENSE for more details.
"""

import re


def make_compare(key, value, obj):
    "Map a key name to a specific comparison function"
    if '__' not in key:
        # If no __ exists, default to doing an "exact" comparison
        key, comp = key, 'exact'
    else:
        key, comp = key.rsplit('__', 1)
    # Check if comp is valid
    if hasattr(Compare, comp):
        return getattr(Compare, comp)(key, value, obj)
    raise AttributeError("No comparison '%s'" % comp)


class Compare(object):
    "Private class, namespacing comparison functions."

    @staticmethod
    def exact(key, value, obj):
        try:
            return getattr(obj, key) == value
        except AttributeError:
            # Fall back to checking tags
            if hasattr(obj, 'tags'):
                for tag in obj.tags:
                    if key == tag.lower():
                        return obj.tags[tag] == value
            # There is no tag found either
            return False

    @staticmethod
    def iexact(key, value, obj):
        value = value.lower()
        try:
            return getattr(obj, key).lower() == value
        except AttributeError:
            # Fall back to checking tags
            if hasattr(obj, 'tags'):
                for tag in obj.tags:
                    if key == tag.lower():
                        return obj.tags[tag].lower() == value
            # There is no tag found either
            return False

    @staticmethod
    def like(key, value, obj):
        if isinstance(value, basestring):
            # If a string is passed in,
            # we want to convert it to a pattern object
            value = re.compile(value)
        try:
            return bool(value.match(getattr(obj, key)))
        except AttributeError:
            # Fall back to checking tags
            if hasattr(obj, 'tags'):
                for tag in obj.tags:
                    if key == tag.lower():
                        return bool(value.match(obj.tags[tag]))
            # There is no tag found either
            return False
    # Django alias
    regex = like

    @staticmethod
    def ilike(key, value, obj):
        return Compare.like(key, re.compile(value, re.I), obj)
    # Django alias
    iregex = ilike

    @staticmethod
    def contains(key, value, obj):
        try:
            return value in getattr(obj, key)
        except AttributeError:
            # Fall back to checking tags
            if hasattr(obj, 'tags'):
                for tag in obj.tags:
                    if key == tag.lower():
                        return value in obj.tags[tag]
            # There is no tag found either
            return False

    @staticmethod
    def icontains(key, value, obj):
        value = value.lower()
        try:
            return value in getattr(obj, key).lower()
        except AttributeError:
            # Fall back to checking tags
            if hasattr(obj, 'tags'):
                for tag in obj.tags:
                    if key == tag.lower():
                        return value in obj.tags[tag]
            # There is no tag found either
            return False

    @staticmethod
    def startswith(key, value, obj):
        try:
            return getattr(obj, key).startswith(value)
        except AttributeError:
            # Fall back to checking tags
            if hasattr(obj, 'tags'):
                for tag in obj.tags:
                    if key == tag.lower():
                        return obj.tags[tag].startswith(value)
            # There is no tag found either
            return False

    @staticmethod
    def istartswith(key, value, obj):
        value = value.lower()
        try:
            return getattr(obj, key).startswith(value)
        except AttributeError:
            # Fall back to checking tags
            if hasattr(obj, 'tags'):
                for tag in obj.tags:
                    if key == tag.lower():
                        return obj.tags[tag].lower().startswith(value)
            # There is no tag found either
            return False

    @staticmethod
    def endswith(key, value, obj):
        try:
            return getattr(obj, key).endswith(value)
        except AttributeError:
            # Fall back to checking tags
            if hasattr(obj, 'tags'):
                for tag in obj.tags:
                    if key == tag.lower():
                        return obj.tags[tag].endswith(value)
            # There is no tag found either
            return False

    @staticmethod
    def iendswith(key, value, obj):
        value = value.lower()
        try:
            return getattr(obj, key).endswith(value)
        except AttributeError:
            # Fall back to checking tags
            if hasattr(obj, 'tags'):
                for tag in obj.tags:
                    if key == tag.lower():
                        return obj.tags[tag].lower().endswith(value)
            # There is no tag found either
            return False

    @staticmethod
    def isnull(key, value, obj):
        try:
            return (getattr(obj, key) is None) == value
        except AttributeError:
            # Fall back to checking tags
            if hasattr(obj, 'tags'):
                for tag in obj.tags:
                    if key == tag.lower():
                        return (obj.tags[tag] is None) and value
            # There is no tag found either, so must be null
            return True and value
