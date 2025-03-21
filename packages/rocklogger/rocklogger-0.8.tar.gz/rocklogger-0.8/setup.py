from setuptools import setup, find_packages

setup(
  name='rocklogger',  # How you named your package folder (MyLib)
  packages=find_packages(),  # Automatically find packages
  version='0.8',  # Start with a small number and increase it with every change you make
  license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description='Rockwool logger with intelligent module filtering',  # Give a short description about your library
  author='Mohamed Abouseif',  # Type in your name
  author_email='mohamed.abouseif@rockwool.com',  # Type in your E-Mail
  url='https://github.com/rw-MohamedAbouseif/Rocklogger.git',  # Provide either the link to your GitHub or to your website
  download_url='https://github.com/rw-MohamedAbouseif/Rocklogger/archive/refs/tags/v0.8.0.tar.gz',  # Link to the specific release
  keywords=['Logger', 'ROCKWOOL', 'Logging', 'Filter'],  # Keywords that define your package best
  install_requires=[  # List dependencies here
      # e.g. 'requests', 'numpy',
  ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',  # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',  # Again, pick a license
    'Programming Language :: Python :: 3',  # Specify which Python versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
  ],
  long_description=open('README.md').read(),  # Ensure README.md exists
  long_description_content_type='text/markdown',  # Correct option name
)
