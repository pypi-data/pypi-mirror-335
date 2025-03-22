"""
AI Chat Commons in Python
----------------------

Links
`````

* `development version <https://bitbucket.org/entinco/eic-ai-prototypes/src/main/lib-aichatcommons-python>`

"""

from setuptools import find_packages
from setuptools import setup

try:
    readme = open('readme.md').read()
except:
    readme = __doc__

setup(
    name='eic_aichat_commons',
    version='1.0.1',
    url='https://bitbucket.org/entinco/eic-ai-prototypes/src/master/lib-aichatcommons-python',
    license='Commercial',
    author='Enterprise Innovation Consulting LLC',
    author_email='seroukhov@entinco.com',
    description='AI Chat Commons in Python',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['config', 'data', 'test']),
    include_package_data=True,
    zip_safe=True,
    platforms='any',
    install_requires=[
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
