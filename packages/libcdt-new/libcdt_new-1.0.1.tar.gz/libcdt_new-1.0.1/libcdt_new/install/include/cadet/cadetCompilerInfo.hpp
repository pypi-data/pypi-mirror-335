
// This is a generated file. Do not edit!

#ifndef CADET_COMPILER_DETECTION_H
#define CADET_COMPILER_DETECTION_H

// =============================================================================
//  CADET
//  
//  Copyright © 2008-present: The CADET-Core Authors
//            Please see the AUTHORS.md file.
//  
//  All rights reserved. This program and the accompanying materials
//  are made available under the terms of the GNU Public License v3.0 (or, at
//  your option, any later version) which accompanies this distribution, and
//  is available at http://www.gnu.org/licenses/gpl.html
// =============================================================================


#ifdef __cplusplus
# define CADET_COMPILER_IS_Comeau 0
# define CADET_COMPILER_IS_Intel 0
# define CADET_COMPILER_IS_IntelLLVM 0
# define CADET_COMPILER_IS_PathScale 0
# define CADET_COMPILER_IS_Embarcadero 0
# define CADET_COMPILER_IS_Borland 0
# define CADET_COMPILER_IS_Watcom 0
# define CADET_COMPILER_IS_OpenWatcom 0
# define CADET_COMPILER_IS_SunPro 0
# define CADET_COMPILER_IS_HP 0
# define CADET_COMPILER_IS_Compaq 0
# define CADET_COMPILER_IS_zOS 0
# define CADET_COMPILER_IS_IBMClang 0
# define CADET_COMPILER_IS_XLClang 0
# define CADET_COMPILER_IS_XL 0
# define CADET_COMPILER_IS_VisualAge 0
# define CADET_COMPILER_IS_NVHPC 0
# define CADET_COMPILER_IS_PGI 0
# define CADET_COMPILER_IS_CrayClang 0
# define CADET_COMPILER_IS_Cray 0
# define CADET_COMPILER_IS_TI 0
# define CADET_COMPILER_IS_FujitsuClang 0
# define CADET_COMPILER_IS_Fujitsu 0
# define CADET_COMPILER_IS_GHS 0
# define CADET_COMPILER_IS_Tasking 0
# define CADET_COMPILER_IS_OrangeC 0
# define CADET_COMPILER_IS_SCO 0
# define CADET_COMPILER_IS_ARMCC 0
# define CADET_COMPILER_IS_AppleClang 0
# define CADET_COMPILER_IS_ARMClang 0
# define CADET_COMPILER_IS_Clang 0
# define CADET_COMPILER_IS_LCC 0
# define CADET_COMPILER_IS_GNU 0
# define CADET_COMPILER_IS_MSVC 0
# define CADET_COMPILER_IS_ADSP 0
# define CADET_COMPILER_IS_IAR 0
# define CADET_COMPILER_IS_MIPSpro 0

#if defined(__COMO__)
# undef CADET_COMPILER_IS_Comeau
# define CADET_COMPILER_IS_Comeau 1

#elif defined(__INTEL_COMPILER) || defined(__ICC)
# undef CADET_COMPILER_IS_Intel
# define CADET_COMPILER_IS_Intel 1

#elif (defined(__clang__) && defined(__INTEL_CLANG_COMPILER)) || defined(__INTEL_LLVM_COMPILER)
# undef CADET_COMPILER_IS_IntelLLVM
# define CADET_COMPILER_IS_IntelLLVM 1

#elif defined(__PATHCC__)
# undef CADET_COMPILER_IS_PathScale
# define CADET_COMPILER_IS_PathScale 1

#elif defined(__BORLANDC__) && defined(__CODEGEARC_VERSION__)
# undef CADET_COMPILER_IS_Embarcadero
# define CADET_COMPILER_IS_Embarcadero 1

#elif defined(__BORLANDC__)
# undef CADET_COMPILER_IS_Borland
# define CADET_COMPILER_IS_Borland 1

#elif defined(__WATCOMC__) && __WATCOMC__ < 1200
# undef CADET_COMPILER_IS_Watcom
# define CADET_COMPILER_IS_Watcom 1

#elif defined(__WATCOMC__)
# undef CADET_COMPILER_IS_OpenWatcom
# define CADET_COMPILER_IS_OpenWatcom 1

#elif defined(__SUNPRO_CC)
# undef CADET_COMPILER_IS_SunPro
# define CADET_COMPILER_IS_SunPro 1

