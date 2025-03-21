from setuptools import setup, find_packages

setup(
    name='tamagotchi_jeu',  # Nom de ton package
    version='0.1',  # Version de ton package
    packages=find_packages(),  # Trouve automatiquement les packages (dossier contenant __init__.py)
    install_requires=[],  # Liste des dépendances, vide ici si tu n'en as pas
    include_package_data=True,
    description='Un jeu Tamagotchi en Python',  # Une description courte de ton projet
    long_description=open('README.md').read(),  # Lecture du fichier README pour une description plus détaillée
    long_description_content_type='text/markdown',  # Format markdown pour README
    author='Meyer Robin',
    author_email='robin.meyer@cpe.fr',
    url='https://github.com/toncompte/tamagotchi',  # Lien vers ton projet
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Change selon ta licence
        'Operating System :: OS Independent',
    ],
)
