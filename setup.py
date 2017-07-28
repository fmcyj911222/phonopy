import numpy
import os

with_openmp = False

try:
    from setuptools import setup, Extension
    use_setuptools = True
    print("setuptools is used.")
except ImportError:
    from distutils.core import setup, Extension
    use_setuptools = False
    print("distutils is used.")

include_dirs_numpy = [numpy.get_include()]
cc = None
if 'CC' in os.environ:
    if 'clang' in os.environ['CC']:
        cc = 'clang'
    if 'gcc' in os.environ['CC']:
        cc = 'gcc'

# Workaround Python issue 21121
import sysconfig
config_var = sysconfig.get_config_var("CFLAGS")
if config_var is not None and "-Werror=declaration-after-statement" in config_var:
    os.environ['CFLAGS'] = config_var.replace(
        "-Werror=declaration-after-statement", "")    

######################
# _phonopy extension #
######################
include_dirs_phonopy = ['c/harmonic_h', 'c/kspclib_h'] + include_dirs_numpy
sources_phonopy = ['c/_phonopy.c',
                   'c/harmonic/dynmat.c',
                   'c/harmonic/derivative_dynmat.c',
                   'c/kspclib/kgrid.c',
                   'c/kspclib/tetrahedron_method.c']

if with_openmp:
    extra_compile_args_phonopy = ['-fopenmp',]
    if cc == 'gcc':
        extra_link_args_phonopy = ['-lgomp',]
    elif cc == 'clang':
        extra_link_args_phonopy = []
    else:
        extra_link_args_phonopy = ['-lgomp',]
else:
    extra_compile_args_phonopy = []
    extra_link_args_phonopy = []

extension_phonopy = Extension(
    'phonopy._phonopy',
    extra_compile_args=extra_compile_args_phonopy,
    extra_link_args=extra_link_args_phonopy,
    include_dirs=include_dirs_phonopy,
    sources=sources_phonopy)


#####################
# _spglib extension #
#####################
if with_openmp:
    extra_compile_args_spglib=['-fopenmp',]
    if cc == 'gcc':
        extra_link_args_spglib=['-lgomp',]
    elif cc == 'clang':
        extra_link_args_spglib=[]
    else:
        extra_link_args_spglib=['-lgomp',]
else:
    extra_compile_args_spglib=[]
    extra_link_args_spglib=[]

extension_spglib = Extension(
    'phonopy._spglib',
    include_dirs=['c/spglib_h'] + include_dirs_numpy,
    extra_compile_args=extra_compile_args_spglib,
    extra_link_args=extra_link_args_spglib,
    sources=['c/_spglib.c',
             'c/spglib/arithmetic.c',
             'c/spglib/cell.c',
             'c/spglib/delaunay.c',
             'c/spglib/hall_symbol.c',
             'c/spglib/kgrid.c',
             'c/spglib/kpoint.c',
             'c/spglib/mathfunc.c',
             'c/spglib/niggli.c',
             'c/spglib/pointgroup.c',
             'c/spglib/primitive.c',
             'c/spglib/refinement.c',
             'c/spglib/sitesym_database.c',
             'c/spglib/site_symmetry.c',
             'c/spglib/spacegroup.c',
             'c/spglib/spg_database.c',
             'c/spglib/spglib.c',
             'c/spglib/spin.c',
             'c/spglib/symmetry.c'])

ext_modules_phonopy = [extension_phonopy, extension_spglib]
packages_phonopy = ['phonopy',
                    'phonopy.cui',
                    'phonopy.gruneisen',
                    'phonopy.harmonic',
                    'phonopy.interface',
                    'phonopy.phonon',
                    'phonopy.qha',
                    'phonopy.spectrum',
                    'phonopy.structure',
                    'phonopy.unfolding',
                    'phonopy.version']
scripts_phonopy = ['scripts/phonopy',
                   'scripts/phonopy-qha',
                   'scripts/phonopy-FHI-aims',
                   'scripts/bandplot',
                   'scripts/outcar-born',
                   'scripts/propplot',
                   'scripts/tdplot',
                   'scripts/dispmanager',
                   'scripts/gruneisen',
                   'scripts/pdosplot']

if __name__ == '__main__':

    version_nums = [None, None, None]
    with open("phonopy/version/__init__.py") as f:
        for line in f:
            if "short_version" in line:
                for i, num in enumerate(line.split()[2].strip('\"').split('.')):
                    version_nums[i] = int(num)
                break

    try:
        import subprocess
        git_describe = subprocess.check_output(["git", "describe", "--tags"])
        git_hash = str(git_describe.strip().split(b"-")[2][1:])
        if git_hash[:2] == "b\'":
            git_hash = git_hash[2:]
        git_hash = git_hash.replace('\'', '')
        with open("phonopy/version/git_hash.py", 'w') as w:
            git_hash_line = "git_hash = \"%s\"\n" % git_hash
            w.write(git_hash_line)
            print(git_hash_line)
    except:
        with open("phonopy/version/git_hash.py", 'w') as w:
            w.write("git_hash = None\n")

    # To deploy to pypi/conda by travis-CI
    if os.path.isfile("__nanoversion__.txt"):
        with open('__nanoversion__.txt') as nv:
            try :
                for line in nv:
                    nanoversion = int(line.strip())
                    break
            except ValueError :
                nanoversion = 0
            if nanoversion:
                version_nums.append(nanoversion)

    if None in version_nums:
        print("Failed to get version number in setup.py.")
        raise

    version_number = ".".join(["%d" % n for n in version_nums])
    if use_setuptools:
        setup(name='phonopy',
              version=version_number,
              description='This is the phonopy module.',
              author='Atsushi Togo',
              author_email='atz.togo@gmail.com',
              url='http://atztogo.github.io/phonopy/',
              packages=packages_phonopy,
              install_requires=['numpy', 'PyYAML', 'matplotlib', 'h5py'],
              provides=['phonopy'],
              scripts=scripts_phonopy,
              ext_modules=ext_modules_phonopy)
    else:
        setup(name='phonopy',
              version=version_number,
              description='This is the phonopy module.',
              author='Atsushi Togo',
              author_email='atz.togo@gmail.com',
              url='http://atztogo.github.io/phonopy/',
              packages=packages_phonopy,
              requires=['numpy', 'PyYAML', 'matplotlib', 'h5py'],
              provides=['phonopy'],
              scripts=scripts_phonopy,
              ext_modules=ext_modules_phonopy)


