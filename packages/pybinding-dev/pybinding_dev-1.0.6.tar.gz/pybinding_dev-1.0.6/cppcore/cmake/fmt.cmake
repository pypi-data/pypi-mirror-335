download_dependency(fmt 11.1.4 https://raw.githubusercontent.com/fmtlib/fmt/\${VERSION}
                    include/fmt/format.h
                    src/format.cc
                    include/fmt/format-inl.h
                    include/fmt/ostream.h
                    include/fmt/base.h
                    include/fmt/chrono.h)

add_library(fmt STATIC EXCLUDE_FROM_ALL
            ${FMT_INCLUDE_DIR}/src/format.cc)
target_include_directories(fmt SYSTEM PUBLIC ${FMT_INCLUDE_DIR}/include)
set_target_properties(fmt PROPERTIES POSITION_INDEPENDENT_CODE TRUE)
