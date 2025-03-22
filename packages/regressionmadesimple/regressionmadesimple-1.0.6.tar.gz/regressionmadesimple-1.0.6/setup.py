from setuptools import setup
setup(
    name="regressionmadesimple",
    version="1.0.6",
    description="Automate some Linear Regression tasks and plot them using Plotly. The alias is `rms`",
    install_requires=[
        'pandas',
        'numpy',
        'plotly',
        'scikit-learn',
    ],
    packages=['regressionmadesimple'],
    author='Unknownuserfrommars',
    python_requires='>=3.10',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
