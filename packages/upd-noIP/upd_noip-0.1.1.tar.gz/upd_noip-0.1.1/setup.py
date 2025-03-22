from setuptools import setup, find_packages
setup(
       name="upd_noIP",
       version="0.1.1",
       packages=find_packages(),
       install_requires=[
           "aiohttp>=3.8.0",
       ],
       entry_points={
           "console_scripts": [
               "upd-noip=upd_noIP.cli:main",
           ],
       },
       description="Модуль для оновлення IP на No-IP",
       author="Дмитро Колоднянський",
       author_email="gosdepyxa@gmail.com",
       url="https://github.com/DepyXa/upd_noIP",
       classifiers=[
           "Programming Language :: Python :: 3",
           "License :: OSI Approved :: MIT License",
           "Operating System :: OS Independent",
       ],
       python_requires=">=3.7",
)
