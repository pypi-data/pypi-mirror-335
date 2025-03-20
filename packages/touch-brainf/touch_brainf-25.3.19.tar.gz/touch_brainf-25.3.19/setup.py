# based on the goonlang setup.py

from setuptools import setup, find_packages # type: ignore
 
classifiers = [
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.12',
    'Programming Language :: Python :: Implementation',
    'Programming Language :: Python :: Implementation :: CPython'
]
 
setup(
    name='touch_brainf',
    version='25.3.19',
    description='BrainF interpreter Python package',
    long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.md').read(),
    url='https://github.com/Touchcreator/touch-brainf',  
    author='Touchcreator (Tochukwu Okolo)',
    author_email='tochukwu.m.okolo@gmail.com',
    license='MIT', 
    classifiers=classifiers,
    keywords=['brainf', 'branflakes', 'brainfuck', 'python', 'touchcreator'], 
    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'touch-brainf = touch_brainf.__main__:main'
        ]
    },
    long_description_content_type='text/markdown'
)