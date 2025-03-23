from setuptools import setup, find_namespace_packages

setup(
    name='fx-shared-models',
    version='0.2.17',
    packages=find_namespace_packages(include=['shared_models*']),
    install_requires=[
        'Django>=3.0',
        'django-environ>=0.10.0',
    ],
    python_requires='>=3.8',
    author='FX Backend',
    author_email='fxbackend@gmail.com',
    description='Shared models for FX Backend',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/fxbackend/fx-shared-models',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django',
    ],
    include_package_data=True,
    package_data={
        'shared_models': [
            'accounts/*'
            'common/*',
            'company_ba/*'
            'customers/*',
            'ib_commission/*',
            'services/*',
            'system_settings/*',
            'transactions/*',
        ],
    },
) 