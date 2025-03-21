from setuptools import setup, find_packages

setup(
    name="decentralized-ai",
    version="1.0.0",
    packages=find_packages(include=['federated_learning*', 'ipfs*']),
    package_data={
        'federated_learning': ['zk-circuits/*.zok'],
    },
    install_requires=[
        'torch>=2.2.0',
        'cryptography==41.0.7',
        'zkpytorch @ git+https://github.com/yourorg/zkpytorch@main',
    ],
    extras_require={
        'gpu': ['cupy-cuda12x>=13.0.0'],
        'quantum': ['qiskit-kyber==0.5.0'],
    },
    entry_points={
        'console_scripts': [
            'ai-train=federated_learning.train.federated_trainer:main',
        ],
    },
    dependency_links=[
        'https://download.pytorch.org/whl/cu118/',
    ]
)