from setuptools import setup, find_packages
setup(
        name='cs103',
        version='0.3.7',

        description='cs103 utils package',
        long_description='Utility package for CPSC 103 @ The University of British Columbia',

        author='CPSC 103',
        author_email='cs-103@students.cs.ubc.ca',

        license='GPLv3',

        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Education',
            'Topic :: Education',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5'
            ],

        keywords='cs103',
        packages=find_packages(),
        install_requires=['matplotlib', 'pandas', 'canvasapi', 'python-dotenv'],
        include_package_data=True,
        package_data={
            'cs103.custom': ['custom.js']
            }
        )
