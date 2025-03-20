import setuptools

setuptools.setup(name='pysecoda',
                 version='0.1.2',
                 description='Python API wrapper for the Secoda data platform',
                 long_description=open('README.md').read().strip(),
                 long_description_content_type="text/markdown",
                 author='Matthew Senick',
                 author_email='senick.matthew@gmail.com',
                 url='https://github.com/matts52/pysecoda',
                 packages=setuptools.find_packages(),
                 install_requires=[
                        'requests'
                 ],
                 license='MIT License',
                 zip_safe=False,
                 keywords='API wrapper Secoda data',
                 classifiers=[
                     'Development Status :: 3 - Alpha',
                     'Intended Audience :: Developers',
                     'Programming Language :: Python'
                     ]
                )