import setuptools

PACKAGE_NAME = "opensearch-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.5',  # ! check: https://pypi.org/project/opensearch-local/ for the latest version
    author="Circles",
    author_email="info@circlez.ai",
    description=f"PyPI Package for Circles {PACKAGE_NAME} Python",
    long_description=f"PyPI Package for Circles {PACKAGE_NAME} Python",
    long_description_content_type='text/markdown',
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'python-sdk-remote',
        'event-local>=0.0.9',
        'contact-local>=0.0.71',
        'opensearch-py'
    ]
)
