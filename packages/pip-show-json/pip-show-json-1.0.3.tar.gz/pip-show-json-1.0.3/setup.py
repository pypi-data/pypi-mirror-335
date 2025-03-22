import setuptools
import distutils.core

setuptools.setup(
    name='pip-show-json',
    version="1.0.3",
    author='readwithai',
    long_description_content_type='text/markdown',
    url='https://github.com/talwrii/pip-show',
    author_email='talwrii@gmail.com',
    description='Show JSON metadata for an uninstalled pip package',
    license='MIT',
    packages=["pip_show"],
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': ['pip-show-json=pip_show.main:main']
    }
)
