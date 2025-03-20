/*****************************************************************************
*
* ALPS Project: Algorithms and Libraries for Physics Simulations
*
* ALPS Libraries
*
* Copyright (C) 1994-2003 by Matthias Troyer <troyer@itp.phys.ethz.ch>
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

/* $Id$ */

//=======================================================================
// This file defines the simulation specific classes for a simple
// simulation of a one-dimensional Ising model
//=======================================================================

#include <alps/scheduler/montecarlo.h>

typedef boost::adjacency_list<boost::vecS,boost::vecS,boost::undirectedS,
                              // vertex property
                              boost::property<alps::vertex_type_t,unsigned int>,
                              // edge property
                              boost::property<alps::edge_type_t,unsigned int, boost::property<alps::edge_index_t, unsigned int> >
                              > graph_type;

class IsingSimulation2 : public alps::scheduler::LatticeMCRun<graph_type>
{
public:
  static void print_copyright(std::ostream&);

  IsingSimulation2(const alps::ProcessList&,const alps::Parameters&,int);
  void save(alps::ODump&) const;
  void load(alps::IDump&);
  void dostep();
  bool is_thermalized() const;
  double work_done() const;
  bool change_parameter(const std::string& name, const alps::StringValue& value);

private:
  double beta;                      // the inverse temperature
  boost::uint32_t sweeps;                  // the number of sweeps done
  boost::uint32_t thermalization_sweeps;   // the number of sweeps to be done for equilibration
  boost::uint32_t total_sweeps;            // the total number of sweeps to be done after equilibration
  std::vector<int> spins;           // the vector to store the spins
};

typedef alps::scheduler::SimpleMCFactory<IsingSimulation2> IsingFactory2;
