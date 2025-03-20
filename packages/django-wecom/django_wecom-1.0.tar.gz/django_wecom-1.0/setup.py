from setuptools import setup, find_packages

setup(
    name = 'django_wecom',
    version = '1.0',
    packages = ['django_wecom', 'django_wecom.migrations'],
    install_requires = [
        'requests',
    ],
    description = 'Wecom Auth for Djnago',
    long_description = open('readme.md').read(),
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/liuzihaohao/django-wecom',
    author = 'Edgar Liu',
    author_email = 'liuzihao@qdzx.net.cn',
    python_requires = '>=3.6',
)