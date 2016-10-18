# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 10:12:07 2016

@author: ryandrewjones
"""

import config as cfg
#import util
#import numpy as np
#from dispatch_classes import Dispatch

def process_shapes(shape):
    cfg.initialize_config(shape.workingdir, shape.cfgfile_name, shape.pint_definitions_file, shape.log_name)
    shape.process_shape()
    cfg.cur.close()
    return shape

def node_calculate(node):
    cfg.initialize_config(node.workingdir, node.cfgfile_name, node.pint_definitions_file, node.log_name)
    node.calculate()
    cfg.cur.close()
    return node

def subsector_calculate(subsector):
    if not subsector.calculated:
        cfg.initialize_config(subsector.workingdir, subsector.cfgfile_name, subsector.pint_definitions_file, subsector.log_name)
        subsector.calculate()
        cfg.cur.close()
    return subsector

def subsector_populate(subsector):
    cfg.initialize_config(subsector.workingdir, subsector.cfgfile_name, subsector.pint_definitions_file, subsector.log_name)
    subsector.add_energy_system_data()
    cfg.cur.close()
    return subsector


def aggregate_subsector_shapes(params):
    subsector = params[0]
    year = params[1]    
    cfg.initialize_config(subsector.workingdir, subsector.cfgfile_name, subsector.pint_definitions_file, subsector.log_name)
    aggregate_electricity_shape = subsector.aggregate_electricity_shapes(year)
    cfg.cur.close()    
    return aggregate_electricity_shape

def aggregate_sector_shapes(params):
    sector = params[0]
    year = params[1]    
    cfg.initialize_config(sector.workingdir, sector.cfgfile_name, sector.pint_definitions_file, sector.log_name)
    aggregate_electricity_shape = sector.aggregate_inflexible_electricity_shape(year)
    cfg.cur.close()
    return aggregate_electricity_shape