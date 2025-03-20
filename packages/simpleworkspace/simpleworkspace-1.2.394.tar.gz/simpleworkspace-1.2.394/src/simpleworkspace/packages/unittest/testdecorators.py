class TestDecorators:
    @staticmethod
    def TemporaryDirectory(inject:str):
        import functools
        from tempfile import TemporaryDirectory

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with TemporaryDirectory(prefix="pytestrun_") as tempdir:
                    # Pass the temporary directory to the test function
                    tempdir = tempdir.replace('\\', '/')
                    kwargs[inject] = tempdir
                    result = func(*args, **kwargs)
                    return result
            return wrapper
        return decorator

    @staticmethod
    def SilenceOutput(func):
        '''avoids cluttering test run with expected stdout and stderr'''
        import functools
        from contextlib import redirect_stderr, redirect_stdout
        from io import StringIO

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            stream_stdout, stream_stderr = StringIO(), StringIO()
            with redirect_stdout(stream_stdout), redirect_stderr(stream_stderr):
                result = func(*args, **kwargs)
                return result
        return wrapper