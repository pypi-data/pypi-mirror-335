# Copyright (2025) Beijing Volcano Engine Technology Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .._future import SubOptions

def density_fit(mf, auxbasis=None):
    class DFHF(mf.__class__):
        _keys = {'with_df'}
        _methods = mf.__class__._methods + ['.density_fit']

        def to_cpu(self):
            return super().to_cpu().density_fit()

    new_mf = object.__new__(DFHF)
    new_mf.__dict__.update(mf.__dict__)
    new_mf.with_df = DF()
    if auxbasis is not None:
        new_mf.with_df.auxbasis = auxbasis
    return new_mf

class DF(SubOptions):
    _keys = {'auxbasis'}