#elif defined(__HP_aCC)
# undef CADET_COMPILER_IS_HP
# define CADET_COMPILER_IS_HP 1

#elif defined(__DECCXX)
# undef CADET_COMPILER_IS_Compaq
# define CADET_COMPILER_IS_Compaq 1

#elif defined(__IBMCPP__) && defined(__COMPILER_VER__)
# undef CADET_COMPILER_IS_zOS
# define CADET_COMPILER_IS_zOS 1

#elif defined(__open_xl__) && defined(__clang__)
# undef CADET_COMPILER_IS_IBMClang
# define CADET_COMPILER_IS_IBMClang 1

#elif defined(__ibmxl__) && defined(__clang__)
# undef CADET_COMPILER_IS_XLClang
# define CADET_COMPILER_IS_XLClang 1

#elif defined(__IBMCPP__) && !defined(__COMPILER_VER__) && __IBMCPP__ >= 800
# undef CADET_COMPILER_IS_XL
# define CADET_COMPILER_IS_XL 1

#elif defined(__IBMCPP__) && !defined(__COMPILER_VER__) && __IBMCPP__ < 800
# undef CADET_COMPILER_IS_VisualAge
# define CADET_COMPILER_IS_VisualAge 1

#elif defined(__NVCOMPILER)
# undef CADET_COMPILER_IS_NVHPC
# define CADET_COMPILER_IS_NVHPC 1

#elif defined(__PGI)
# undef CADET_COMPILER_IS_PGI
# define CADET_COMPILER_IS_PGI 1

#elif defined(__clang__) && defined(__cray__)
# undef CADET_COMPILER_IS_CrayClang
# define CADET_COMPILER_IS_CrayClang 1

#elif defined(_CRAYC)
# undef CADET_COMPILER_IS_Cray
# define CADET_COMPILER_IS_Cray 1

#elif defined(__TI_COMPILER_VERSION__)
# undef CADET_COMPILER_IS_TI
# define CADET_COMPILER_IS_TI 1

#elif defined(__CLANG_FUJITSU)
# undef CADET_COMPILER_IS_FujitsuClang
# define CADET_COMPILER_IS_FujitsuClang 1

#elif defined(__FUJITSU)
# undef CADET_COMPILER_IS_Fujitsu
# define CADET_COMPILER_IS_Fujitsu 1

#elif defined(__ghs__)
# undef CADET_COMPILER_IS_GHS
# define CADET_COMPILER_IS_GHS 1

#elif defined(__TASKING__)
# undef CADET_COMPILER_IS_Tasking
# define CADET_COMPILER_IS_Tasking 1

#elif defined(__ORANGEC__)
# undef CADET_COMPILER_IS_OrangeC
# define CADET_COMPILER_IS_OrangeC 1

#elif defined(__SCO_VERSION__)
# undef CADET_COMPILER_IS_SCO
# define CADET_COMPILER_IS_SCO 1

#elif defined(__ARMCC_VERSION) && !defined(__clang__)
# undef CADET_COMPILER_IS_ARMCC
# define CADET_COMPILER_IS_ARMCC 1

#elif defined(__clang__) && defined(__apple_build_version__)
# undef CADET_COMPILER_IS_AppleClang
# define CADET_COMPILER_IS_AppleClang 1

#elif defined(__clang__) && defined(__ARMCOMPILER_VERSION)
# undef CADET_COMPILER_IS_ARMClang
# define CADET_COMPILER_IS_ARMClang 1

#elif defined(__clang__)
# undef CADET_COMPILER_IS_Clang
# define CADET_COMPILER_IS_Clang 1

#elif defined(__LCC__) && (defined(__GNUC__) || defined(__GNUG__) || defined(__MCST__))
# undef CADET_COMPILER_IS_LCC
# define CADET_COMPILER_IS_LCC 1

#elif defined(__GNUC__) || defined(__GNUG__)
# undef CADET_COMPILER_IS_GNU
# define CADET_COMPILER_IS_GNU 1

#elif defined(_MSC_VER)
# undef CADET_COMPILER_IS_MSVC
# define CADET_COMPILER_IS_MSVC 1

#elif defined(_ADI_COMPILER)
# undef CADET_COMPILER_IS_ADSP
# define CADET_COMPILER_IS_ADSP 1

#elif defined(__IAR_SYSTEMS_ICC__) || defined(__IAR_SYSTEMS_ICC)
# undef CADET_COMPILER_IS_IAR
# define CADET_COMPILER_IS_IAR 1


