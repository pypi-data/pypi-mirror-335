class AnnotatedType:
    """
    Enables metadata injection using square brackets ([]) on class types.
    Inherit this class to use metadata annotations with `[]`.
    """
    def __class_getitem__(cls, params):
        cls.__metadata__ = params
        return cls


def annotated_type(cls):
    """
    Adds metadata injection capability to a class via square brackets ([]).
    Use this decorator to enable metadata annotations on classes.
    """
    def class_getitem(cls, params):
        cls.__metadata__ = params
        return cls

    cls.__class_getitem__ = classmethod(class_getitem)
    return cls
