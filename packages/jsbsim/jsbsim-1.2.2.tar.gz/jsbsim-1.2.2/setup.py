# This script has been automatically built from /Users/runner/work/jsbsim/jsbsim/python/setup.py.in
#
# Copyright (c) 2014-2025 Bertrand Coconnier
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, see <http://www.gnu.org/licenses/>
#

import os

from setuptools._distutils.ccompiler import new_compiler
from setuptools._distutils.unixccompiler import UnixCCompiler
from setuptools._distutils import log
from setuptools import setup
from setuptools.command.build_ext import build_ext
from setuptools.command.install_lib import install_lib
from setuptools.dist import Distribution
from setuptools.extension import Extension


# When compiled with Microsoft Visual C++, the JSBSim Python module is linked
# with the dynamically linked library msvcp140.dll which is not a standard
# library on Windows. So this code allows msvcp140.dll to be shipped with the
# Python module.
class InstallJSBSimModule(install_lib):
    def install(self):
        if compiler.compiler_type == 'msvc':
            msvcp_dll = 'msvcp140.dll'

            for d in os.environ['PATH'].split(';'):
                libpath = os.path.join(d, msvcp_dll)
                if os.path.exists(libpath):
                    if not os.path.exists(self.install_dir):
                        log.info(f'creating {self.install_dir}')
                        os.makedirs(self.install_dir)
                    log.info("copying %s -> %s", libpath, self.install_dir)
                    self.copy_file(libpath, os.path.join(self.install_dir,
                                                         msvcp_dll))
                    break
            else:
                raise FileNotFoundError(f"Could not find '{msvcp_dll}'")
        install_lib.install(self)

# distutils assumes that all the files must be compiled with the same compiler
# flags regardless of their file extension .c or .cpp.
# JSBSim C++ files must be compiled with -std=c++1x but compilation on MacOSX
# fails when trying to compile C files with -std=c++1x.
# The class C_CxxCompiler adds C++ flags to compilation flags for C++ files only.
class C_CxxCompiler(UnixCCompiler):
    def _compile(self, obj, src, ext, cc_args, extra_postargs, pp_opts):
        _cc_args = cc_args
        # Add the C++ flags to the compile flags if we are dealing with a C++
        # source file.
        if os.path.splitext(src)[-1] in ('.cpp', '.cxx', '.cc'):
            _cc_args = cpp_compile_flag + cc_args

        UnixCCompiler._compile(self, obj, src, ext, _cc_args,
                                extra_postargs, pp_opts)

# The class BuildC_CxxExtension intercepts the build of the Python module and
# replaces the compiler by an instance of C_CxxCompiler that select the compile
# flags depending on whether it is a C++ source file or not.
class BuildC_CxxExtension(build_ext):
    def build_extension(self, ext):
        if self.compiler.compiler_type == 'unix':

            old_compiler = self.compiler
            self.compiler = C_CxxCompiler()
            # Copy the attributes to the new compiler instance
            for attr, value in old_compiler.__dict__.items():
                setattr(self.compiler, attr, value)
        return build_ext.build_extension(self, ext)

# Get the path to the JSBSim library.
library_path = os.path.join('../', 'src')

compiler = new_compiler()

# Update the JSBSim library path according to the environment variable
# JSBSIM_BUILD_CONFIG. This feature is mainly useful for CI builds.
if compiler.compiler_type == 'msvc' and 'JSBSIM_BUILD_CONFIG' in os.environ:
    library_path=os.path.join(library_path, os.environ['JSBSIM_BUILD_CONFIG'])

# It is good practice to provide library paths as absolute paths.
library_path = os.path.abspath(library_path)

convert_CMake_list_to_Python_list = lambda s: [item.strip() for item in s.split(';') if item!='']

# `cpp_compile_flag` is used for C++ compilation only (see class `C_CxxCompiler`)
if compiler.compiler_type == 'unix':
    cpp_compile_flag = ['-std=c++14', '-DNDEBUG']
    cpp_link_flags = []
    link_libraries = convert_CMake_list_to_Python_list(';m')
elif compiler.compiler_type == 'msvc':
    cpp_compile_flag = ['/DJSBSIM_STATIC_LINK', '/DNDEBUG']
    cpp_link_flags = []
    link_libraries = convert_CMake_list_to_Python_list(';wsock32;ws2_32')
else:
    cpp_compile_flag = ['-DNDEBUG']
    cpp_link_flags = []
    link_libraries = convert_CMake_list_to_Python_list('')

# Check if the library exists and build the Python module accordingly.
dist = Distribution({'script_name': __file__})
dist.parse_command_line()

