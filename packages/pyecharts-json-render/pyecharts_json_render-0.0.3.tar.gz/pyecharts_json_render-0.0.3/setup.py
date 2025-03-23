import setuptools
import os

# 如果readme文件中有中文，那么这里要指定encoding='utf-8'，否则会出现编码错误
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as readme:
    README = readme.read()

setuptools.setup(
 name="pyecharts_json_render",
 version="0.0.3",
 author="forhonourlx",
 author_email="forhonourlx@qq.com",
 description="A simple wrapper using pyecharts to render html from Echarts option(JSON).",
 long_description="You can use Echarts option JSON (similar way in JavaScript) directly to make Echarts html."+README,
 long_description_content_type="text/markdown",
 url="https://github.com/forhonourlx/pyecharts_json_render",
 packages=setuptools.find_packages(),
 classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
 ],
 install_requires=[
        'pyecharts<=1.5.1',
        'Jinja2<=3.0.3',
        'beautifulsoup4',
        #'Django >= 1.11, != 1.11.1, <= 2',
    ],
)