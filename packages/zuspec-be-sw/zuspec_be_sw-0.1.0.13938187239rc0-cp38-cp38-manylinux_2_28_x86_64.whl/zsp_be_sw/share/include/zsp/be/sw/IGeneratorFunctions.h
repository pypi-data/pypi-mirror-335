/**
 * IGeneratorFunctions.h
 *
 * Copyright 2022 Matthew Ballance and Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may 
 * not use this file except in compliance with the License.  
 * You may obtain a copy of the License at:
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software 
 * distributed under the License is distributed on an "AS IS" BASIS, 
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
 * See the License for the specific language governing permissions and 
 * limitations under the License.
 *
 * Created on:
 *     Author: 
 */
#pragma once
#include <memory>
#include <vector>
#include "zsp/arl/dm/IContext.h"
#include "zsp/arl/dm/IDataTypeFunction.h"
#include "zsp/be/sw/IOutput.h"

namespace zsp {
namespace be {
namespace sw {


class IGeneratorFunctions;
using IGeneratorFunctionsUP=std::unique_ptr<IGeneratorFunctions>;
class IGeneratorFunctions {
public:

    virtual ~IGeneratorFunctions() { }

    virtual void generate(
        arl::dm::IContext                                   *ctxt,
        const std::vector<arl::dm::IDataTypeFunction *>     &funcs,
        const std::vector<std::string>                      &inc_c,
        const std::vector<std::string>                      &inc_h,
        IOutput                                             *out_c,
        IOutput                                             *out_h
    ) = 0;

};

} /* namespace sw */
} /* namespace be */
} /* namespace zsp */


