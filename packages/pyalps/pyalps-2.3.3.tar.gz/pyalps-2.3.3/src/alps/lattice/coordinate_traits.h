/*****************************************************************************
*
* ALPS Project: Algorithms and Libraries for Physics Simulations
*
* ALPS Libraries
*
* Copyright (C) 2001-2002 by Matthias Troyer <troyer@itp.phys.ethz.ch>,
*                            Synge Todo <wistaria@comp-phys.org>
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

#ifndef ALPS_LATTICE_COORDINATE_TRAITS_H
#define ALPS_LATTICE_COORDINATE_TRAITS_H

#include <alps/config.h>
#include <algorithm>
#include <iomanip>
#include <sstream>
#include <valarray>

namespace alps {

template <class C>
struct coordinate_traits {
  typedef typename C::value_type value_type;
  typedef typename C::iterator iterator;
  typedef typename C::const_iterator const_iterator;
};
  
template <class C>
struct coordinate_traits<const C> {
  typedef typename C::value_type value_type;
  typedef typename C::const_iterator iterator;
  typedef typename C::const_iterator const_iterator;
};
  
template <class C>
inline std::pair<typename coordinate_traits<C>::iterator, typename coordinate_traits<C>::iterator>
coordinates(C& c)
{
  return std::make_pair(c.begin(),c.end());
}

template <class T, int sz>
struct coordinate_traits<T[sz]> {
  typedef T value_type;
  typedef T* iterator;
  typedef const T* const_iterator;
};
  
/*
template <class T, int sz>
inline std::pair<T*, T*>
coordinates(T[sz]& c)
{
  return std::make_pair(c,c+sz);
}

template <class T, int sz>
inline std::pair<const T*, const T*>
coordinates(const T[sz]& c)
{
  return std::make_pair(c,c+sz);
}
*/

template <class T>
struct coordinate_traits<std::valarray<T> > {
  typedef T value_type;
  typedef T* iterator;
  typedef const T* const_iterator;
};
  
template <class T>
inline std::pair<T*, T*>
coordinates(std::valarray<T>& c)
{
  return make_pair(&(c[0]),&(c[0])+c.size());
}

template <class T>
inline std::pair<const T*, const T*>
coordinates(const std::valarray<T>& c)
{
  return std::pair<const T*, const T*>
    (&(const_cast<std::valarray<T>&>(c)[0]),
    &(const_cast<std::valarray<T>&>(c)[0])+c.size());
}


template <class C>
std::string coordinate_to_string(const C& c, int precision = 0)
{
  std::ostringstream str;
  str << "( ";
  if (precision > 0) str << std::setprecision(precision);
  int n=0;
  typename coordinate_traits<C>::const_iterator first, last;
  for (boost::tie(first,last) = coordinates(c); first != last; ++first, ++n) {
    if (n) str << ',';
    str << *first;
  }
  str << " )";
  return str.str();
} 

} // end namespace alps

#endif // ALPS_LATTICE_COORDINATE_TRAITS_H
