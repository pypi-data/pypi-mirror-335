/*****************************************************************************
 *
 * ALPS MPS DMRG Project
 *
 * Copyright (C) 2013 Institute for Theoretical Physics, ETH Zurich
 *               2012-2013 by Michele Dolfi <dolfim@phys.ethz.ch>
 * 
* Permission is hereby granted, free of charge, to any person obtaining
* a copy of this software and associated documentation files (the “Software”),
* to deal in the Software without restriction, including without limitation
* the rights to use, copy, modify, merge, publish, distribute, sublicense,
* and/or sell copies of the Software, and to permit persons to whom the
* Software is furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included
* in all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
* OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
* FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
* DEALINGS IN THE SOFTWARE.
 *
 *****************************************************************************/

#ifndef MAQUIS_DMRG_STATE_MPS_H
#define MAQUIS_DMRG_STATE_MPS_H

#include "dmrg/mp_tensors/mps.h"

#include <boost/tuple/tuple.hpp>

template <class Matrix, class SymmGroup, class Charge>
MPS<Matrix, SymmGroup> state_mps(std::vector<boost::tuple<Charge, std::size_t> > const & state,
                                 std::vector<Index<SymmGroup> > const& phys_dims, std::vector<int> const& site_type)
{
    typedef typename SymmGroup::charge charge;
    typedef boost::tuple<charge, size_t> local_state;
    
    MPS<Matrix, SymmGroup> mps(state.size());
    
    Index<SymmGroup> curr_i;
    curr_i.insert(std::make_pair(SymmGroup::IdentityCharge, 1));
    size_t curr_b = 0;
    for (int i=0; i<state.size(); ++i)
    {
        charge newc = SymmGroup::fuse(curr_i[0].first, boost::get<0>(state[i]));
        size_t news = 1;
        Index<SymmGroup> new_i;
        new_i.insert(std::make_pair(newc, news));
        ProductBasis<SymmGroup> left(phys_dims[site_type[i]], curr_i);
        mps[i] = MPSTensor<Matrix, SymmGroup>(phys_dims[site_type[i]], curr_i, new_i, false, 0);
        size_t b_in = left(boost::get<0>(state[i]), curr_i[0].first) + boost::get<1>(state[i]) * curr_i[0].second + curr_b;
        size_t b_out = 0;
        
        mps[i].make_left_paired();
        block_matrix<Matrix, SymmGroup> & block = mps[i].data();
        Matrix & m = block(SymmGroup::fuse(curr_i[0].first, boost::get<0>(state[i])), new_i[0].first);
        m(b_in, b_out) = 1.;
        
        curr_i = new_i;
        curr_b = b_out;
    }
    return mps;
}


#endif