if 'sdist' not in dist.commands and compiler.find_library_file([library_path],
                                                               'JSBSim'):
    # OK, the JSBSim library has already been compiled so let's use it to build
    # the Python module.
    if os.path.exists('_jsbsim.cxx'):
        source_file = '_jsbsim.cxx'
    else:
        source_file = '_jsbsim.pyx'

    ext_kwargs = { 'sources': [source_file],
                   'include_dirs': ['src'],
                   'libraries': ['JSBSim'] + link_libraries,
                   'library_dirs': [library_path],
                   'extra_compile_args': cpp_compile_flag,
                   'extra_link_args': cpp_link_flags }
    setup_kwargs = { 'cmdclass' : {'install_lib': InstallJSBSimModule}}
else:
    # We cannot find the JSBSim library so the Python module must be built from
    # the sources.
    if compiler.compiler_type == 'msvc':
        compile_flags = ['/D'+flag for flag in convert_CMake_list_to_Python_list('_USE_MATH_DEFINES;NOMINMAX;XML_STATIC;JSBSIM_VERSION="1.2.2 [GitHub build 1471/commit 6b045fbff3b97a5e94834665cf4e2c990af5adaf]";NDEBUG;JSBSIM_STATIC_LINK')]
    else:
        compile_flags = ['-D'+flag for flag in convert_CMake_list_to_Python_list('JSBSIM_VERSION="1.2.2 [GitHub build 1471/commit 6b045fbff3b97a5e94834665cf4e2c990af5adaf]";NDEBUG')]

    ext_kwargs = { 'sources': convert_CMake_list_to_Python_list('_jsbsim.pyx;src/FGFDMExec.cpp;src/FGJSBBase.cpp;src/initialization/FGInitialCondition.cpp;src/initialization/FGTrim.cpp;src/initialization/FGTrimAxis.cpp;src/initialization/FGLinearization.cpp;src/models/atmosphere/FGMSIS.cpp;src/models/atmosphere/FGStandardAtmosphere.cpp;src/models/atmosphere/FGWinds.cpp;src/models/atmosphere/MSIS/nrlmsise-00.c;src/models/atmosphere/MSIS/nrlmsise-00_data.c;src/models/flight_control/FGDeadBand.cpp;src/models/flight_control/FGFCSComponent.cpp;src/models/flight_control/FGFilter.cpp;src/models/flight_control/FGGain.cpp;src/models/flight_control/FGKinemat.cpp;src/models/flight_control/FGSummer.cpp;src/models/flight_control/FGSwitch.cpp;src/models/flight_control/FGFCSFunction.cpp;src/models/flight_control/FGSensor.cpp;src/models/flight_control/FGPID.cpp;src/models/flight_control/FGActuator.cpp;src/models/flight_control/FGAccelerometer.cpp;src/models/flight_control/FGGyro.cpp;src/models/flight_control/FGMagnetometer.cpp;src/models/flight_control/FGAngles.cpp;src/models/flight_control/FGWaypoint.cpp;src/models/flight_control/FGDistributor.cpp;src/models/flight_control/FGLinearActuator.cpp;src/models/propulsion/FGElectric.cpp;src/models/propulsion/FGEngine.cpp;src/models/propulsion/FGForce.cpp;src/models/propulsion/FGNozzle.cpp;src/models/propulsion/FGPiston.cpp;src/models/propulsion/FGPropeller.cpp;src/models/propulsion/FGRocket.cpp;src/models/propulsion/FGTank.cpp;src/models/propulsion/FGThruster.cpp;src/models/propulsion/FGTurbine.cpp;src/models/propulsion/FGTurboProp.cpp;src/models/propulsion/FGTransmission.cpp;src/models/propulsion/FGRotor.cpp;src/models/propulsion/FGBrushLessDCMotor.cpp;src/models/FGAerodynamics.cpp;src/models/FGAircraft.cpp;src/models/FGAtmosphere.cpp;src/models/FGAuxiliary.cpp;src/models/FGFCS.cpp;src/models/FGSurface.cpp;src/models/FGGroundReactions.cpp;src/models/FGInertial.cpp;src/models/FGLGear.cpp;src/models/FGMassBalance.cpp;src/models/FGModel.cpp;src/models/FGOutput.cpp;src/models/FGPropagate.cpp;src/models/FGPropulsion.cpp;src/models/FGInput.cpp;src/models/FGExternalReactions.cpp;src/models/FGExternalForce.cpp;src/models/FGBuoyantForces.cpp;src/models/FGGasCell.cpp;src/models/FGAccelerations.cpp;src/math/FGColumnVector3.cpp;src/math/FGFunction.cpp;src/math/FGLocation.cpp;src/math/FGMatrix33.cpp;src/math/FGPropertyValue.cpp;src/math/FGQuaternion.cpp;src/math/FGRealValue.cpp;src/math/FGTable.cpp;src/math/FGCondition.cpp;src/math/FGRungeKutta.cpp;src/math/FGModelFunctions.cpp;src/math/FGTemplateFunc.cpp;src/math/FGStateSpace.cpp;src/input_output/FGGroundCallback.cpp;src/input_output/FGPropertyManager.cpp;src/input_output/FGScript.cpp;src/input_output/FGXMLElement.cpp;src/input_output/FGXMLParse.cpp;src/input_output/FGfdmSocket.cpp;src/input_output/FGXMLFileRead.cpp;src/input_output/FGOutputType.cpp;src/input_output/FGOutputFG.cpp;src/input_output/FGOutputSocket.cpp;src/input_output/FGOutputFile.cpp;src/input_output/FGOutputTextFile.cpp;src/input_output/FGPropertyReader.cpp;src/input_output/FGModelLoader.cpp;src/input_output/FGInputType.cpp;src/input_output/FGInputSocket.cpp;src/input_output/FGUDPInputSocket.cpp;src/input_output/string_utilities.cpp;src/simgear/props/props.cxx;src/simgear/xml/easyxml.cxx;src/simgear/xml/xmlparse.c;src/simgear/xml/xmltok.c;src/simgear/xml/xmlrole.c;src/simgear/magvar/coremag.cxx;src/simgear/misc/sg_path.cxx;src/simgear/misc/strutils.cxx;src/simgear/io/iostreams/sgstream.cxx;src/GeographicLib/Geodesic.cpp;src/GeographicLib/GeodesicLine.cpp;src/GeographicLib/Math.cpp'),
                   'libraries': link_libraries,
                   'include_dirs': ['src', 'src/simgear/xml'],
                   'extra_compile_args': compile_flags }
    # List of required modules to build the JSBSim module from the sources.
    setup_kwargs = {'cmdclass' : {'build_ext': BuildC_CxxExtension}}

