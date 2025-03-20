from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='m_panel',
    version='0.0.0.3',
    author='Mahdi Hasan Shuvo',
    author_email='shuvobbhh@gmail.com',
    description='A library for manipulating memory in a Windows process',
    long_description=long_description,
    long_description_content_type='text/markdown',  # Ensure this matches your file format
    url='https://github.com/Mahdi-hasan-shuvo/PyMemoryRW',  # Project homepage
    project_urls={
        'Homepage': 'https://github.com/Mahdi-hasan-shuvo/PyMemoryRW',
        'Bug Reports': 'https://github.com/Mahdi-hasan-shuvo/PyMemoryRW/issues',
        'Source': 'https://github.com/Mahdi-hasan-shuvo/PyMemoryRW',
    },
    packages=find_packages(include=['PyMemRW'
        # 'mahdix', 'pymem', 'pyinjector'
        ]),
    install_requires=[
        # 'pyinjector',
        # 'pymem',
        # 'mahdix',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',  # Adjusted to your requirement
    license='MIT',  # License type
    keywords='memory manipulation Windows memory management process memory Windows API memory injection memory editing Windows process memory library process hacking Windows utilities memory access system programming memory tools Win32 API Python memory library process manipulation memory read/write Windows programming memory management library Python Windows API',
)
