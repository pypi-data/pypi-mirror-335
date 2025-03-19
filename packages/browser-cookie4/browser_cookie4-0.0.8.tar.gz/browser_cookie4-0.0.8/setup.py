from setuptools import setup

setup(
    name='browser-cookie4',
    version='0.0.8',
    packages=['browser_cookie4'],
    # look for package contents in current directory
    package_dir={'browser_cookie4': 'browser_cookie4'},
    author='Ilya Rakhlin',
    author_email='i.rakhlin@gmail.com',
    description='Original author Boris Babic boris.ivan.babic@gmail.com',     # noqa: E501
    url='https://github.com/borisbabic/browser_cookie4',
    install_requires=[
        'lz4',
        'pycryptodomex',
        'urllib3',
        'requests',
        'websocket-client',
        'dbus-python; python_version < "3.7" and ("bsd" in sys_platform or sys_platform == "linux")',
        'jeepney; python_version >= "3.7" and ("bsd" in sys_platform or sys_platform == "linux")',
        'shadowcopy; python_version >= "3.7" and platform_system == "Windows"',
        'wslwinreg2==1.2.0; sys_platform == "linux"',
    ],
    entry_points={'console_scripts': ['browser-cookie=browser_cookie4.__main__:main']},
    license_files=('LICENSE')
)
