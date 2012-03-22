from distutils.core import setup

setup(
    name='django_questions',
    description='Anonimous questions to site moderators. Not for wide use.',
    version='0.0.1',
    packages=[
        'django_questions',
    ],
    install_requires=[
        'BeautifulSoup'
    ],
)