#endif

#  if CADET_COMPILER_IS_GNU

#    if !((__GNUC__ * 100 + __GNUC_MINOR__) >= 404)
#      error Unsupported compiler version
#    endif

# if defined(__GNUC__)
#  define CADET_COMPILER_VERSION_MAJOR (__GNUC__)
# else
#  define CADET_COMPILER_VERSION_MAJOR (__GNUG__)
# endif
# if defined(__GNUC_MINOR__)
#  define CADET_COMPILER_VERSION_MINOR (__GNUC_MINOR__)
# endif
# if defined(__GNUC_PATCHLEVEL__)
#  define CADET_COMPILER_VERSION_PATCH (__GNUC_PATCHLEVEL__)
# endif

#    if (__GNUC__ * 100 + __GNUC_MINOR__) >= 406 && (__cplusplus >= 201103L || (defined(__GXX_EXPERIMENTAL_CXX0X__) && __GXX_EXPERIMENTAL_CXX0X__))
#      define CADET_COMPILER_CXX_NOEXCEPT 1
#    else
#      define CADET_COMPILER_CXX_NOEXCEPT 0
#    endif

#    if (__GNUC__ * 100 + __GNUC_MINOR__) >= 407 && __cplusplus >= 201103L
#      define CADET_COMPILER_CXX_USER_LITERALS 1
#    else
#      define CADET_COMPILER_CXX_USER_LITERALS 0
#    endif

#    if (__GNUC__ * 100 + __GNUC_MINOR__) >= 406 && (__cplusplus >= 201103L || (defined(__GXX_EXPERIMENTAL_CXX0X__) && __GXX_EXPERIMENTAL_CXX0X__))
#      define CADET_COMPILER_CXX_CONSTEXPR 1
#    else
#      define CADET_COMPILER_CXX_CONSTEXPR 0
#    endif

#    if (__GNUC__ * 100 + __GNUC_MINOR__) >= 404 && (__cplusplus >= 201103L || (defined(__GXX_EXPERIMENTAL_CXX0X__) && __GXX_EXPERIMENTAL_CXX0X__))
#      define CADET_COMPILER_CXX_VARIADIC_TEMPLATES 1
#    else
#      define CADET_COMPILER_CXX_VARIADIC_TEMPLATES 0
#    endif

#  elif CADET_COMPILER_IS_Clang

#    if !(((__clang_major__ * 100) + __clang_minor__) >= 301)
#      error Unsupported compiler version
#    endif

# define CADET_COMPILER_VERSION_MAJOR (__clang_major__)
# define CADET_COMPILER_VERSION_MINOR (__clang_minor__)
# define CADET_COMPILER_VERSION_PATCH (__clang_patchlevel__)
# if defined(_MSC_VER)
   /* _MSC_VER = VVRR */
#  define CADET_SIMULATE_VERSION_MAJOR (_MSC_VER / 100)
#  define CADET_SIMULATE_VERSION_MINOR (_MSC_VER % 100)
# endif

#    if ((__clang_major__ * 100) + __clang_minor__) >= 301 && __has_feature(cxx_noexcept)
#      define CADET_COMPILER_CXX_NOEXCEPT 1
#    else
#      define CADET_COMPILER_CXX_NOEXCEPT 0
#    endif

#    if ((__clang_major__ * 100) + __clang_minor__) >= 301 && __has_feature(cxx_user_literals)
#      define CADET_COMPILER_CXX_USER_LITERALS 1
#    else
#      define CADET_COMPILER_CXX_USER_LITERALS 0
#    endif

#    if ((__clang_major__ * 100) + __clang_minor__) >= 301 && __has_feature(cxx_constexpr)
#      define CADET_COMPILER_CXX_CONSTEXPR 1
#    else
#      define CADET_COMPILER_CXX_CONSTEXPR 0
#    endif

#    if ((__clang_major__ * 100) + __clang_minor__) >= 301 && __has_feature(cxx_variadic_templates)
#      define CADET_COMPILER_CXX_VARIADIC_TEMPLATES 1
#    else
#      define CADET_COMPILER_CXX_VARIADIC_TEMPLATES 0
#    endif

#  elif CADET_COMPILER_IS_AppleClang

#    if !(((__clang_major__ * 100) + __clang_minor__) >= 400)
#      error Unsupported compiler version
#    endif

