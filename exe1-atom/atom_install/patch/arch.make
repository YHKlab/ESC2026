#
# Sample arch.make for stand-alone ATOM program
#
ARCH=macosx-gfortran
#
# --- Required libraries: xmlf90 and libGridXC
#
# It is assumed that the user has downloaded the library tarballs from Launchpad
# and compiled and installed them.
#
# Somehow (here, or in the environment) define the XMLF90_ROOT and
# GRIDXC_ROOT symbols
#
# ====================================================================
# 1단계: WDIR (상위 작업 디렉토리) 자동 계산 단계
# ====================================================================
# (1) 현재 읽고 있는 arch.make 파일의 위치를 절대 경로로 추적합니다.
#     예: /home/joonho/test/atoms/atom-111/arch.make
_THIS_FILE := $(lastword $(MAKEFILE_LIST))

# (2) 파일명을 떼어내고 폴더 경로만 남깁니다.
#     예: /home/joonho/test/atoms/atom-111/
_ATOM_DIR  := $(dir $(abspath $(_THIS_FILE)))

# (3) 현재 폴더의 상위 폴더(..)를 구해 WDIR로 지정합니다. (자동으로 /../ 기호가 제거됨)
#     예: /home/joonho/test/atoms
WDIR       := $(abspath $(_ATOM_DIR)..)

XMLF90_ROOT := $(WDIR)/libs
GRIDXC_ROOT := $(WDIR)/libgridxc-0.7.6/Gfortran
#
#  NOTE: The building mechanism for Siesta-related libraries is still
#  being refined. The paths of the .mk files under $(XMLF90_ROOT) and $(GRIDXC_ROOT)
#  might change with different versions of the libraries. Check their
#  installation trees and use the appropriate path to the .mk file.
#
include $(XMLF90_ROOT)/share/org.siesta-project/xmlf90.mk
include $(GRIDXC_ROOT)/gridxc.mk
#
# -----Compiler-dependent settings -------------------------------------
#
FC=gfortran
#
FFLAGS= -O2
FFLAGS_DEBUG= -O0 -g -fbacktrace
LDFLAGS=
RANLIB=echo
#
.F.o:
	$(FC) -c $(FFLAGS) $(INCFLAGS)  $(FPPFLAGS) $<
.f.o:
	$(FC) -c $(FFLAGS) $(INCFLAGS)   $<
.F90.o:
	$(FC) -c $(FFLAGS) $(INCFLAGS)  $(FPPFLAGS) $<
.f90.o:
	$(FC) -c $(FFLAGS) $(INCFLAGS)   $<
#
