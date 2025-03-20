/*****************************************************************************
*
* ALPS Project Applications
*
* Copyright (C) 2001-2004 by Matthias Troyer <troyer@comp-phys.org>,
*                            Simon Trebst <trebst@comp-phys.org>
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

#ifndef TIME_STRUCT_H___
#define TIME_STRUCT_H___

#include <alps/osiris.h>
#include <cmath>

class time_struct {
public:
  time_struct(double t=0.) : t_(checkfull(t)) {}
  const time_struct& operator=(double t) { t_=checkfull(t); return *this;}
  operator double() const { return t_;}
  time_struct operator-(double t) const { return time_struct(checkone(t_-t),0);}
  time_struct operator+(double t) const { return time_struct(checkone(t_+t),0);}
  double operator-(time_struct t) const { return t>=t_ ? t_-t+1. : t_-t;}

private:
  time_struct(double t,int) : t_(t) {}
  double checkfull(double t) const { return t>0. ? std::fmod(t,1.) : std::fmod(t,1.)+1.;}
  double checkone(double t) const {return t<=0. ? t+1. : (t>=1. ? t-1. : t);}
  double t_;
};

inline alps::ODump& operator << (alps::ODump& dump, const time_struct& t) {
  return dump << double(t);
}

inline alps::IDump& operator >> (alps::IDump& dump, time_struct& t) {
  double td;
  dump >> td;
  t=td;
  return dump;
}

#endif

