from z3c.form.field import Fields
from plone.z3cform.fieldsets.utils import find_source
from plone.z3cform.fieldsets.group import GroupFactory


def add(form, *args, **kwargs):
    """Add one or more fields. Keyword argument 'index' can be used to
    specify an index to insert at. Keyword argument 'group' can be used
    to specify the label of a group, which will be found and used or
    created if it doesn't exist.
    """
    index = kwargs.pop('index', None)
    group = kwargs.pop('group', None)

    new_fields = Fields(*args, **kwargs)

    if not group or isinstance(group, basestring):
        source = find_source(form, group=group)
    else:
        source = group

    if source is None and group:
        source = GroupFactory(group, new_fields)
        #form.groups.append(source)
        # MAKE sure groups is a new list on the instance and not the class
        form.groups += (source, )
    else:
        if index is None or index >= len(source.fields):
            source.fields += new_fields
        else:
            field_names = source.fields.keys()
            source.fields = source.fields.select(*field_names[:index]) + \
                            new_fields + \
                            source.fields.select(*field_names[index:])


def patchExtensibleForm(klass, original, replacement):
    klass.groups = ()
