from setuptools import setup, find_packages
print(find_packages())

def parse_requirements(filename='requirements.txt'):
    with open(filename) as f:
        lines = (line.strip() for line in f)
        return [line for line in lines if line and not line.startswith("#")]
setup(
    name='tlhengine',
    version='1.0',
    description='my package',
    author='tian lh',
    author_email='tianlhcs@163.com',
    url='https://github.com/your-username/your-package-repo',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.6',
    install_requires =parse_requirements(),
)