# define CADET_COMPILER_VERSION_MAJOR (__clang_major__)
# define CADET_COMPILER_VERSION_MINOR (__clang_minor__)
# define CADET_COMPILER_VERSION_PATCH (__clang_patchlevel__)
# if defined(_MSC_VER)
   /* _MSC_VER = VVRR */
#  define CADET_SIMULATE_VERSION_MAJOR (_MSC_VER / 100)
#  define CADET_SIMULATE_VERSION_MINOR (_MSC_VER % 100)
# endif
# define CADET_COMPILER_VERSION_TWEAK (__apple_build_version__)

#    if ((__clang_major__ * 100) + __clang_minor__) >= 400 && __has_feature(cxx_noexcept)
#      define CADET_COMPILER_CXX_NOEXCEPT 1
#    else
#      define CADET_COMPILER_CXX_NOEXCEPT 0
#    endif

#    if ((__clang_major__ * 100) + __clang_minor__) >= 400 && __has_feature(cxx_user_literals)
#      define CADET_COMPILER_CXX_USER_LITERALS 1
#    else
#      define CADET_COMPILER_CXX_USER_LITERALS 0
#    endif

#    if ((__clang_major__ * 100) + __clang_minor__) >= 400 && __has_feature(cxx_constexpr)
#      define CADET_COMPILER_CXX_CONSTEXPR 1
#    else
#      define CADET_COMPILER_CXX_CONSTEXPR 0
#    endif

#    if ((__clang_major__ * 100) + __clang_minor__) >= 400 && __has_feature(cxx_variadic_templates)
#      define CADET_COMPILER_CXX_VARIADIC_TEMPLATES 1
#    else
#      define CADET_COMPILER_CXX_VARIADIC_TEMPLATES 0
#    endif

#  elif CADET_COMPILER_IS_MSVC

#    if !(_MSC_VER >= 1600)
#      error Unsupported compiler version
#    endif

  /* _MSC_VER = VVRR */
# define CADET_COMPILER_VERSION_MAJOR (_MSC_VER / 100)
# define CADET_COMPILER_VERSION_MINOR (_MSC_VER % 100)
# if defined(_MSC_FULL_VER)
#  if _MSC_VER >= 1400
    /* _MSC_FULL_VER = VVRRPPPPP */
#   define CADET_COMPILER_VERSION_PATCH (_MSC_FULL_VER % 100000)
#  else
    /* _MSC_FULL_VER = VVRRPPPP */
#   define CADET_COMPILER_VERSION_PATCH (_MSC_FULL_VER % 10000)
#  endif
# endif
# if defined(_MSC_BUILD)
#  define CADET_COMPILER_VERSION_TWEAK (_MSC_BUILD)
# endif

#    if _MSC_VER >= 1900
#      define CADET_COMPILER_CXX_NOEXCEPT 1
#    else
#      define CADET_COMPILER_CXX_NOEXCEPT 0
#    endif

#    if _MSC_VER >= 1900
#      define CADET_COMPILER_CXX_USER_LITERALS 1
#    else
#      define CADET_COMPILER_CXX_USER_LITERALS 0
#    endif

#    if _MSC_VER >= 1900
#      define CADET_COMPILER_CXX_CONSTEXPR 1
#    else
#      define CADET_COMPILER_CXX_CONSTEXPR 0
#    endif

#    if _MSC_VER >= 1800
#      define CADET_COMPILER_CXX_VARIADIC_TEMPLATES 1
#    else
#      define CADET_COMPILER_CXX_VARIADIC_TEMPLATES 0
#    endif

#  elif CADET_COMPILER_IS_Intel

#    if !(__INTEL_COMPILER >= 1210)
#      error Unsupported compiler version
#    endif

  /* __INTEL_COMPILER = VRP prior to 2021, and then VVVV for 2021 and later,
     except that a few beta releases use the old format with V=2021.  */
# if __INTEL_COMPILER < 2021 || __INTEL_COMPILER == 202110 || __INTEL_COMPILER == 202111
#  define CADET_COMPILER_VERSION_MAJOR (__INTEL_COMPILER/100)
#  define CADET_COMPILER_VERSION_MINOR (__INTEL_COMPILER/10 % 10)
#  if defined(__INTEL_COMPILER_UPDATE)
#   define CADET_COMPILER_VERSION_PATCH (__INTEL_COMPILER_UPDATE)
#  else
#   define CADET_COMPILER_VERSION_PATCH (__INTEL_COMPILER   % 10)
#  endif
# else
#  define CADET_COMPILER_VERSION_MAJOR (__INTEL_COMPILER)
#  define CADET_COMPILER_VERSION_MINOR (__INTEL_COMPILER_UPDATE)
   /* The third version component from --version is an update index,
      but no macro is provided for it.  */
