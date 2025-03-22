from setuptools import setup, find_packages

setup(
    name="ssh_ansible",
    version="0.9.0",
    description="SSH to host from ansible inventory",
    long_description=open("PYPI.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/marekruzicka/ansible-ssh.git",
    author="Marek Ruzicka",
    author_email="pypi@glide.sk",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
         "console_scripts": [
             "ansible-ssh = ssh_ansible.ansible_ssh:main",
         ]
    },
    install_requires=[
      "ansible-core>=2.9",
    ],
    extra_require={
      "dev": [
        "twine>=6.1",
      ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console"
    ],
)
