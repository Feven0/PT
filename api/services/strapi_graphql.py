import os,sys, copy
import requests
import json


from api import config
from api.services.secret import get_auth, lambda_friendly_path
from api.utils.logger import LLPackerLogger

logger = LLPackerLogger(os.path.basename(__file__))

class StrapiGraphql():
    def __init__(self, **kwargs):
        
        # define run environment
        if config.strapi.stage.startswith('dev'):
            run_stage =  kwargs.get('run_stage',config.strapi.stage)
        else:
            run_stage = config.strapi.stage
            
        self.run_stage = run_stage        
        # define url
        root, ssmkey = config.get_strapi_params(run_stage)    
   
        self.apiroot = f"https://{root}.10academy.org/graphql" 
        self.ssmkey = ssmkey
        
        # define token
        token = kwargs.get('strapi_token',kwargs.get('token',''))
        if not token:
            logger.info('StrapiGraphql no token passed! Getting token using run_stage:', run_stage, level=9)
            self.token = get_auth(ssmkey,
                                envvar='STRAPI_TOKEN',
                                fconfig=lambda_friendly_path(f'.env/{root}.json'))
        else:
            self.token = token
            logger.good('StrapiGraphql token passed!', level=9)

        # define headers
        if self.token:            
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            raise "Token not passed!"

      
    
    
    def get_token(self):
       
        return get_auth(ssmkey=self.ssmkey, fconfig=lambda_friendly_path(f'.env/Strapi_token.json'))
        
        

    def fetch_data(self,table, token=None):
       
        r = requests.get(f"{self.apiroot.replace('graphql','api')}/{table}",
                         headers = {

                        "Authorization": f"Bearer {self.token}", 

                        "Content-Type": "application/json"})
        return r.json()
    
        
    def insert_data (self,data,table, token=None):
      
        try:
            r = requests.post(

                f"{self.apiroot.replace('graphql','api')}/{table}", 

                data = json.dumps({"data":data}),
                # self.token['token']
                headers = {

                "Authorization": f"Bearer {self.token}", 

                "Content-Type": "application/json"}

            ).json()
        except Exception as e:
            print(e)
            raise
            
        return r
    
    def update_data (self, id, data, table, token=None):
      
        try:
            r = requests.put(

                f"{self.apiroot.replace('graphql','api')}/{table}/{id}", 

                data = json.dumps({"data":data}),
                # self.token['token']
                headers = {

                "Authorization": f"Bearer {self.token}", 

                "Content-Type": "application/json"}

            ).json()
        except Exception as e:
            print(e)
            raise
            
        return r
          
        
    def insert_table (self, query, variables):
        """

        Args:
            query (String): You can write mutation graphql query to insert 
            variables (stirng ): Values of each attributes needs to be inserted 

        Raises:
            Exception: _description_

        Returns:
            result_json (Json): Response for your request 
        """
        # use CreateTablename() Mutation query 
        
        request = requests.post(self.apiroot, json={'query': query, 'variables': variables}, headers=self.headers)
        if request.status_code == 200:
            r =  request.json()
            # result_json= json.dumps(r, indent=2)
            result_json = r
            
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(
                    request.status_code, query))
        
        return result_json
    
    def Select_from_table (self,query, variables):
        
        """

        Args:
            query (String): You can write query graphql query to select from table
            variables (stirng ): values if you have specific filter 

        Raises:
            Exception: _description_

        Returns:
            result_json (Json): Response for your request 
        """
        
        # Use query to select from table  
        if variables in [None, {}, ""]:
            kwargs = {'query': query}
        else:
            kwargs = {'query': query, 'variables': variables}
           
            
        try:
            request = requests.post(self.apiroot, 
                                    headers=self.headers,
                                    json=kwargs)   
            if request.status_code == 200:  
                r =  request.json()
            else:              
                try:
                    print('***************Being Eror Message***************') 
                    print(json.dumps(request.json(), indent=4))
                    print('***************End Eror Message***************')
                except:
                    pass
                raise Exception("Query failed to run by returning code of {}. {}".format(
                        request.status_code, query))
                               
        except Exception as err:                
            print(err)
            raise
            
        return r
        
    def update_table (self, query, variables):
        """

        Args:
            query (String): You can write mutation graphql query to update 
            variables (stirng ): Values of each attributes needs to be updated

        Raises:
            Exception: _description_

        Returns:
            result_json (Json): Response for your request 
        """
        # use updateTablename() Mutation query 
        
        request = requests.post(self.apiroot, 
                                json={'query': query, 
                                      'variables': variables}, 
                                      headers=self.headers)
        if request.status_code == 200:
            r =  request.json()
            result_json= json.dumps(r, indent=2)
            
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(
                    request.status_code, query))
        
        return result_json
    
    def delete_from_table (self, query, variables):
        """

        Args:
            query (String): You can write mutation graphql query to delete 
            variables (stirng ): Values of each attributes needs to be deleted

        Raises:
            Exception: _description_

        Returns:
            result_json (Json): Response for your request 
        """
        # use deleteTablename() Mutation query 
        
        request = requests.post(self.apiroot, json={'query': query, 'variables': variables}, headers=self.headers)
        if request.status_code == 200:
            r =  request.json()
            result_json= json.dumps(r, indent=2)
            
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(
                    request.status_code, query))
        
        return result_json
    
    def make_scol_optype_dict(self, col, var, func=None):
        if not func:
            func = lambda x: x
        #
        if isinstance(var, str):
            var = {x: var for x in col}
        elif isinstance(var, list):
            var = {x: var[i] for i, x in enumerate(col)}
        elif isinstance(var, dict):
            pass
        else:
            var = {x: func(x) for x in col}
            
        return var
                        
    def create_filter(self, scol="", sval="",  stype='String', op="$eq",
                         andcol=[], andvalue=[], andop={}, andtype={},
                         orcol=[], orvalue=[], orop={}, ortype={},                         
                         default_type='String', relation_map={}, **kwargs
                         ):   
        
        
        if len(andvalue)==0:            
            andvalue = kwargs.get('andval', [])
        if len(orvalue)==0:            
            orvalue = kwargs.get('orval', [])            

        #
        if isinstance(andcol, str):
            andcol = [andcol]
        if isinstance(andvalue, str):
            andvalue = [andvalue]
        if isinstance(andtype, str):
            andvalue = [andtype]                
        if len(andcol) != len(andvalue):
            logger.error('andcol and andvalue should have the same length')
            print('andcol:', andcol)
            print('andvalue:', andvalue)
            minlen = min(len(andcol), len(andvalue))
            andcol = andcol[:minlen]
            andvalue = andvalue[:minlen]
            
        #
        if isinstance(orcol, str):
            orcol = [orcol]
        if isinstance(orvalue, str):
            orvalue = [orvalue]
        if isinstance(ortype, str):
            orvalue = [ortype]                
        if len(orcol) != len(orvalue):
            logger.error('orcol and orvalue should have the same length')
            print('orcol:', orcol)
            print('orvalue:', orvalue)
            minlen = min(len(orcol), len(orvalue))
            orcol = orcol[:minlen]
            orvalue = orvalue[:minlen]            
        
        def stringize(x, dq=False):
            if isinstance(x, str):
                if ' ' in x and not (x.startswith('"') and x.endswith('"')):
                    logger.debug(f'Fixing Space in filter ... Input={x}')
                    x = '"%s"'%x 
                    logger.debug(f'Fixed Space in filter ... Output={x}')
                elif x.startswith("'") and x.endswith("'"):
                    logger.debug(f'Fixing Single Quote in filter ... Input={x}')
                    x = '"%s"'%str(x)  #.replace("'", '"')
                    logger.debug(f'Fixed Single Quote in filter ... Output={x}')
                else:
                    if dq:
                        x = '"%s"'%x
                    else:
                        x = x
            elif isinstance(x, list):
                x = '[' + ', '.join([stringize(t, dq=True) for t in x]) + ']'
            return x
        
                        
        # update values
        if sval:         
            sval = stringize(sval)
        if andvalue:
            andvalue = [stringize(x) for x in andvalue]
        if orvalue:
            orvalue = [stringize(x) for x in orvalue]

                    
        # validate and filter
        if len(andvalue)>0:
            if not isinstance(andcol, list):
                andcol = []
            if not isinstance(andvalue, list):
                andvalue = []
            #
            f1 = lambda x: op
            f2 = lambda x: default_type
            andop = self.make_scol_optype_dict(andcol, andop, func=f1)            
            andtype = self.make_scol_optype_dict(andcol, andtype, func=f2)
                
                        
        # validate or filter
        if len(orvalue)>0:
            if not isinstance(orcol, list):
                orcol = []
            if not isinstance(orvalue, list):
                orvalue = []
            #
            f1 = lambda x: op
            f2 = lambda x: default_type
            orop = self.make_scol_optype_dict(orcol, orop, func=f1)
            ortype = self.make_scol_optype_dict(orcol, ortype, func=f2)
                               
                          
        andfilters = []
        if andcol and andvalue:                
            for i, (acol, avalue) in enumerate(zip(andcol, andvalue)):
                aop = andop.get(acol, op)    
                atype = andtype.get(acol, default_type)  
                if atype in ['ID']:
                    item = '{%s: { id: {%s: %s}} }' % (acol, aop, avalue)
                elif acol in relation_map.keys():
                    item = '{%s: { %s: {%s: %s}} }' % (relation_map[acol], acol, aop, avalue)
                else:              
                    item = '{%s: {%s: %s}}' % (acol, aop, avalue)
                andfilters.append(item)
                
        orfilters = []
        if orcol and orvalue:
            if isinstance(orcol, str):
                orcol = [orcol]
            if isinstance(orvalue, str):
                orvalue = [orvalue]
            assert len(orcol) == len(orvalue), "orcol and orvalue should have the same length"
            for i, (ocol, ovalue) in enumerate(zip(orcol, orvalue)):           
                oop = orop.get(ocol, op)
                otype = ortype.get(ocol, default_type)
                if otype in ['ID']:
                    item = '{%s: { id: {%s: %s}} }' % (ocol, oop, ovalue)
                elif ocol in relation_map.keys():
                    item = '{%s: { %s: {%s: %s}} }' % (relation_map[ocol], acol, aop, avalue)                    
                else:
                    item = '{%s: {%s: %s}}' % (ocol, oop, ovalue)
                orfilters.append(item)

        aofilters = ""
        if andfilters:            
            aofilters += ', and: [%s]'%', '.join(andfilters)
        if orfilters:
            aofilters += ', or: [%s]'%', '.join(orfilters)
            
        #print('***====aofilters===***',aofilters)

        if scol and sval:          
            if stype == 'ID' and scol != 'id':
                filters = '{ %s: { id: {%s: %s} } %s}' % (scol, op, sval, aofilters)
            elif scol in relation_map.keys():
                filters = '{ %s: { %s: {%s: %s} } %s}' % (relation_map[scol], scol, op, sval, aofilters)
            else:
                filters = '{%s: {%s: %s} %s}' % (scol, op, sval, aofilters)
        else:
            filters = aofilters
                        

            
        return filters
            
                        
    def unrap_dict_wprefix(self, xin, prefix='', yy = {}, irecord=0):
        x = copy.deepcopy(xin)
        xx = copy.deepcopy(yy)
        
        for name, xa in x.items():        
            newprefix = prefix
            if name not in ['data', 'attributes']:
                if prefix != '':
                    newprefix = '_'.join([prefix, name])
                else:
                    newprefix = name
                                
            if isinstance(xa, dict):                
                d = self.unrap_dict_wprefix(xa, prefix=newprefix, yy=xx)
                xx.update(d)
                
            elif isinstance(xa, list):
                if len(xa) > 0 and isinstance(xa[0], dict):
                    for ix, x in enumerate(xa):
                        d = self.unrap_dict_wprefix(x, prefix=newprefix, yy=xx, irecord=ix)
                        xx.update(d)
                    
            else:
                if irecord > 0:                    
                    d = {f"newprefix_{irecord}": xa}
                else:
                    d = {newprefix: xa}
                xx.update(d)
              
        #print('***====output xx===***',xx)  
        return xx
            
    def execute_query(self, query, variables={}, dataframe=False, raw=True, nopp=False, **kwargs):
        if 'table_name' in kwargs.keys():
            table = kwargs.get('table_name')
        else:
            table = query.split('{')[1].split('(')[0].strip()
            
        response = self.Select_from_table(
                            query=query, 
                            variables=variables)
        

        try:
            newtable = [x for x in response['data'].keys() if x in table or table in x][0]            
            if newtable != table and table != 'me':
                logger.good('***=======*** Autofix table name from %s to %s'%(table, newtable))
                table = newtable
        except:
            pass
        
        meta = {}
        try:
            if 'meta' in response['data'][table].keys():
                meta = response['data'][table].pop('meta', {})
        except:
            pass
        
        #
        if nopp:
            # No post processing
            return response, meta
        
        
        if raw:            
            try:                
                res = response['data'][table]
                if 'data' in res.keys():
                    res = res['data']
                
                if isinstance(res, dict):
                    res = [res]
               
                if not res:
                    return [], meta 
            except Exception as e:
                logger.error(f"Get_From_Query: Unable to parse response for table={table}! {e}")
                print('Query:', query)
                print('Variables:', variables)                
                print('response', response)
                
                
            try:
                rlist = []
                for ra in res:                    
                    #
                    rr = {}                   
                    if 'id' in ra.keys():
                        rr['id'] = ra['id']
                        
                    #                    
                    for name, xa in ra.get('attributes', {}).items():           
                        if isinstance(xa, dict):
                            if 'data' in xa.keys():         
                                d = copy.deepcopy(xa)               
                                dxa = self.unrap_dict_wprefix(d, prefix=name, yy={})
                                rr.update(dxa)
                            else:
                                rr[name] = xa
                        else:
                            rr[name] = xa
                    #
                    rlist.append(rr)                    
                    #
                #print('***=======***',rlist[0].keys())
                return rlist, meta
            except Exception as e:
                logger.error(f"Get_From_Query: Unable to flatten response for table={table}! {e}")     
                print('Res:', res)           
                print(e)
                return res, meta
                    
        try:
            dlist = []
            if table:            
                xa = copy.deepcopy(response['data'][table]['data'])
                if isinstance(xa, dict):
                    d = self.unrap_dict_wprefix(xa, yy={})
                    dlist.append(copy.deepcopy(d))
                elif isinstance(xa, list):
                    if len(xa) > 0 and isinstance(xa[0], dict):                    
                        for x in xa:
                            d = self.unrap_dict_wprefix(x, yy={})                        
                            dlist.append(copy.deepcopy(d))
                else:
                    dlist.append(xa)                            
            else:
                dlist = response    

            #
            if dataframe:
                try:
                    import pandas as pd
                    dfresponse = pd.DataFrame.from_records(dlist).dropna(axis=1, how='all')
                except:
                    logger.warn(f"Pandas not available! Unable to convert response to dataframe!")
                    dfresponse = dlist
            else:
                dfresponse = dlist                                               
                                            
            return dfresponse, meta    
        except:
            logger.warn(f"Get_From_Query: Unable to parse response!")
            return response, meta
        
    def get_from_query(self, *args, **kwargs):
        return self.execute_query(*args, **kwargs)
        
    def create_cv_analysis(self, id, analysis, analysed=True, remark={}):
        query = '''
            mutation AddAnalysis($id:ID!, $analysis:JSON, $remark:JSON, $analysed:Boolean){
                updatePapSuitabilityFeedback(id:$id,data:{
                AnalysisResponse:$analysis,
                remark:$remark,
                analysed:$analysed
                }){
                data{
                id
                attributes{
                    AnalysisResponse
                    remark
                    analysed                    
                }
                }
            }
            }        
        '''   
        logger.good(f"Using run_stage: {self.run_stage}")
        variables = {"id": id, "analysis": analysis, 
                     "analysed": analysed, "remark": remark}
        try:
            res = self.execute_query(query, variables) 
            try:
                res = res[0][0]                                          
            except:
                logger.warn("Unable to parse response for CV analysis!")            
        except Exception as e:
            logger.error(f"Create_CV_Analysis: Unable to Create CV analysis! {e}")
            res = {}
            
        return res
        
    def get_cv_analysis(self, id):
        query = '''
            query getPapSuitabilityFeedback($id:ID!){
                papSuitabilityFeedback(id:$id){
                data{
                id
                attributes{
                    AnalysisResponse
                    analysed
                    remark
                }
                }
            }
            }        
        '''   
        variables = {"id": id}
        try:
            res = self.execute_query(query, variables)          
            res = res[0][0] #['AnalysisResponse']
            #res['analysed'] = res[0][0]['analysed']
        except Exception as e:
            logger.error(f"Get_CV_Analysis: Unable to get CV analysis! {e}")
            res = {}
            
        return res
                
    def get_user_info(self, nopp=True):
        query = '''
            query {
                me {
                    username,
                    email,
                    role {
                        name
                    }
                }
                }        
        '''   
        try:
            response, meta = self.execute_query(query, table_name='me')
            if response:
                try:
                    response = response[0]
                except:
                    print('Me Response', response)
            
            if response:
                response['role'] = response.pop('role', {}).get('name', "")
        except Exception as e:
            logger.error(f"Get_User_Info: Unable to get user info! {e}")
            print('run_stage:', self.run_stage)
            print('token:', self.token)
            response = {}        
        
        return response
                
if __name__ == "__main__":
    obj = StrapiGraphql()
    
#     query = """mutation createUser($username:String!,$email:String!) { register(input: { username: $username, email: $email, password: $email } ) { user { id username email }  } }"""
# variables = {"username": "Nebiyu", "email":"neba.samuel17@gmail.com"}
    variables =  None
    # query = """ query getTraineeId{
    #                 trainees(pagination:{start:0,limit:200} filters:{batch:{Batch:{eq:5}}}){
    #                     data{
    #                     id
    #                     attributes{
    #                         trainee_id
    #                         email
                            
    #                     }
    #                     }
    #                 }
    #                 } """
    # print(obj.Select_from_table(query, variables=variables))
    # variables = {"email": "mahlet@10academy.org", "password":"12341234"}
    # print(obj.get_token())
    print(obj.headers)
