from distutils.core import setup

setup(
    name='django_questions',
    description='Anonimous questions to site moderators. Not for wide use.',
    packages=[
        'django_questions',
    ],
    requires=[
        'BeautifulSoup'
    ],
)