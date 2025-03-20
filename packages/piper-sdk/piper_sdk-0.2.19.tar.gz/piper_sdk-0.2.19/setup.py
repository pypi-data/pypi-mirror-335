from setuptools import setup, find_packages # 导入setuptools打包工具
# import setuptools_scm

setup(
    name='piper_sdk',
    version='0.2.19',    # 包版本号，便于维护版本
    # use_scm_version=True,  # 启用 setuptools_scm 来动态获取版本号
    # setup_requires=['setuptools>=40.0', 'setuptools_scm'],  # 指定需要的构建工具
    setup_requires=['setuptools>=40.0'], 
    long_description=open('./piper_sdk/DESCRIPTION.MD').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/agilexrobotics/piper_sdk',  # 主页链接
    license='MIT License',  # 这里显式指定 License
    packages=find_packages(include=['piper_sdk', 'piper_sdk.*']),
    include_package_data=True,
    package_data={
        '': ['LICENSE','*.sh','*.MD'],  # 指定包含的文件
        'piper_sdk/asserts': ['*'],  # 包括 asserts 文件夹下的所有文件
    },
    install_requires=[
        'python-can>=3.3.4',
    ],
    entry_points={
    },
    author='RosenYin',  # 作者
    author_email='yinruocheng321@gmail.com',
    description='A sdk to control Agilex piper arm',   #包的简述
    platforms=['Linux'],
    # url="https://github.com/agilexrobotics/piper_sdk",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',    #对python的最低版本要求,18.04及以上
    project_urls={
        'Repository': 'https://github.com/agilexrobotics/piper_sdk',
        'ChangeLog': 'https://github.com/agilexrobotics/piper_sdk/blob/master/CHANGELOG.MD',
    },
)

