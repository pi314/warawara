import unittest

try:
    import coverage
    cov = coverage.Coverage()

except ModuleNotFoundError:
    class DummyCoverageClass:
        def __init__(self):
            pass
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    cov = DummyCoverageClass()


if __name__ == '__main__':
    cov.start()

    loader = unittest.TestLoader()
    tests = loader.discover('.')
    runner = unittest.runner.TextTestRunner(verbosity=2)
    runner.run(tests)

    cov.stop()
    cov.save()

    cov.html_report(omit=['test_*.py', '*/site-packages/*'])
