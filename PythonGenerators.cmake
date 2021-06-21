function(source_files_searcher ENTRY DIRS OUTPUT PREFIX EXCLUDES)
    find_package(Python3)
    if (Python3_FOUND)

        if (NOT ${EXCLUDES} STREQUAL "")
            set(PARAMS --entry ${ENTRY} --dirs ${DIRS} --excludes ${EXCLUDES} -o ${OUTPUT})
        else ()
            set(PARAMS --entry ${ENTRY} --dirs ${DIRS} -o ${OUTPUT})
        endif ()

        if (NOT ${PREFIX} STREQUAL "")
            set(PARAMS ${PARAMS} --prefix ${PREFIX})
        endif ()

        execute_process(
                COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/Helpers/included_files_searcher.py" ${PARAMS}
                RESULT_VARIABLE res_var
        )
        if(NOT "${res_var}" STREQUAL "0")
            message(FATAL_ERROR "Generation of '${OUTPUT}' process failed with code res_var='${res_var}'")
        endif()

    else ()
        message(FATAL_ERROR "Python3 requested but executable not found")
    endif ()
endfunction()
