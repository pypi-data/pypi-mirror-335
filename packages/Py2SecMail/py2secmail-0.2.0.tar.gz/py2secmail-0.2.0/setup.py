from setuptools import setup, find_packages

setup(
    name='Py2SecMail',  # Nom du package
    version='0.2.0',  # Version de votre package
    description='Librairie pour interagir avec l\'API 2SecMail pour des emails temporaires',
    long_description=open('README.md', encoding='utf-8').read(),  # Lire le fichier README.md avec encodage UTF-8
    long_description_content_type='text/markdown',
    author='ItsukiPth',  # Remplacez par votre nom
    author_email='itsukiche@gmail.com',  # Remplacez par votre email
    url='https://github.com/alvorks/Py2SecMail',  # Remplacez par l'URL de votre projet
    packages=find_packages(),  # Détecte automatiquement les packages dans votre projet
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[  # Liste des dépendances nécessaires
        'requests',  # Pour effectuer les requêtes HTTP
    ],
    python_requires='>=3.6',  # Version de Python requise
)