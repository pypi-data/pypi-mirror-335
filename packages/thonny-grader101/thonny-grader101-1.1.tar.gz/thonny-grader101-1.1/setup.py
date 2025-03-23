from setuptools import setup
import os.path

setup(
      name="thonny-grader101",
      version="1.1",
      description="Thonny Plugins for Grader 101",
      long_description="""Thonny plugin for ChulaEngineeing Grader 101""",
      url="https://2110101.cp.eng.chula.ac.th",
      author="somchai.p",
      author_email="somchai.p@chula.ac.th",
      license="MIT",
      install_requires=[
        'requests>=2.27.1',
        'bs4>=0.0.2',
      ],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      keywords="Grader101",
      platforms=["Windows", "macOS", "Linux"],
      python_requires=">=3.5",
      packages=["thonnycontrib.grader101"],
)