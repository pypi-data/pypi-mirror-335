from setuptools import setup, find_packages

setup(
    name='old_package',
    version='0.1.0',
    description='Старый пакет, который будет заменен',
    author='old_author',
    author_email='old_author@example.com',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'requests>=2.25.1',
    ],
    obsoletes=['cheigsfera'],  # Указывает, что этот пакет устарел
)