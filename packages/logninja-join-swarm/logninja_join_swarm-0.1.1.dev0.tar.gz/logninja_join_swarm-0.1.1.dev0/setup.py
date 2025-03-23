from setuptools import setup, find_packages

setup(
    name="logninja-join-swarm",
    version="0.1.1-dev",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'logninja-join-swarm=join_logninja_docker_swarm.setup_node:setup_node'
        ]
    },
    author="Nathan",
    description="Auto-join a machine to the LogNinja Docker Swarm cluster",
    keywords=["docker", "swarm", "logninja", "setup", "ai"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
)
