#===============================================================================
# Copyright 2019 Intel Corporation
#
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# 
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.
#
#===============================================================================

include_guard()

include("${CMAKE_CURRENT_LIST_DIR}/IPPPathLayout.cmake")

macro (ipp_getlibversion VERSION_FILE)
    unset(IPP_VERSION_MAJOR)
    unset(IPP_VERSION_MINOR)
    unset(IPP_VERSION_UPDATE)
    unset(IPP_VERSION)
    unset(IPP_INTERFACE_VERSION_MAJOR)
    unset(IPP_INTERFACE_VERSION_MINOR)
    file(STRINGS "${VERSION_FILE}" FILE_CONTENTS)
    foreach (LINE ${FILE_CONTENTS})
        if (${LINE} MATCHES "#define IPP_VERSION_MAJOR")
            string(REGEX REPLACE "^#define +IPP_VERSION_MAJOR +\([0-9]+\).*$" "\\1"
                                 IPP_VERSION_MAJOR ${LINE})
        endif ()
        if (${LINE} MATCHES "#define IPP_VERSION_MINOR")
            string(REGEX REPLACE "^#define +IPP_VERSION_MINOR +\([0-9]+\).*$" "\\1"
                                 IPP_VERSION_MINOR ${LINE})
        endif ()
        if (${LINE} MATCHES "#define IPP_VERSION_UPDATE")
            string(REGEX REPLACE "^#define +IPP_VERSION_UPDATE +\([0-9]+\).*$" "\\1"
                                 IPP_VERSION_UPDATE ${LINE})
        endif ()
        if (${LINE} MATCHES "#define IPP_INTERFACE_VERSION_MAJOR")
            string(REGEX REPLACE "^#define +IPP_INTERFACE_VERSION_MAJOR +\([0-9]+\).*$" "\\1"
                                 IPP_INTERFACE_VERSION_MAJOR ${LINE})
        endif ()
        if (${LINE} MATCHES "#define IPP_INTERFACE_VERSION_MINOR")
            string(REGEX REPLACE "^#define +IPP_INTERFACE_VERSION_MINOR +\([0-9]+\).*$" "\\1"
                                 IPP_INTERFACE_VERSION_MINOR ${LINE})
        endif ()
    endforeach ()
    set(IPP_VERSION "${IPP_VERSION_MAJOR}.${IPP_VERSION_MINOR}.${IPP_VERSION_UPDATE}")
    set(IPP_INTERFACE_VERSION "${IPP_INTERFACE_VERSION_MAJOR}.${IPP_INTERFACE_VERSION_MINOR}")
    unset(FILE_CONTENTS)
endmacro (ipp_getlibversion)

ipp_getlibversion("${CMAKE_CURRENT_LIST_DIR}/${IPP_INC_REL_PATH}/ipp/ippversion.h")
if ((NOT DEFINED IPP_VERSION_MAJOR)
    OR (NOT DEFINED IPP_VERSION_MINOR)
    OR (NOT DEFINED IPP_VERSION_UPDATE)
    OR (NOT DEFINED IPP_INTERFACE_VERSION_MAJOR)
    OR (NOT DEFINED IPP_INTERFACE_VERSION_MINOR))
    message(WARNING "Cannot parse version from ippversion.h file. The project might be corrupted.")
endif ()
