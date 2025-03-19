try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

long_desc = '''Translates JavaScript to Python code. jsemulator is able to translate and execute virtually any JavaScript code.

jsemulator is written in pure python and does not have any dependencies. Basically an implementation of JavaScript core in pure python.


    import jsemulator

    f = jsemulator.eval_js( "function $(name) {return name.length}" )

    f("Hello world")

    # returns 11

Now also supports ECMA 6 through jsemulator.eval_js6(js6_code)!
'''

# rm -rf dist build && python3 setup.py sdist bdist_wheel
# twine upload dist/*
setup(
    name='jsemulator',
    version='0.7.4',

    packages=['jsemulator', 'jsemulator.utils', 'jsemulator.prototypes', 'jsemulator.translators',
              'jsemulator.constructors', 'jsemulator.host', 'jsemulator.es6', 'jsemulator.internals',
              'jsemulator.internals.prototypes', 'jsemulator.internals.constructors', 'jsemulator.py_node_modules'],
    install_requires = ['tzlocal>=1.2', 'six>=1.10', 'jsparser>=2.7.3'],
    license='MIT',
    author='Blake Foster',
    author_email='blakehulsey@gmail.com',
    description='JavaScript to Python Translator & JavaScript interpreter written in 100% pure Python.',
    long_description=long_desc
)
