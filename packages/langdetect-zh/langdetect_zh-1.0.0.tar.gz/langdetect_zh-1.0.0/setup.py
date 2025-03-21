try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as f:
    readme = f.read()


setup(
    name='langdetect_zh',
    version='1.0.0',
    description='对Google的langdetect进行了修改，使其单独作用于中文文本并获得更好的表现',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='huyc',
    author_email='huyc@mail.ecust.edu.cn',
    keywords='language detection library',
    packages=['langdetect', 'langdetect.utils', 'langdetect.tests'],
    include_package_data=True,
    install_requires=['six'],
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
