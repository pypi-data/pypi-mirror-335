from setuptools import setup, Extension
import sys

# Configuración para requerir numpy durante la instalación
setup_requires = ['numpy']
install_requires = ['numpy', 'pandas']

# Define extensión sin include_dirs inicialmente
trend_module = Extension('trend_following',
                         sources=['trend_following.c'],
                         extra_compile_args=['-fPIC'])

# Intentar importar numpy y configurar include_dirs inmediatamente
# Esto funcionará cuando numpy ya esté instalado o durante la construcción con python -m build
try:
    import numpy
    trend_module.include_dirs = [numpy.get_include()]
    print(f"NumPy include directory encontrado: {numpy.get_include()}")
except ImportError:
    print("NumPy no disponible en tiempo de configuración, usando setup_requires")

setup(
    name='trend_following_frd',
    version='1.0',
    description='Módulo de backtest de trend following en C',
    ext_modules=[trend_module],
    setup_requires=setup_requires,
    install_requires=install_requires,
    py_modules=['utils'],
    python_requires='>=3.6',
)