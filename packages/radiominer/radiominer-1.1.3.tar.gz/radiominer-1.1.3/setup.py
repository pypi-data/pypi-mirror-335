from setuptools import setup, find_packages

setup(
    name='radiominer',
    version='1.1.3',
    author='Sebastian Milchsack',
    author_email='info@milchsack.com',
    description='A radio streaming and transcription application.',
    long_description=open('README.md').read(),
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'radiominer=radiominer.cli:main',
        ],
    },
    install_requires=[
        'openai-whisper',
        'ffmpeg-python',
        'numpy',
        'colorama',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)