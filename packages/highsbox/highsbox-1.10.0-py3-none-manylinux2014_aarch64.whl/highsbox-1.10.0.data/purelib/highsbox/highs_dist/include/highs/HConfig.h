#ifndef HCONFIG_H_
#define HCONFIG_H_

#define FAST_BUILD
#define ZLIB_FOUND
#define CUPDLP_CPU
/* #undef CUPDLP_GPU */
/* #undef CUPDLP_FORCE_NATIVE */
#define CMAKE_BUILD_TYPE "Release"
#define CMAKE_INSTALL_PREFIX "/project/HiGHS/highs_dist"
/* #undef HIGHSINT64 */
/* #undef HIGHS_NO_DEFAULT_THREADS */
/* #undef HIGHS_HAVE_MM_PAUSE */
#define HIGHS_HAVE_BUILTIN_CLZ
/* #undef HIGHS_HAVE_BITSCAN_REVERSE */

#define HIGHS_GITHASH "fd86653"
#define HIGHS_VERSION_MAJOR 1
#define HIGHS_VERSION_MINOR 10
#define HIGHS_VERSION_PATCH 0
#define HIGHS_DIR "/project/HiGHS"

#endif /* HCONFIG_H_ */
