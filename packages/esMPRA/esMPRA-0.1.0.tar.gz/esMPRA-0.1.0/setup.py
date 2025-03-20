from setuptools import setup, find_packages

setup(
    name="esMPRA",           # 包名称
    version="0.1.0",             # 版本号
    author="Jiaqi Li",          # 作者
    author_email="kaches@foxmail.com",
    description="An easy to use pipeline for MPRA experiment quality control and data processing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/KachesL/esMPRA",  # 项目主页
    packages=find_packages(where="src"),
    package_dir={"": "src"},    # 自动发现所有包和子包
    package_data={
        "esMPRA": ["data/*.pkl"],  # 打包 data 文件夹中的所有 .txt 文件
    },
    include_package_data=True,
    install_requires=[
        # 依赖项列表
        "numpy>=1.18.0",
        "matplotlib",
        'pandas',
        'reportlab'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',     # 支持的 Python 版本
    entry_points={
        'console_scripts': [
            'step1_oligo_barcode_map=esMPRA.step1_oligo_barcode_map:main',
            'step2_get_plasmid_counts=esMPRA.step2_get_plasmid_counts:main',
            'step3_get_RNA_counts=esMPRA.step3_get_RNA_counts:main',
            'step4_get_result=esMPRA.step4_get_result:main',
            'step5_compare_diff_rep=esMPRA.step5_compare_diff_rep:main',
            'generate_data_for_MPRAnalyse=esMPRA.generate_data_for_MPRAnalyse:main',
            'qc_step1=esMPRA.qc_step1:main',
            'qc_step2=esMPRA.qc_step2:main',
            'qc_step3=esMPRA.qc_step3:main',
            'qc_step4=esMPRA.qc_step4:main',
            'qc_step5=esMPRA.qc_step5:main',
        ],
    },
)