# Prepare the list of XML data files (aircraft, engines, ...)
package_data_files = ['_jsbsim.pxd', 'engine/*.xml', 'scripts/*.xml', 'systems/*.xml',
                      'aircraft/*.xml', 'LICENSE.txt', 'libexpat-LICENSE.txt',
                      'GeographicLib-LICENSE.txt', 'py.typed', '*.pyi']

# Iterate over the aircraft folders
for d in os.scandir('jsbsim/aircraft'):
    if d.is_dir():
        dir_name = os.path.join('aircraft', d.name)
        package_data_files.append(os.path.join(dir_name, '*.xml'))

        # Some aircraft folders include a "Systems" and/or an "Engines"
        # sub-directory (with several alternative spelling) so make sure they
        # are copied in the wheel archive (see GH issue #687)
        for sub_dir in ('Systems', 'systems', 'Engines', 'engines', 'Engine',
                        'engine'):
            sub_dir_name = os.path.join(dir_name, sub_dir)
            subdir_dir_fullname = os.path.join('jsbsim', sub_dir_name)
            if os.path.exists(subdir_dir_fullname) and os.path.isdir(subdir_dir_fullname):
                package_data_files.append(os.path.join(sub_dir_name, '*.xml'))

# Build & installation process for the JSBSim Python module
setup(
    name="JSBSim".lower(),
    version="1.2.2",
    url="https://github.com/JSBSim-Team/jsbsim",
    author="Jon S. Berndt et al.",
    author_email="jsbsim-users@lists.sourceforge.net",
    license="LGPL 2.1",
    description="An open source flight dynamics & control software library",
    long_description="JSBSim is a multi-platform, general purpose object-oriented Flight Dynamics Model (FDM) written in C++. The FDM is essentially the physics & math model that defines the movement of an aircraft, rocket, etc., under the forces and moments applied to it using the various control mechanisms and from the forces of nature. JSBSim can be run in a standalone batch mode flight simulator (no graphical displays) for testing and study, or integrated with [FlightGear](http://home.flightgear.org/) or other flight simulator.",
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Operating System :: Microsoft",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: C++",
        "Programming Language :: Python :: 3",
        "Topic :: Education",
        "Topic :: Games/Entertainment :: Simulation",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    scripts=['JSBSim.py'],
    install_requires=['numpy>=1.20'],
    ext_modules=[Extension('jsbsim._jsbsim', language='c++', **ext_kwargs)],
    python_requires=">=3.8",
    packages=['jsbsim'],
    package_data={'jsbsim': package_data_files},
    zip_safe=False,  # needed for mypy to find the type hints stubs
    **setup_kwargs)
