import inspect
import types
import numbers


class PyGeodeFunction:
    def __init__(self, function):
        self.expression = inspect.getsource(function)
        self.preprocess_function(function)
        print(self.expression)

    def preprocess_function(self, function):
        extra_indent = self.expression.index('def')
        self.expression = '\n'.join([item for item in [line[extra_indent:] for line in self.expression.splitlines()]])
        self.expression += self.return_locals_statement()
        self.expression += '\nself.py_geode_function_context.update_original_context(' + function.__name__ + '())'

    def return_locals_statement(self):
        return ';return locals()'


class PyGeodeFunctionContext:
    def __init__(self, original_context=None, target_context=None):
        self.original_context = original_context
        self.target_context = target_context

    def update_original_context(self, context):
        self.original_context.update(context)

    def update_target_context(self, context):
        self.target_context.update(context)


class PyGeodeSession:
    """
    Wrapper class which will execute the passed-in content within the context of the specified Gemfire region.

    For example,

    geodeSession = new PyGeodeSession(region=region, server_side_function=server_side_function)
    with geodeSession.create():
        def main():
            ...Model training/scoring code goes here...
    results = geodeSession.execute('main')

    will pass the embedded code as an argument to the Java client code which will invoke the Gemfire server-side function.

    ----------
    :param region: The Gemfire region
    :parameter server_side_function: The Gemfire server-side function
    """

    def __init__(self, region, server_side_function):
        self.region = region
        self.server_side_function = server_side_function
        self.py_geode_function = None
        self.py_geode_function_context = PyGeodeFunctionContext(original_context={}, target_context={})

    def __enter__(self):
        self.switch_context(to_jvm=False, local=True)

    def __exit__(self, *args, **kwargs):
        self.switch_context(to_jvm=True, local=True)

    def execute(self, client_function):
        self.py_geode_function = PyGeodeFunction(client_function)
        self.py_geode_function_context = \
            PyGeodeFunctionContext(target_context=self.get_locals(targetcontext=True),
                                   original_context=self.get_locals(targetcontext=False))

        # execute Geode function
        exec(self.py_geode_function.expression)

        # return dictionary of computed variables
        return self.py_geode_function_context.original_context

    def create(self):
        return self

    def switch_context(self, to_jvm=True, local=True):
        """
        Used to synchronize the state of targetcontext variables in the invoking Java method's calling context with corresponding variables in the invoked Python function's context.
        Parameters
        ----------
        :param to_jvm: If True (default), will copy targetcontext variable state from the invoking Python caller to the invoked Java context;
        else the reverse will be done (targetcontext variable state from the Java context will be copied to the Python invoker's context)
        :param local: If True (default), no remote call will be invoked; else a remote call will be invoked
        (i.e. when invoking the Geode server-side function)
        """
        if to_jvm:
            print('Copy Python context to Geode context')
            self.py_geode_function_context.update_target_context(self.py_geode_function_context.original_context)
        else:
            print('Copy Geode context to Python context')
            self.py_geode_function_context.update_original_context(self.py_geode_function_context.target_context)

    def get_locals(self, targetcontext=True):
        """
        Returns the "locals" dictionary associated with the target context is targetcontext=True,
        or the original caller if targetcontext=False
        :param targetcontext
        :return: The locals dict associated with the specified context
        """
        frame = inspect.currentframe()
        try:
            if targetcontext:
                return frame.f_back.f_locals
            else:
                return frame.f_back.f_back.f_locals
        finally:
            del frame
