#include <iostream>
#include <boost/python.hpp>
#include <map>
#include <string>
#include <exception>
#include <stdexcept>
#include "pyutil.hpp"

using namespace std;
using namespace boost::python;

struct Vec4d
{
  double values[4];

  Vec4d()
  {
    for(int iter = 0; iter < 4; ++iter)
      values[iter] = 0;
  }

  double dist(const Vec4d&o) const
  {
    double ssd = 0;
    for(int iter = 0; iter < 4; ++iter)
    {
      double diff = (values[iter] - o.values[iter]);
      ssd += diff * diff;
    }
    return ssd;
  }
};

std::ostream& operator<<(ostream&os, const Vec4d&o) 
{
  os << "[" << o.values[0] << ", " << o.values[1] << ", " << o.values[2] << ", " << o.values[3] << "] ";
  return os;
}

#include "eval_ik.cpp"

bool strhas(const string&str,const string&has)
{
  return str.find(has) != std::string::npos;
}

class IK
{
public:
  map<string,double> null_solution;
  map<string,double> regularizers;
  float step_size;
  
  IK()
  {
  }
  
  double objective_cost(map<string,Vec4d>&target_positions,map<string,double>&solution)
  {
    // compute target component
    double ssd = 0;
    for(auto && targ : target_positions)
    {
      Vec4d cur = joint_position(targ.first,solution);
      ssd += cur.dist(targ.second);
    }

    // compute the reguarizer cost.
    for(auto && param : solution)
    {
      auto null_value = null_solution.find(param.first);
      if(null_value != null_solution.end())
      {
	double C = regularizers[param.first];
	double diff = null_value->second - param.second;
	ssd += C * diff * diff;
      }
    }
    
    return ssd;
  }

  map<string,double> perturb_solution_random(const map<string,double>&solution)
  {
    map<string,double> sol_prime = solution;
    static std::default_random_engine generator;
    static std::normal_distribution<double> distribution(0,1.0);

    int param_id = rand() % sol_prime.size();
    int iter =0;
    for(auto && param : sol_prime)
    {
      if(iter == param_id)
	param.second += distribution(generator);
      ++iter;
    }
    
    return sol_prime;
  }

  map<string,double> perturb_solution_gradient(map<string,Vec4d>&targets,map<string,double>&solution)
  {
    map<string,double> sp;
    
    for(auto && param : solution)
    {        
      // data gradient
      double grad = 0;
      for(auto && target : targets)
      {
	Vec4d cur_pos = joint_position(target.first,solution);
	for(int i = 0; i < 4; ++i)
	{
	  grad += 2 * (cur_pos.values[i] - target.second.values[i]) * diff(target.first,param.first,i,solution);
	}
      }
      
      // regularizer gradient
      auto null_value = null_solution.at(param.first);	
      double C = regularizers.at(param.first);
      double diff = null_value - param.second;
      grad += C * -2 * diff;

      // update
      sp[param.first] = param.second - step_size*grad;
    }

    return sp;
  }

  map<string,double> perturb_solution(map<string,Vec4d>&target,map<string,double>&solution)
  {
    static long ctr = 0;
    ctr++;
    if(ctr % 500 == 0)
      return perturb_solution_gradient(target,solution);
    else
      return perturb_solution_random(solution);
  }  

  void print_match(map<string,Vec4d>&target_positions,map<string,double>&solution)
  {
    for(auto && targ : target_positions)
    {
      Vec4d cur = joint_position(targ.first,solution);
      cout << targ.first << targ.second << " vs " << cur << endl;
    }
  }

  map<string,double> extract_solution(boost::python::dict pySol)
  {
    boost::python::list sol_keys = pySol.keys();
    map<string,double> sol;
    for(int iter = 0; iter < len(sol_keys); ++iter)
    {
      boost::python::extract<std::string> key(sol_keys[iter]);
      boost::python::extract<double> value(pySol[sol_keys[iter]]);
      sol[key] = value;
    }
    return sol;
  }

  map<string,Vec4d> extract_targets(boost::python::dict target_positions)
  {
    boost::python::list target_keys = target_positions.keys();
    map<string,Vec4d> target;
    for( int iter = 0; iter < len(target_keys); ++iter)
    {
      boost::python::extract<std::string> key(target_keys[iter]);
      boost::python::list value = boost::python::extract<boost::python::list>(target_positions[target_keys[iter]]);
      Vec4d v;
      assert(len(value) == 4);
      for(int jter = 0; jter < len(value); ++jter)
	v.values[jter] = boost::python::extract<double>(value[jter]);
      target[key] = v;
    }
    return target;
  }
  
  void set_null_solution(boost::python::dict null_solution)
  {
    // convert init solution
    this->null_solution = extract_solution(null_solution);
  }

  void set_regularizers(boost::python::dict py_reguarizers)
  {
    // convert init solution
    this->regularizers = extract_solution(py_reguarizers);
  }  

  void optimize(map<string,Vec4d>&target,map<string,double>&sol)
  {
    ScopedGILRelease unlock;
    
    double start_cost = objective_cost(target,sol);
    double best_cost = start_cost;
    cout << "init cost = " << best_cost << endl;
    int max_iter = 1000;
    for(int iter = 0; iter < max_iter; ++iter)
    {
      auto sol_prime = perturb_solution(target,sol);
      double cost_prime = objective_cost(target,sol_prime);
      if(cost_prime < best_cost)
      {
	cout << "ACCEPT: " << best_cost << " => " << cost_prime << endl;
	sol = sol_prime;
	best_cost = cost_prime;
      }
      else if(iter % 100 == 0)
      {
	cout << "REJECT: " << best_cost << " => " << cost_prime << endl;
      }

      if(iter % 1000 == 0)
      {
	cout << "iter " << iter << " of " << 50000 << endl;
      }
    }
    
    print_match(target,sol);
    cout << "init cost = " << start_cost << endl;    
    cout << "final cost = " << objective_cost(target,sol) << endl;
  }
  
  boost::python::dict solve(boost::python::dict target_positions,boost::python::dict init_solution)
  {   
    // convert arguments
    map<string,Vec4d> target = extract_targets(target_positions);

    // convert init solution
    map<string,double> sol = extract_solution(init_solution);

    // OPTIMIZE THE DAMN THING!!!
    {      
      optimize(target,sol);
    }
    
    // convert to output
    boost::python::dict dictionary;
    for(auto && param : sol)
    {
      dictionary[param.first] = param.second;
    }
    return dictionary;
  }

  void set_grad_step_size(float s)
  {
    step_size = s;
  }
};

BOOST_PYTHON_MODULE(iksolver)
{
  class_<IK>("iksolver", init<>())
    .def(init<>())
    .def("solve", &IK::solve)
    .def("set_null_solution",&IK::set_null_solution)
    .def("set_regularizers",&IK::set_regularizers)
    .def("set_grad_step_size",&IK::set_grad_step_size);
}
