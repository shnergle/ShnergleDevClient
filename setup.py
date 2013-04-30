from setuptools import setup

setup(
    app=['main.py'],
    date_files=['--iconfile'],
    options={'py2app': {'iconfile': 'icon.icns'}},
    setup_requires=['py2app'],
    name='ShnergleDevClient'
)