#  define CADET_COMPILER_VERSION_PATCH (0)
# endif
# if defined(__INTEL_COMPILER_BUILD_DATE)
   /* __INTEL_COMPILER_BUILD_DATE = YYYYMMDD */
#  define CADET_COMPILER_VERSION_TWEAK (__INTEL_COMPILER_BUILD_DATE)
# endif
# if defined(_MSC_VER)
   /* _MSC_VER = VVRR */
#  define CADET_SIMULATE_VERSION_MAJOR (_MSC_VER / 100)
#  define CADET_SIMULATE_VERSION_MINOR (_MSC_VER % 100)
# endif
# if defined(__GNUC__)
#  define CADET_SIMULATE_VERSION_MAJOR (__GNUC__)
# elif defined(__GNUG__)
#  define CADET_SIMULATE_VERSION_MAJOR (__GNUG__)
# endif
# if defined(__GNUC_MINOR__)
#  define CADET_SIMULATE_VERSION_MINOR (__GNUC_MINOR__)
# endif
# if defined(__GNUC_PATCHLEVEL__)
#  define CADET_SIMULATE_VERSION_PATCH (__GNUC_PATCHLEVEL__)
# endif

#    if __INTEL_COMPILER >= 1400 && ((__cplusplus >= 201103L) || defined(__INTEL_CXX11_MODE__) || defined(__GXX_EXPERIMENTAL_CXX0X__))
#      define CADET_COMPILER_CXX_NOEXCEPT 1
#    else
#      define CADET_COMPILER_CXX_NOEXCEPT 0
#    endif

#    if __cpp_user_defined_literals >= 200809 || (__INTEL_COMPILER >= 1500 && ((__cplusplus >= 201103L) || defined(__INTEL_CXX11_MODE__) || defined(__GXX_EXPERIMENTAL_CXX0X__)) && (!defined(_MSC_VER) || __INTEL_COMPILER >= 1600))
#      define CADET_COMPILER_CXX_USER_LITERALS 1
#    else
#      define CADET_COMPILER_CXX_USER_LITERALS 0
#    endif

#    if __cpp_constexpr >= 200704 || __INTEL_COMPILER >= 1400 && ((__cplusplus >= 201103L) || defined(__INTEL_CXX11_MODE__) || defined(__GXX_EXPERIMENTAL_CXX0X__))
#      define CADET_COMPILER_CXX_CONSTEXPR 1
#    else
#      define CADET_COMPILER_CXX_CONSTEXPR 0
#    endif

#    if (__cpp_variadic_templates >= 200704 || __INTEL_COMPILER >= 1210) && ((__cplusplus >= 201103L) || defined(__INTEL_CXX11_MODE__) || defined(__GXX_EXPERIMENTAL_CXX0X__))
#      define CADET_COMPILER_CXX_VARIADIC_TEMPLATES 1
#    else
#      define CADET_COMPILER_CXX_VARIADIC_TEMPLATES 0
#    endif

#  else
#    error Unsupported compiler
#  endif

#  if defined(CADET_COMPILER_CXX_NOEXCEPT) && CADET_COMPILER_CXX_NOEXCEPT
#    define CADET_NOEXCEPT noexcept
#    define CADET_NOEXCEPT_EXPR(X) noexcept(X)
#  else
#    define CADET_NOEXCEPT
#    define CADET_NOEXCEPT_EXPR(X)
#  endif


#  if defined(CADET_COMPILER_CXX_CONSTEXPR) && CADET_COMPILER_CXX_CONSTEXPR
#    define CADET_CONSTEXPR constexpr
#  else
#    define CADET_CONSTEXPR 
#  endif

#endif

#if CADET_COMPILER_CXX_CONSTEXPR
	#define CADET_CONST_OR_CONSTEXPR constexpr
#else
	#define CADET_CONST_OR_CONSTEXPR const
#endif
#if CADET_COMPILER_CXX_USER_LITERALS && CADET_COMPILER_CXX_CONSTEXPR
	#define CADET_COMPILETIME_HASH 1
#else
	#define CADET_COMPILETIME_HASH 0
#endif


#endif
