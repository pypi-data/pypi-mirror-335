from setuptools import find_packages, setup

with open('README.md', encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='txtwrap',
    version='2.1.0',
    description='A simple text wrapping tool.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='azzammuhyala',
    author_email='azzammuhyala@gmail.com',
    license='MIT',
    python_requires='>=3.3',
    packages=find_packages(),
    include_package_data=True,
    keywords=['wrap', 'wrapper', 'wrapping', 'wrapped', 'wrapping tool', 'text wrap',
              'text wrapper', 'simple wrap', 'align', 'aligner', 'aligning', 'aligned'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License'
    ]
)