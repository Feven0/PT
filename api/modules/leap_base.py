import os, sys
import re
import copy
import json
from datetime import datetime, timedelta
import pandas as pd
import boto3
import requests

from .pathfig import *

from api import config
from api.services.strapi_graphql import StrapiGraphql
from api.services.strapi_methods import StrapiMethods
import api.utils.aws_utils as awsut
from api.utils import camel_to_snake
from api.modules.utils.utils import measure_execution_time
#

from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))

#
capitalize = lambda x: x[0].upper() + x[1:]


    
class LeapBaseClass:
    def __init__(self, **kwargs) -> None:
        log_level = kwargs.get('log_level', None)
        
        #          
        if log_level and isinstance(log_level, int):
            logger._logger.setLevel(log_level) 
                    
        if config.strapi.stage=='dev':
            self.run_stage =  kwargs.get('run_stage',config.strapi.stage)
        else:
            self.run_stage = config.strapi.stage
        self.user_token = kwargs.get('strapi_token', kwargs.get('user_token', ""))
        self.strapi_token = self.user_token
        self.user_role = kwargs.get('user_role', "")
                                
        self.kwargs = kwargs
        self.sg = StrapiGraphql(**kwargs)
        self.verbose = kwargs.get('verbose', 0)
        self.data = kwargs.get('data', "")
        self.table = kwargs.get('table', "")
        self.table_single = kwargs.get('table_single', "")
        self.tosingle = lambda x: x[:-1] if x[-1]=='s' else x
        self.type_map = kwargs.get('type_map', {})
        self.relation_map = kwargs.get('relation_map', {})
        self.id_names_map = kwargs.get('id_names_map', {})
        self.output_variables = kwargs.get('output_variables', [])
        self.enum_map = {}
        
        #
        self.sns = awsut.sns
        self.sqs = awsut.sqs
        self.sns_link = awsut.sns_link
        self.sqs_link = awsut.sqs_link
        self.publish_to_sns = awsut.publish_to_sns
        self.publish_to_sqs = awsut.publish_to_sqs
              
            
    def _get_value(self, res, key, single=False, default="", **kwargs):

        if isinstance(res, dict):
            return res.get(key, "")
        elif isinstance(res, pd.Series):
            return res.get(key, "")
        elif isinstance(res, list):
            output = []
            out = ""
            for r in res:
                if isinstance(r, (list, tuple)):
                    out = self._get_value(r, key, single, **kwargs)
                elif isinstance(r, dict):                    
                    if key in r.keys():
                        out = r[key]
                if out:
                    output.append(out)
                if single:
                    return out
                
            return output
        else:
            return kwargs.get(key, default)
                            
    def process_extra_data(self, extra_data, inplace=True, **kwargs):
        # if not extra_data:            
        #     return "", {}, {} 
        
        for tcol, rtcol in {'createdAt':'created_at', 'updatedAt':'updated_at'}.items():
            if len([x for x in extra_data if x['name']==tcol])==0:
                v = {"name":tcol, "dtype":"DateTime", "value":tcol, "rename":rtcol}                
                extra_data.append(v)  
            if not tcol in self.type_map.keys():
                self.type_map[tcol] = 'DateTime'
                            
        data_template = self.data
        if hasattr(self, 'data_template'):
            data_template = self.data_template
            
        new_data_item = ""
        new_type_map = {}
        new_enum_map = {}
        new_name_map = {}
        has_nested_filter = False
        if extra_data:
            if isinstance(extra_data, dict):
                extra_data = [extra_data]
            if not isinstance(extra_data, list):
                logger.error("Invalid extra data format!")
                return "", {}, {}

            for ed in extra_data:
                name = ed.get('name', "").strip()
                dtype = ed.get('type', ed.get('dtype', "")).strip()
                value = ed.get('value', "").strip()
                rename = ed.get('rename', "")
                nested_filter = ed.get('filter', "")
                
                if name in ['createdAt', 'updatedAt'] and not (name in self.type_map.keys()):
                    self.type_map[name] = 'DateTime'

                logger.info(f"Processing extra data for table={self.table}, name={name}, dtype={dtype}, value: {value}")
                
                # Validate data before adding
                if name in data_template:
                    logger.info(f"Extra data name={name} already exists in data_template!")
                    continue
                
                if name not in self.type_map.keys():
                    self.type_map[name] = dtype
                
                if name and dtype and value and name:
                    #logger.good(f'name={name} is valid')
                    if dtype in ['String','DateTime','Int','Float','ID','JSON'] or dtype.startswith('ENUM'):
                        logger.info(f"Adding a field in data with name={name}, dtype={dtype}, value: {value}")
                        #logger.good(f'dtype={dtype} is valid!')
                        #
                        if dtype == "ID":                            
                            if 'data {' in value:
                                if nested_filter:
                                    has_nested_filter = True
                                    value = "%s %s { %s }"%(name, nested_filter, value)
                                else:
                                    value = "%s { %s }"%(name, value)
                            else:
                                value = name
                        elif dtype.startswith('ENUM'):
                            value = name
                            if elist:=ed.get('enum_list', []):
                                new_enum_map[name] = elist  
                        else:
                            value = name                              
                            
                        # Data is validated, it is read to add to self.data
                        new_data_item += f"{value} \n"                    
                        new_type_map[name] = dtype
                        if rename:
                            if isinstance(rename, dict):
                                new_name_map.update(rename)
                            elif isinstance(rename, str):
                                if dtype == "ID" and not name.endswith('_id'):
                                    new_name_map[name+"_id"] = rename
                                else:
                                    new_name_map[name] = rename
                                
                    else:
                        logger.error(f"Invalid data type: {dtype} for extra data name={name}")
                        continue
                else:
                    logger.error(f"Invalid extra data: {ed}")
                    continue
                     
        logger.info(f"New data item from extra_data: \n {new_data_item}")  
         
        if inplace:            
            if not new_data_item:
                logger.warn("Extra_data keyword passed, but got empty new_data_item to add to self.data!")
                return new_data_item, new_type_map, new_enum_map
            
            try:          
                if '%s' in data_template:
                    # logger.info(f"Updating self.data with new data item ...")
                    #                                                      
                    self.data = data_template%new_data_item[:-1] 
                    #if has_nested_filter:
                    #    print('**** query schema with nested filter: \n', self.data)
                        
                    self.type_map.update(new_type_map)
                    self.enum_map.update(new_enum_map)
                    self.id_names_map.update(new_name_map)
                else:
                    logger.error("Can not find `%s` in self.data: ")
            except Exception as e:
                logger.error(f"Error updating self.data: {e}")              
        else:
            return new_data_item, new_type_map, new_enum_map
        
        
    @measure_execution_time 
    def coarsen_object_type(self, object):
        new_object = {}
        for ovar, val in object.items():
            var = ovar
            
            if not val:
                logger.info(f"Empty value for attribute: {var} in object! Skipping it ...", fg='yellow')
                continue
            
            if var in self.output_variables:
                logger.info(f"Output attribute: {var} in object! Skipping it ...", fg='yellow')
                continue
            
            if ovar.endswith('_id'):
                if ovar in self.type_map.keys():
                    pass  # already in correct format
                elif ovar[:-3] in self.type_map.keys() and self.type_map.get(ovar[:-3], "") == 'ID':
                    logger.info(f'Auto Fix: {var} with {var[:-3]}!', fg='green')
                    var = ovar[:-3]  
                elif 'tinder_'+ovar[:-3] in self.type_map.keys():
                    logger.info(f'Auto Fix: {var} with tinder_{var[:-3]}!', fg='green')
                    var = 'tinder_'+ovar[:-3]    
                for k, v in self.id_names_map.items():
                    if ovar == v and k in self.type_map.keys():
                        logger.info(f'Auto Fix: {var} with {k}!')
                        var = k
                        break                 
                                
            if var in self.type_map.keys():         
                try:
                    if self.type_map[var] == 'ID':
                        if isinstance(val, (str, int, list, tuple)):
                            new_object[var] = val
                        else:
                            logger.error(f"Error coarsening TABLE/ID object=({var}, {val}). Skipping it ...")
                    elif self.type_map[var] in ['Text', 'String']:
                        try:
                            new_object[var] = str(val)
                        except Exception as e:
                            # print(e)
                            logger.error(f"Error coarsening STRING object=({var}, {val}). Skipping it ...")                        
                    elif self.type_map[var].startswith('Date'):
                        try:                            
                            #issue with python vs javascript isoformat - remove/add last 'Z' to parse/cast                             
                            try:
                                new_object[var] = datetime.fromisoformat(val).strftime('%Y-%m-%dT%H:%M:%SZ')
                                #.isoformat()
                            except:
                                new_object[var] = datetime.fromisoformat(val[:-1]).strftime('%Y-%m-%dT%H:%M:%SZ')                                
                        except Exception as e:
                            # print(e)
                            logger.error(f"Error coarsening DATE object=({var}, {val}). Skipping it ...")
                    elif self.type_map[var] in ['Number','Int','Float']:
                        try:
                            if self.type_map[var] == 'Int':
                                new_object[var] = int(val)
                            else:
                                new_object[var] = float(val)
                        except Exception as e:
                            # print(e)
                            logger.error(f"Error coarsening {self.type_map[var]} object=({var}, {val}). Skipping it ...")
                    elif self.type_map[var] == 'Boolean':
                        try:
                            new_object[var] = bool(val)
                        except Exception as e:
                            # print(e)
                            logger.error(f"Error coarsening BOOLEAN object=({var}, {val}). Skipping it ...")
                    elif self.type_map[var] == 'JSON':
                        try:
                            new_object[var] = json.loads(val) if isinstance(val, str) else val
                        except Exception as e:
                            # print(e)
                            logger.error(f"Error coarsening JSON object=({var}, {val}). Skipping it ...")  
                    elif 'enum' in self.type_map[var].lower():
                        if val in self.enum_map.get(var, []):
                            new_object[var] = val
                        else:
                            logger.warn(f"Invalid ENUM value={val} for attribute: {var} in object!")
                            logger.info(f"Valid values are: {self.enum_map.get(var, [])}")
                            logger.info(f'Setting default value for attribute: {var} in object!')
                            new_object[var] = self.enum_map.get(var, [""])[0]
                    else:
                        logger.error(f'Invalid type for attribute: {var}={val} in object! Skipping it ...')
                        
                    # if var in self.type_map.keys() and var not in new_object.keys():
                    #     raise                         
                except Exception as e:
                    logger.error(f"Error coarsening object=({var}, {val}): {e}")
                    return {}
            else:
                logger.info(f"Invalid attribute: {var} in object! Skipping it ...", fg='yellow')
                
        return new_object
                
    @measure_execution_time
    def validate_objects_type(self, object, all=True, coarsen=True):
        if coarsen:
            object = self.coarsen_object_type(object)
            # coarsed object satisfies the type_map so no need to check
            return True
            
        for var, val in object.items():                                  
                            
            if var not in self.type_map.keys() and all:                
                logger.error(f"Invalid attribute: {var} in object!")
                return False
            if var not in self.type_map.keys() and not all: 
                _ = object.pop(var)
                continue
            else:
                if self.type_map[var] == 'ID':
                    if not isinstance(val, (str, int, list, tuple)):
                        logger.error(f"Invalid type for attribute: {var} in object! Expected ID got {type(val)}!")
                        return False
                elif self.type_map[var] in ['Text', 'String']:
                    if not isinstance(val, str):
                        logger.error(f"Invalid type for attribute: {var} in object! Expected String got {type(val)}!")
                        return False
                elif self.type_map[var].startswith('Date'):
                    try:
                        if 'Z' in val:                            
                            _ = datetime.fromisoformat(val[0:-1])
                        else:
                            _ = datetime.fromisoformat(val)
                    except:
                        logger.error(f"Invalid type for attribute: {var} in object! Expected Date got {type(val)}!")
                        return False
                elif self.type_map[var] in ['Number','Int','Float']:
                    if not isinstance(val, (int, float)):
                        logger.error(f"Invalid type for attribute: {var} in object! Expected Number got {type(val)}!")
                        return False
                elif self.type_map[var] == 'Boolean':
                    if not isinstance(val, bool):
                        logger.error(f"Invalid type for attribute: {var} in object! Expected Boolean got {type(val)}!")
                        return False
                elif self.type_map[var] == 'JSON':
                    if not isinstance(val, dict):
                        logger.error(f"Invalid type for attribute: {var} in object! Expected JSON got {type(val)}!")
                        return False
                elif self.type_map[var].startswith('ENUM'):
                    if not isinstance(val, (str, int, float)):
                        logger.error(f"Invalid type for attribute: {var} in object! Expected Scalar got {type(val)}!")
                        return False
                else:
                    logger.error(f"Invalid type for attribute: {var} in object!")
                    return False
        return True
                
            
    def validate_objects_name(self, object, all=True):
        data = self.data
        if not data:
            logger.error("No data schema provided!")
            return False
        vars = data.split('attributes {')
        if len(vars) > 1:
            vars = vars[1].split('}')[0].split('\n')
            if all:
                # create: check if all attributes are present
                for var in vars:
                    if var.strip() not in object:
                        logger.error(f"Missing attribute: {var.strip()} in object!")
                        return False                
            else:
                # update or delete: check if all attributes are valid
                for var in object:
                    if var.strip() not in vars:
                        logger.error(f"Invalid attribute: {var.strip()} in object!")
                        return False
                
        return True
    
    def id_name(self, table=""):
        if not table:
            table = self.table_single
            
        if table == 'job' or table == 'jobs':
            return 'job_id'
        elif table == 'tinderJobProfile' or table == 'tinderJobProfiles':
            return 'job_profile_id'
        elif table == 'tinderUserProfile' or table == 'tinderUserProfiles':
            return 'user_profile_id'
        elif table == 'tinderUserPreference' or table == 'tinderUserPreferences':
            return 'user_preference_id'        
        elif table == 'tinderUserJobMatch' or table == 'tinderUserJobMatches':
            return 'user_job_match_id'
        elif table == 'tinderUserReaction' or table == 'tinderUserReactions':
            return 'user_reaction_id'
        elif table =='tinderAssetGeneration' or table == 'tinderAssetGenerations':
            return 'asset_generation_id'
        elif table == "jobTrainee" or table == "jobTrainees":
            return 'job_trainee_id'
        elif table == "trainee" or table == "trainees":
            return 'trainee_id'
        elif table == "jobApplicationStatus" or table == "jobApplicationStatuses":
            return 'job_application_status_id'        
        else:
            try:
                #logger.warn(f"Mapping id to *_id for table: {table} ...")
                return camel_to_snake(table)+'_id'
            except Exception as e:
                # print(e)
                logger.error(f"Invalid table name: {table} to map id to *_id!")
                return 'id' 
           
    def gql_type_and_var(self, item, **kwargs):
        '''
        create mutation query
        '''
        
        idval = kwargs.get('idval', "")
        param_type = ""
        param_var = ""  
        
        # add id attribute       
        if idval:                
            param_var += f"id: {idval}" + ', data: {'
            
            
        # loop over other attributes    
        for k,v in self.type_map.items(): 
            if k in ['createdAt', 'updatedAt']:
                continue
            
            if k in item:  
                if v == 'ID':
                    logger.info(f"ID attribute found in object: col={k}, val={item[k]}, type={type(item[k])}!")
                    if isinstance(item[k], list):
                        param_type += f"\n \t\t\t ${k}: [{v}]!"
                    else:
                        param_type += f"\n \t\t\t ${k}: {v}!"
                else:         
                    param_type += f"\n \t\t\t ${k}: {v}"
                #                    
                param_var += f"\n \t\t\t\t {k}: ${k}"
                
        if idval:
            param_var += "\n \t\t\t\t }"
            
        return param_type, param_var
                       
    def map_id_to_object_id(self, res):              
        res = copy.deepcopy(res)
        
        def _apply_id_map(k, v, cols):
            newcol = None
            col = None
            try:
                if k+'_id' in cols:
                    newcol = v                          
                    col = k+'_id'
                else:
                    for c in cols:
                        if c.startswith(k):
                            newcol = c.replace(k, v)
                            col = c
                            break                    
            except Exception as e:
                logger.error(e)
            
            return newcol, col
        
        if isinstance(res, pd.DataFrame):
            if res.empty:
                return res
            tenxdf = res
            if 'id' not in tenxdf.columns:
                logger.error("No ID attribute found in DATAFRAME RES object!")
                if logger.log_level<50:
                    # print(res)
                    pass
                return tenxdf
            
            columns={'id': self.id_name()}
            for k, v in self.id_names_map.items():                
                newcol, col = _apply_id_map(k, v, tenxdf.columns)
                if newcol:
                    columns[col] = newcol
    
            tenxdf.rename(columns=columns, inplace=True)            
            return tenxdf
        
        elif isinstance(res, dict):
            if not res:
                return res     
            if 'data' in res.keys():
                res = res['data']
                return self.map_id_to_object_id(res)       
            elif 'id' not in res.keys():
                logger.error("No ID attribute found in DICT RES object!")
                return res
            else:
                res[self.id_name()] = res.pop('id')
                
            keys_list = list(res.keys())           
            for k, v in self.id_names_map.items():  
                newcol, col = _apply_id_map(k, v, keys_list)
                if newcol: 
                    try:                                           
                        res[newcol] = res.pop(col)
                    except Exception as e:
                        # print(e)
                        logger.error(f"Error mapping {(k, v, col)} to {newcol} in object!")
                        continue
                    
            return res
        
        elif isinstance(res, (list, tuple)):
            if not res:
                return res
            res_out = []
            for item in res:
                res_out.append(self.map_id_to_object_id(item))                
            return res_out
        else:
            if res is None:
                logger.error("No data found in object!")
            else:
                logger.error(f"Invalid data format: type(res)={type(res)}!")
            return res
           
    def get_id_from_gql_res(self, res, table):       
        if isinstance(res, dict): 
            if 'id' in res:
                id = res['id']
            elif self.id_name() in res:
                id = res[self.id_name()]
            else:
                try:
                    id = res['data'][table]['data']['id']   
                    if isinstance(id, dict):
                        if 'id' in id:
                            id = id['id']
                        elif 'data' in id:
                            id = id['data']['id']
                except:
                    id = res
        elif isinstance(res, list):
            try:
                id = []
                for x in res:
                    id.append(self.get_id_from_gql_res(x, table))
            except:
                id = res
        
        if isinstance(id, list):
            if len(id) == 1:
                id = id[0]
                
        return id
    
    def _is_valid_field(self, scol, **kwargs)->bool:
        c1 = scol in self.type_map.keys()
        c2 = scol in self.relation_map.keys()
        c3 = scol=='id'
        c4 = True
        for k, v in kwargs.items():
            c4 = c4 or scol in v
        
        return c1 or c2 or c3 or c4
        
    def construct_query_filter(self, prefix=", ", **kwargs):
        
        query_filter = ""
        for k in ['query_filter', 'filter', 'filters']:
            if k in kwargs.keys():
                query_filter = kwargs.pop(k)
                break
        
        # process extra data
        extra_data = kwargs.pop('extra_data', [])
        if isinstance(extra_data, dict):
            extra_data = [extra_data]
            
        #
        extra_keys_map = {}
        if extra_data:
            extra_keys_map = {x['name']:x.get('dtype',x.get('type',"")) 
                                    for x in extra_data 
                                    if 'name' in x.keys() and
                                        ('dtype' in x.keys() or 'type' in x.keys())
            }
                    
        # add created at query_filter                 
        if not query_filter:
            
            logger.info('Empty query_filter. Checking if time and general filter keys are passed ...')            
            scol = kwargs.pop('scol',"")
            sval = kwargs.pop('sval',"")
            op = kwargs.pop('op',"eq")
            
            #
            exkeys = list(extra_keys_map.keys())
            if self._is_valid_field(scol, exkeys=exkeys):
                if scol=='id':
                    stype='ID'
                else:           
                    stype=self.type_map.get(scol, extra_keys_map.get(scol, 'String'))
            else:
                if scol and sval:
                    klist = list(self.type_map.keys())
                    klist.extend(list(extra_keys_map.keys()))
                    klist.append('id')
                    logger.warn(f"scol={scol} is not a member of type_map.keys={klist}")
                    logger.warn(f"!!!!setting scol={scol} and sval={sval} to empty string!!!!")
                    scol = ""
                    sval = ""
 
                                
            #
            dtval = ""
            dtcol = kwargs.pop('dtcol', 'createdAt')
            dtop = kwargs.pop('dtop', 'gt') 
            dtype = 'DateTime'
            if dt:=kwargs.pop('dt', kwargs.pop('since',None)):
                if isinstance(dt, int):
                    dt = datetime.now().replace(hour=23,minute=59,second=59, microsecond=0) - timedelta(days=dt)
                if isinstance(dt, datetime):
                    dt = dt.isoformat()
                if isinstance(dt, str):
                    dtval = f'"{dt}Z"'                                 
                    #
                logger.good(f'----> Time filter for `{dtcol} {dtop} {dt}` ...')
                    
            andcol = kwargs.pop('andcol', [])
            andval = kwargs.pop('andval', kwargs.pop('andvalue', []))            
            andop = kwargs.pop('andop', {})
            andtype = kwargs.pop('andtype', {x:self.type_map.get(x, 'String') for x in andcol})
            
            f1 = lambda x: op
            f2 = lambda x: self.type_map.get(x, 'String')
            andop = self.sg.make_scol_optype_dict(andcol, andop, func=f1)
            andtype = self.sg.make_scol_optype_dict(andcol, andtype, func=f2)
                                    

            if scol and sval and dtcol and dt and dtop:
                logger.info(f'----> Applying general filter for `{dtcol} {dtop} {dt}` ...')                                
                andcol.append(dtcol)                
                andval.append(dtval)                                        
                andop[dtcol] = dtop
                andtype[dtcol] = 'DateTime'
            elif dtcol and dtval and dtop:
                logger.info(f'----> Applying time filter for `{dtcol} {dtop} {dt}` ...')
                scol = dtcol
                sval = dtval
                op = dtop   
                stype = dtype
                             
            if scol and sval:
                kwargs.update(dict(
                                   scol=scol,
                                   sval=sval,
                                   op=op, 
                                   stype=stype, 
                                   andcol=andcol, 
                                   andval=andval, 
                                   andop=andop,
                                   andtype=andtype,
                                   relation_map=self.relation_map,
                                   ))
                query_filter = self.sg.create_filter(**kwargs)
                    
                if query_filter:
                    query_filter = f'{prefix}filters: {query_filter}'

                extra_data.append({"name":dtcol, "dtype":"DateTime", "value":dtcol})
            else:
                logger.info('No time or general filter keys passed!')    
                
        
        return query_filter, extra_data        
          
    @measure_execution_time                          
    def exists(self, data="", table='', 
               scol='id', sval='', 
               op='eq', **kwargs):
        
        query_filter = ""
        for k in ['query_filter', 'filter', 'filters']:
            if k in kwargs.keys():
                query_filter = kwargs.pop(k)
                break
        
        logger.debug(f'-------> exists kwargs {kwargs}', level=9)
        
        # process extra data
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)        
        
        if not data:
            data = self.data
        if not data:
            logger.error("No data schema provided!")
            return []        
            
        if scol == 'id':
            if not table:        
                table = self.table_single
            else:
                table = self.tosingle(table)
        else:
            if not table:
                table = self.table
                
        # get type        
        stype = kwargs.pop('stype',self.type_map.get(scol, 'ID'))
        andtype = kwargs.pop('andtype', self.type_map)
        ortype = kwargs.pop('ortype', self.type_map)           
        #    
        if not table:
            logger.error("Table name is not provided!")
            return []
            
        
        logger.info("----------------------> check/get data if exists in Tenx:")
            
        logger.info(f"Checking if data exists in `table={table}` using the following filter:")
        if not query_filter:   
            if scol == 'id':
                var = "$id"
            else:
                var = f"$val"
                
            kwargs.update(dict(scol=scol, 
                                sval=var, 
                                stype=stype, 
                                op=op, 
                                andtype=andtype, 
                                ortype=ortype,
                                relation_map=self.relation_map))
            query_filter =  self.sg.create_filter(**kwargs)            

        logger.info(f"----> `self.exists` query_filter: {query_filter}", fg='yellow')
        
        if scol == 'id':     
            logger.info(f'----> Filtering by ID column...')  
            if isinstance(sval, list):            
                query = '''
                    query get%s($id: [ID]!) {
                        %s(id: $id) {
                            %s
                        }
                    }
                '''%(capitalize(table), table, data)
            else:
                query = '''
                        query get%s($id: ID!) {
                            %s(id: $id) {
                                %s
                            }
                        }
                    '''%(capitalize(table), table, data)                
            
            variables = {'id': sval}
            
        elif self.type_map[scol] == 'ID':  #it is a table
            logger.info(f'----> Filtering by related_table={scol} in `table={table}` ...')
            if isinstance(sval, list): 
                #query_filter = query_filter.replace('eq:', 'in:')              
                query = '''
                    query get%s($val: [%s]!) {
                        %s(filters: %s ) {     
                            %s 
                        }
                    }
                '''%(capitalize(table), stype, table, query_filter, data)
            else:
                query = '''
                    query get%s($val: %s!) {
                        %s(filters: %s ) {     
                            %s 
                        }
                    }
                '''%(capitalize(table), stype, table, query_filter, data)
                            
            variables = {'val': sval}  
                      
        else:
            logger.info(f'----> Filtering by column={scol} in `table={table}` ...')
            query = '''
                query get%s($val: %s!) {
                    %s(filters: %s ) {     
                        %s 
                    }
                }
            '''%(capitalize(table), stype, table, query_filter, data)
            
            variables = {'val': sval}                        

        logger.info(f"----> Searching for `{scol}={sval}` in `table={table}` ... ", bold=True, fg='pink')
        

        if scol == 'id' or scol in data:            
            res, _ = self.sg.execute_query(query, variables, **kwargs)
        else:
            # print('==============================')
            # print('exists query:')
            # print(json.dumps(query, indent=4))
            # print('exists variables:')
            # print(json.dumps(variables, indent=4))
            # print('==============================')            
            logger.error(f"----> Invalid column={scol} for {table} with attributes: \n {data}!")
            return {}
                      
        
        if res:
            logger.good(f"----> Found object with {scol}={sval} in `table={table}`!")
            if not kwargs.get('nopp', False):
                res = self.map_id_to_object_id(res) 
            #logger.good(f'Returned object tyFound objectpe: {type(res)} - >[0]-> {type(res[0])}')   
            if isinstance(res,list):
                return res[0]  
            else:       
                return res
        else:
            logger.info(f"----> No Object found with {scol}={sval} in `table={table}`!")
            return {}
          
    @measure_execution_time                
    def count_records(self, **kwargs):
        
        query_filter = ""
        for k in ['query_filter', 'filter', 'filters']:
            if k in kwargs.keys():
                query_filter = kwargs.pop(k)
                break

        kwargs.update({'dataframe':False, 'raw':True})
        logger.debug(f'-------> count_records kwargs {kwargs}', level=9)
        
        kwargs['limit'] = 0
        kwargs['prefix'] = ""
        query_filter, extra_data = self.construct_query_filter(query_filter=query_filter,
                                                               **kwargs)  
        
        #
        # process extra data                            
        _ = self.process_extra_data(extra_data, inplace=True)
        
        data = kwargs.pop('data', "")
        table = kwargs.pop('table', "")
        
        if not table:
            table = self.table
        if not table:
            logger.error("Table name is not provided!")
            return []
                
        if not data:
            data = self.data
        if not data:
            logger.error("No data schema provided for `table={table}`!")
            return []            
                    
            
        logger.info(f"Counting all `table={table}` objects ...", bold=True, fg='pink')
                
        #        
        query = '''
        query get%s {
            %s( %s ) {     
                meta {
                    pagination {
                        total
                    }
                }   
            }
        }
        '''%(capitalize(table), table, query_filter)
        
        variables = {}        
        
        kwargs['nopp'] = True
        res, meta = self.sg.execute_query(query, variables, **kwargs)         
        total = meta['pagination']['total']
        
        return total   
                  
    @measure_execution_time                      
    def get_all_objects(self, data="", table='', 
                        limit=0, cursor={}, raw=False, ddcol="", 
                        dataframe=True, **kwargs):
         
        query_filter = ""
        for k in ['query_filter', 'filter', 'filters']:
            if k in kwargs.keys():
                query_filter = kwargs.pop(k)
                break
        
        kwargs.update({'dataframe':dataframe, 'raw':raw})
        
        #caller_filename = kwargs.get('caller', "")
        #logger.good(f'-------> `{caller_filename}->get_all_objects` cursor={cursor}', fg='pink')
                            
        if limit == 0:
            limit = kwargs.get('maxobjs', limit)      
        
        # set return cursor
        cursor = copy.deepcopy(cursor)
        return_cursor = False
        if cursor:
            limit = 0
            return_cursor = True
            
        res = pd.DataFrame() if dataframe else []
        
        # empty return object
        if return_cursor:
            empty_return = res, cursor
        else:
            empty_return = res
            
        # set empty output object
        if dataframe:
            tenxdf = pd.DataFrame()
        else:
            tenxdf = []            
        
        # ensure cursor is a dictionary                
        if not isinstance(cursor, dict):
            cursor = {}
        else:
            logger.good('Continue from existing cursor object:')            
        
        
        #
        #print(f'----> limit:{limit}',{k:v for k, v in cursor.items() if k != 'query'})
            
        
        query_filter = cursor.get('filter', query_filter)
        query = cursor.get('query', "")         
        page = cursor.get('page', 1)         
        if return_cursor:   
            page_size = cursor.get('page_size', 20)
        else:
            if limit == 0:
                page_size = kwargs.get('page_size', 1000)
            else:
                page_size = kwargs.get('page_size', min(limit,1000))
            
        if limit>0 and limit < page_size:
            page_size = limit
            
        offset_start = int((page-1)*page_size)
                                                   
        if not query:                       
            #                    
            # process query_filter and extra data  
            kwargs['prefix'] =  ", "
            query_filter, extra_data = self.construct_query_filter(query_filter=query_filter, 
                                                                   **kwargs)                 
            
            logger.good(f"----> `self.get_all_objects` filter: {query_filter}", fg='pink')

            
            # process extra data                            
            _ = self.process_extra_data(extra_data, inplace=True)
                    
            if not data:
                data = self.data
            if not data:
                logger.error("No data schema provided!")
                return empty_return         
                        
            if not table:
                table = self.table
            if not table:
                logger.error("Table name is not provided!")
                return empty_return  
            
                
            logger.info(f"Getting all {table} objects ...", bold=True, fg='pink')
                    
    
            # prepare query
            #$page: Int!            
            #$pageSize: Int!
            #{ page: $page, pageSize: $pageSize }
            
            sort_order = kwargs.get('sort', 'desc')  

            query = '''
            query get%s( $offsetStart: Int!, $pageSize: Int!) {
                %s( pagination: { start: $offsetStart, limit: $pageSize }, sort: "createdAt:%s"  %s ) {     
                    meta {
                        pagination {
                            page
                            pageSize
                            total
                            pageCount
                        }
                    }      
                    %s
                }
            }
            ''' % (capitalize(table), table, sort_order, query_filter, data)

        
         
                 
        logger.info(f"Getting objects from Tenx `table={table}`... ")
            
        if not query:
            logger.error("Invalid query for `table={table}`!")
            if return_cursor:
                return tenxdf, cursor
            else:
                return tenxdf
        
        reslist = []
        res = []                
        ntotal = 0
        navailable = -1
        page_count = -1
        
        # define variables
        #variables = {"page": page, "pageSize": page_size}
        variables = {"offsetStart": offset_start, "pageSize": page_size}       
        
        nloop = 0
        max_loop = 100 
        while True:                      
            nloop += 1
            if nloop > max_loop and max_loop > 0:
                logger.error(f"************Exceeded max loop count: {max_loop}!******")
                break   
            if nloop>10:
                logger.warn(f"While Loop count: {nloop} ...")
                      
            try:             
                res, meta = self.sg.execute_query(query, variables, **kwargs)
            except Exception as e:
                logger.error(f"Error executing query: {e}")
                raise
            
            ntotal += len(res)
            
            if len(res)>0:      
                try:          
                    res = self.map_id_to_object_id(res)
                except Exception as e:
                    logger.error(f"Error mapping id to object id: {e}")
                    raise
                
                if isinstance(res, (dict, pd.DataFrame)):                            
                    reslist.append(res)
                elif isinstance(res, (list,tuple)):
                    reslist.extend(res)
                else:     
                    logger.error(f"Invalid query result data format for `table={table}`: type(res)={type(res)}!")
                    break

            try:
                page = meta['pagination']['page']
                page_count = meta['pagination']['pageCount']
                page_size = meta['pagination']['pageSize']
                navailable = meta['pagination']['total']
                
                # feedback
                sss = f"n={ntotal}, navailable={navailable}"
                sss2 = f"page_count={page_count}, page={page}, page_size={page_size}"
                logger.info(f'Got the following so far ==> {sss}, {sss2}')                  
                                    
                cursor['query'] = query
                cursor['filter'] = query_filter                     
                cursor['page'] = page
                cursor['page_size'] = page_size
                cursor['total'] = navailable
                cursor['page_count'] = page_count
                
            except Exception as e:
                logger.error(f"Error extracting pagination info: {e}")
                break            

            #print(f'-{nloop}--> page, page_count, page_size, navailable, variables, len(res):', 
            #      page, page_count, page_size, navailable, variables, len(res))
         
            if  page >= page_count  or page_count==0 or navailable==0:      
                break
                                                         
            
            offset_start += page_size + 1
            variables["offsetStart"] = offset_start  
                  
            if return_cursor:      
                if ntotal >= page_size:
                    break
            else:
                if limit>0 and ntotal >= limit:
                    break
                
            if max_loop > 0:
                break
                
            
        #print('Returning reslist:', len(reslist))
        tenxdf = reslist
        if len(reslist) > 0 and dataframe:
            if kwargs.get('sort', 'asc'):
                keep = 'last'
            else:
                keep = 'first'
            tenxdf = pd.concat(reslist).drop_duplicates(subset=[self.id_name()],
                                                        ignore_index=True, 
                                                        keep=keep)
            if ddcol:
                tenxdf = tenxdf.drop_duplicates(subset=[ddcol],
                                                ignore_index=True, 
                                                keep='last')  
                                             
        
        if return_cursor:
            return tenxdf, cursor
        else:
            cursor = {}
            return tenxdf          
    
    @measure_execution_time
    def delete_objects_by_id(self, object_ids, table='', **kwargs):  
        
        if not table:
            table = self.table_single
        else:
            table = self.tosingle(table)
        if not table:
            logger.error("Table name is not provided!")
            return []  
        
        #
        if isinstance(object_ids, (str, int)):
            object_ids = [object_ids]  
                
        #
        dquery = '''
        mutation delete%s($id: ID!){
            delete%s(id: $id) {
                data {
                    id
                }
            }
        }
        '''%(capitalize(table), capitalize(table))
        
        dvariables = {"id": ""}
        
        logger.info(f"Deleting `table={table}` objects ...")
        if logger.log_level<10:
            logger.info("Using the following variables and query: ")
            # print(dvariables)
            # print(dquery)
        
        total = len(object_ids)
        deleted_job_matches = []
        iloop = 0
        for id in object_ids:
            dvariables['id'] = id
            res, meta = self.sg.execute_query(dquery, dvariables, nopp=True)
            if res:
                deleted_job_matches.append(res)
                if iloop%20==0:
                    logger.info(f'==> {iloop}/{total} job matches deleted so far')

        return deleted_job_matches

    @measure_execution_time
    def save_or_update_object(self, params, data="", return_object=False, **kwargs):
        '''
        This function saves or updates a single object in the database.
        To update an object, the object must have an 'id' attribute.
        '''
        
        kwargs.update({'dataframe':False, 'raw':True})
        logger.debug(f'-------> save_or_update kwargs {kwargs}', level=11)
        
        if isinstance(params, dict):
            params_list = [params]
        elif isinstance(params, pd.DataFrame):
            params_list = params.to_dict(orient='records')        
        elif isinstance(params, list):
            params_list = params
        else:
            logger.error("Invalid data format for `table={table}`!")
            return []

        if len(params)==0:
            logger.error("No data provided for `table={table}`!")
            return []        

        # process extra data
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)        

        table = self.table_single
        
        if not table:
            logger.error("Table name is not provided!")
            return []
                  
        if not data:
            data = self.data
        if not data:
            logger.error("No data schema provided for `table={table}`!")
            return []                        
                    
        logger.info(f"Saving or updating object entries in Tenx `table={table}` ...")        
        added_item_ids = []
        iloop=0
        for item_loop in params_list:    
            iloop += 1
                 
           # id name for table
            id_name = self.id_name(table)             
            id_val = item_loop.get(id_name, "")
                                                
            logger.info('Coarsening object type for `table={table}` ...')
            item = self.coarsen_object_type(item_loop)
            logger.good('Successfully Coarsened object!')  
                    # create mutation query
            param_type, param_var = self.gql_type_and_var(item, idval=id_val)            
            variables = item                                 
                                                                              
            if id_val: #update                           
                logger.info(f"Updating object with {id_name}={id_val} in `table={table}` ...")
                
                # create mutation query                
                query = """ mutation update%s(%s) {
                    update%s(%s) {
                        %s
                    }
                }
                """%(capitalize(table), param_type, capitalize(table), param_var, data)                                

            else: # create
                logger.info(f"Creating object in {table} ...")
                            
                                                    
                query='''
                mutation create%s(%s) { 
                    create%s(data: {%s}) {                       
                        %s
                    }        
                }
                '''%(capitalize(table), param_type, capitalize(table), param_var, data)
            
            
            if logger.log_level<10 and iloop==1:
                logger.info("1st loop: Using the following variables and query: ")                
                # print(variables)
                # print(query)
                        
            try:
                res, _ = self.sg.execute_query(query=query, variables=variables, **kwargs) 
                      
                if res:   
                    res = self.map_id_to_object_id(res)
                                     
                    if id_name in item: #update
                        tname = 'update%s'%capitalize(table)
                    else:
                        tname = 'create%s'%capitalize(table)
                        
                    if return_object:                        
                        if isinstance(res, dict):
                            added_item_ids.append(res)
                        elif isinstance(res, (list, tuple)):
                            for r in res:
                                if r and isinstance(r, dict):
                                    added_item_ids.append(r)
                                elif r and isinstance(r, (list, tuple)):
                                    for rr in r:
                                        if rr and isinstance(rr, dict):
                                            added_item_ids.append(rr)
                                        else:
                                            logger.error(f"Invalid data format for `table={table}`: type(rr)={type(rr)}!")
                                            added_item_ids.append(rr)            
                                
                        else:
                            logger.error(f"Invalid data format for `table={table}`: type(res)={type(res)}!")                        
                            added_item_ids.append(res)
                            
                    else:
                        if isinstance(res, dict):
                            id = self.get_id_from_gql_res(res, tname)
                        elif isinstance(res, (list, tuple)):                        
                            id = self.get_id_from_gql_res(res[0], tname)
                        else:
                            if logger.log_level<20:
                                # print('type(res), res', type(res), res)
                                pass
                            id = ""
                            
                        if id:
                            logger.good(f'Extracted object id={id} from `table={table}`...')
                        else:
                            logger.error(f'Failed to extract object id from `table={table}`!')
                                                
                        added_item_ids.append(id)                               
                         
                    logger.good(f"Successfully registered entry to Tenx `table={table}`!")
                else:
                    # print(res)
                    logger.error(f"Unable to register entry to Tenx `table={table}`!")
            except Exception as e:
                logger.error(f"Error: {e}")
                logger.error(f"Unable to register entry to Tenx `table={table}`!")                
                logger.info(f"---> used the following query and variables: ")
                # print(variables)
                # print(query)                                
                res = []
                
        return added_item_ids    

    @measure_execution_time
    def get_tenx_id_if_exists(self, scol, params, table='', **kwargs):
        
        # deterimine the filtering columns and their values
        andcol = kwargs.get('andcol', [])
        orcol = kwargs.get('orcol', [])
        andvalue = []
        orvalue = []
        for col in andcol:
            if col not in self.type_map.keys():
                _ = andcol.pop(col)
            else:
                if v:=params[col]:
                    andvalue.append(v)
                else:
                    _ = andcol.pop(col)
        for col in orcol:
            if col not in self.type_map.keys():
                _ = orcol.pop(col)
            else:
                if v:=params[col]:
                    orvalue.append(v)
                else:
                    _ = orcol.pop(col)
                
        
        if scol in self.type_map.keys() or (andcol and andvalue) or (orcol and orvalue): 
            if scol:
                stype = self.type_map[scol]
                sval = params[scol]
            else:
                scol=""
                stype = ""
                sval = ""
                
            # search on plural table name
            if not table:
                table = self.table
            #
            filtercol = {k:v for k,v in zip(andcol, andvalue)}
            filtercol.update({k:v for k,v in zip(orcol, orvalue)})
            filtercol.update({scol: sval})
            logger.info(f"---***---> checking if {filtercol} exists in Tenx `table={table}` ...")
            
            # check if the object exists
            if isinstance(sval, list):
                op = kwargs.get('op','in')
            else:
                op = kwargs.get('op','eq')
                
            res = self.exists(scol=scol, 
                            sval=sval, 
                            stype=stype,
                            andcol=andcol,
                            andvalue=andvalue,
                            orcol=orcol,
                            orvalue=orvalue,                               
                            table=table, 
                            op=op,
                            **kwargs)
            id = ""
            if res:
                logger.good(f"Entry with {scol}={params[scol]} already exists in Tenx `table={table}`!") 
                try:
                    id = self.get_id_from_gql_res(res, table)
                except:
                    pass
            
            return id, res
        else:
            logger.info(f"Entry with {scol}={params[scol]} in Tenx `table={table}` ...")
            return "", {}            
              
    @measure_execution_time      
    def save_if_new(self, scol, params, table='', return_object=False, **kwargs):
        
        #
        kwargs.update({'dataframe':False, 'raw':True})
        logger.debug(f'-------> save_or_update kwargs {kwargs}', level=11)

        
        
        # deterimine the filtering columns and their values
        andcol = kwargs.get('andcol', [])
        orcol = kwargs.get('orcol', [])
        andvalue = []
        orvalue = []
        for col in andcol:
            if col not in self.type_map.keys():
                _ = andcol.pop(col)
            else:
                if v:=params[col]:
                    andvalue.append(v)
                else:
                    _ = andcol.pop(col)
        for col in orcol:
            if col not in self.type_map.keys():
                _ = orcol.pop(col)
            else:
                if v:=params[col]:
                    orvalue.append(v)
                else:
                    _ = orcol.pop(col)
                
        
        filtercol = {}
        
        if scol in params.keys():
            stype = self.type_map[scol]
            sval = params[scol]
        else:            
            scol=""
            stype = ""
            sval = ""
            
        # search on plural table name
        if not table:
            table = self.table
        #
        filtercol = {k:v for k,v in zip(andcol, andvalue) if k in self.type_map.keys() and v}
        filtercol.update({k:v for k,v in zip(orcol, orvalue) if k in self.type_map.keys() and v})
        if scol and sval:
            filtercol.update({scol: sval})

            
            
        if filtercol:
            logger.info(f"Save_if_new: checking if {filtercol} exists in Tenx `table={table}` ...")            
        
            # check if the object exists
            if isinstance(sval, list):
                op = kwargs.get('op','in')
            else:
                op = kwargs.get('op','eq')
                

            #remove vars from kwargs
            _ = kwargs.pop('scol', "")
            _ = kwargs.pop('sval', "")
            _ = kwargs.pop('stype', "")
            _ = kwargs.pop('op', "")
            _ = kwargs.pop('andcol', "")
            _ = kwargs.pop('andvalue', "")
            _ = kwargs.pop('orcol', "")
            _ = kwargs.pop('orvalue', "")
            _ = kwargs.pop('table', "")
        
            res = self.exists(scol=scol, 
                            sval=sval, 
                            stype=stype,
                            andcol=andcol,
                            andvalue=andvalue,
                            orcol=orcol,
                            orvalue=orvalue,                               
                            table=table, 
                            op=op,
                            **kwargs)
        else:
            logger.warn(f"Save_if_new: scol={scol}, sval={sval}, params.keys(): {params.keys()}!")
            logger.info(f"Save_if_new: No filter columns provided for `table={table}`! Skipping search ...")
            res = {}
              
        replace = False  
        if res:                              
            try:
                id = self.get_id_from_gql_res(res, table)
                params[self.id_name()] = id
                replace = True
                if kwargs.get('overwrite', False):
                    logger.warn(f"Overwriting existing `table={table}` record with {self.id_name()}={id} in Tenx ...")                        
                else:                    
                    # return id or object 
                    if return_object:   
                        logger.info(f"Returning loaded object as return_object=True and overwrite=False!")
                        if not isinstance(res, (list, tuple)):
                            res = [res]
                        else:
                            res = list(res)                        
                        return res
                    else:                   
                        logger.info(f"Returning {self.id_name()}={id} as overwrite=False!")
                        return [id]
            except Exception as e:
                logger.error(f"Unable to get id from `table={table}` res: {res}! Error: {e}")
                logger.warn(f"Returning fetched response as is!")
                return res
        else:
            logger.info(f"No entry found with {scol}={params[scol]} in Tenx `table={table}`!")
            
            if scol in params.keys():
                logger.info(f"Registering entry with {scol}={params[scol]} in Tenx `table={table}` ...")
            else:
                logger.info(f"Registering new entry in Tenx `table={table}` ...")
                        
        # save a single object
        if not table:
            table = self.table_single
        else:
            table = self.tosingle(table)

        
        res = self.save_or_update_object(params, table=table, return_object=return_object, **kwargs)
        
        return res
  
        
    def load_object_list(self, objIn, **kwargs):
        
        obj = copy.deepcopy(objIn)
        source = ""
        
        if isinstance(obj, (int, str)):
            if isinstance(obj, int):
                obj = str(obj)
                
            if kwargs.get('isjsonstr', False):
                obj = json.loads(obj)
                source = "jsonstr"
            elif obj.strip().endswith('.json'):                
                if os.path.exists(obj):
                    with open(obj, 'r') as f:
                        obj = json.load(f)
                    source = "jsonfile"
                else:
                    logger.error(f'Failed to load from file: \n {obj}')
                                     
            elif obj.isdigit():                       
                try:
                    kwargs['dataframe'] = False
                    kwargs['raw'] = True
                    _ = kwargs.pop('scol', "")
                    _ = kwargs.pop('sval', "")
                    _ = kwargs.pop('op', "")
                    _ = kwargs.pop('stype', "")
                    obj = self.exists(scol='id', 
                                        sval=obj, 
                                        op='eq', 
                                        stype="ID", 
                                        **kwargs)
                    if obj:                                                
                        obj = [obj]
                        source = "table"
                    else:
                        logger.error(f'Object not found for table={self.table}, id={obj}')
                                            
                    
                except Exception as e:                        
                    logger.error(f'Failed to load object from table={self.table} with id={obj}: \n {e}')
                                                                                       
        elif isinstance(obj, dict):
            obj = [obj]
            source = "dict"
            
        elif isinstance(obj, pd.DataFrame):
            obj = obj.to_dict(orient='records')
            source = "dataframe"
            
        elif isinstance(obj, (list, tuple)):
            source = "list"
            pass
        
        else:
            logger.error(f'Invalid data type `load_object_list` function: type(obj)={type(obj)}')        
        
        return obj, source
                