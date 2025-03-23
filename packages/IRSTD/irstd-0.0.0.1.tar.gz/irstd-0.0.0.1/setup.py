import setuptools

#### 示例 `setup.py` 文件：
import os
import setuptools

# 打开 README.md 文件并读取内容
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as readme:
    long_description = readme.read()

setuptools.setup(
    name="IRSTD",
    version="0.0.0.1",
    python_requires='>=3.7',
    author="Aohua Li",
    author_email="liah24@mails.jlu.edu.cn",
    description="It is a DeepLearning package to foster developed by Aohua Li",
    long_description=long_description,  # 项目描述内容
    long_description_content_type="text/markdown",  # 指定内容类型为 Markdown
    url="https://github.com/PepperCS/IRSTD",
    packages=setuptools.find_packages(),
    zip_safe=True,

    # install_requires=requirements,
)
