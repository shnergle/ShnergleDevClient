from setuptools import setup

setup(
    app=['main.py'],
    options={'py2app': {'iconfile': 'icon.icns', 'semi_standalone': True}},
    setup_requires=['py2app'],
    name='ShnergleDevClient'
)
