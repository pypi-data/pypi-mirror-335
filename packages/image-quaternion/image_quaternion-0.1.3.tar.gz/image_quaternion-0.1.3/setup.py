from setuptools import setup, find_packages

setup(
    name='image_quaternion',
    version='0.1.3',
    author='Ramiro Esquivel Felix, Luis Octavio Solis Sanchez',
    author_email='resfera@gmail.com',
    description='Una librería para trabajar con imágenes en formato de cuaterniones.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/tu_usuario/image_quaternion',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
        'opencv-python',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)