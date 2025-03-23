from setuptools import setup

setup(

    name = 'microesb',
    version = '1.0rc2',
    author = 'Claus Prüfer',
    author_email = 'pruefer@webcodex.de',
    description = 'A small OOP based Enterprise Service Bus implementation.',
    long_description = open('./README.md').read(),

    packages = [
        'microesb'
    ],

    package_dir = {
        'microesb': 'src/'
    },

    zip_safe = True

)
