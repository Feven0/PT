from hmac import new
import pandas as pd
import os, sys, copy
import json
import operator
from functools import reduce
from pprint import pprint

from api import config
from api.utils.logger import LLPackerLogger
from api.services.strapi_graphql import StrapiGraphql

logger = LLPackerLogger(os.path.basename(__file__))


def extract_gql_result(res, keys):
    '''
    Use reduce() to traverse the dictionary
    '''
    try:
        return reduce(operator.getitem, keys, res)
    except:        
        return []


class TenxUtils:
    def __init__(self, **kwargs) -> None:
        
        self.sg = StrapiGraphql(**kwargs)
   
    def get_from_query(self, *args, **kwargs):
        return self.sg.get_from_query(*args, **kwargs)
    
    def unrap_dict(self,x, prefix=''):
        xx = {}
        for name, xa in x.items():                                
            if isinstance(xa, dict):                
                d = self.unrap_dict(xa)
            elif isinstance(xa, list):
                if len(xa) > 0 and isinstance(xa[0], dict):
                    for x in xa:
                        d = self.unrap_dict(x)
                        xx.update(d)
                else:
                    d = {name: xa}
                    xx.update(d)
            else:
                d = {name: xa}
                xx.update(d)
        return xx
       


    def df_from_json(self, res, table='assignments'):
        dlist = []
        for name, xa in res.items():
            if len(extract_gql_result(xa, [table, 'data']))==0:
                continue

            if isinstance(xa[table]['data'], dict):
                d = self.unrap_dict(xa)
            elif isinstance(xa[table]['data'], list):

                if len(xa[table]['data']) > 0 and isinstance(xa[table]['data'][0], dict):
                    for x in xa[table]['data']:

                        d = self.unrap_dict(x)

                        dlist.append(d)

        return pd.DataFrame(dlist)
            
    # def get_challenge_document(self, challenge_id):
    #     query = """
    #             query getChallenge($id: ID) {
    #                 challengeDocument(id: $id) {
    #                     data {
    #                     id
    #                     attributes {
    #                         week
    #                         batch
    #                         slug
    #                         subtitle
    #                         Title
    #                         layout
    #                         type
    #                         slug
    #                         challenge_sections (pagination:{start:0,limit:100}){
    #                         data {
    #                             id
    #                             attributes {
    #                             slug
    #                             Tag
    #                             content
    #                             hasFeedback
    #                             references(pagination:{start:0,limit:100}) {
    #                                 data {
    #                                 id
    #                                 attributes {
    #                                     link
    #                                     Title
    #                                 }
    #                                 }
    #                             }
    #                             }
    #                         }
    #                         }
    #                     }
    #                     }
    #                 }
    #                 }
    #     """     
    #     res_json = self.sg.Select_from_table(
    #                         query=query, variables={"id": challenge_id})
    #     #
    #     data = (res_json.get("data", {})
    #                     .get("challengeDocument", {})
    #                     .get('data', {})
    #                     .get('attributes', {})
    #                     )
    #     print("the content of the data",res_json)
        
    #     # rename Title to title
    #     if 'Title' in data.keys():
    #         data['title'] = data.pop('Title', '')
            
    #     #
    #     layout = data.pop('layout',[])
    #     sections = data.pop('challenge_sections', {})
        
    #     content = {slug: f"Section Title: {cnt.get('title')} \n {cnt.get('content')}"
    #                for x in sections.get('data', [])
    #                if (cnt := x.get('attributes', {}).get("content",{})) 
    #                and (slug := x.get('attributes', {}).get("slug",{}) )
    #     }
        


    #     metadata = data
    #     #
    #     content = '\n'.join([content[k] for k in layout if k in content.keys()])
    #     content = content.replace('<p>', '').replace('</p>', '')
    #     content = f"Challenge Title: {metadata.get('title','')} \n {metadata.get('subtitle','')} \n {content}"
        
    #     return content, metadata
                       
    def get_challenge_document(self, challenge_id):
        query = """
                query getChallenge($id: ID) {
                    challengeDocument(id: $id) {
                        data {
                        id
                        attributes {
                            week
                            batch
                            slug
                            subtitle
                            Title
                            layout
                            type
                            slug
                            challenge_sections (pagination:{start:0,limit:100}){
                            data {
                                id
                                attributes {
                                slug
                                Tag
                                content
                                hasFeedback
                                references(pagination:{start:0,limit:100}) {
                                    data {
                                    id
                                    attributes {
                                        link
                                        Title
                                    }
                                    }
                                }
                                }
                            }
                            }
                        }
                        }
                    }
                    }
        """     
        res_json = self.sg.Select_from_table(
                            query=query, variables={"id": challenge_id})
        #
        data = (res_json.get("data", {})
                        .get("challengeDocument", {})
                        .get('data', {})
                        .get('attributes', {})
                        )
        
        # rename Title to title
        if 'Title' in data.keys():
            data['title'] = data.pop('Title', '')
            
        #
        layout = data.pop('layout',[])
        sections = data.pop('challenge_sections', {})
        
        content = {}
        git_tag_content = ""  # Placeholder for content of section with "git" tag

        for section_data in sections.get('data', []):
            attributes = section_data.get('attributes', {})
            slug = attributes.get('slug', "")
            tag = attributes.get('Tag', "")
            section_content = attributes.get('content', {})
            
            # Store section content by slug
            content[slug] = f"Section Title: {section_content.get('title', '')} \n {section_content.get('content', '')}"
            
            # Check if this is the "git" tagged section and store its content separately
            if 'git' in tag.lower():  # Case-insensitive check
                git_tag_content = section_content.get('content', '')
                git_tag_content = git_tag_content.replace('<p>', '').replace('</p>', '\n')

        # Order content according to the layout
        ordered_content = '\n'.join([content[k] for k in layout if k in content])
        ordered_content = ordered_content.replace('<p>', '').replace('</p>', '\n')
        metadata = data
        # Challenge content without altering
        challenge_content = f"Challenge Title: {metadata.get('title', '')} \n {metadata.get('subtitle', '')} \n {ordered_content}"
        
        # the git tagged section 
    
        if git_tag_content:
            metadata['git_tag_content'] = git_tag_content

        return challenge_content, metadata               

    def get_graded_assignment(self, name):
        query = """
                query Assignments($name: String!) {
                    assignments(
                        pagination: { start: 0, limit: 100 }
                        filters: { assignment_category: { name: { eq: $name } } }
                        sort: "id"
                    ) {
                        data {
                        id
                        attributes {
                            trainee {
                            data {
                                attributes {
                                email
                                trainee_id
                                all_user{
                                    data{
                                    attributes{
                                        name
                                    }
                                    }
                                }                  
                                }
                            }
                            }
                            
                            gclass_submission_identifier
                            assignment_responses(
                            sort: "createdAt:desc"
                            pagination: { start: 0, limit: 1 }
                            ) {
                            data {
                                id
                                attributes {
                                mark,
                                returned
                                content
                                }
                            }
                            }
                        }
                        }
                    }
                    }
                    
                """
        gradeJson = self.sg.Select_from_table(
                            query=query, variables={"name": name})
        dfresponse = self.df_from_json(gradeJson)
        return dfresponse
    
    def fetch_assignment_response(self,acid):
        sg = StrapiGraphql()
        query = """query getAllAssignemnts($id:ID!){
            assignmentCategory(id:$id){
            data{
                attributes{
                name
                rubric_type
                current_rubric
                due_date
                assignments(pagination:{start:0,limit:1000}){
                    data{
                    id
                    attributes{
                    assignment_submission_content
                    trainee{
                        data{
                        id
                        }
                    }
                    }
                    }
                }
                }
            }
            }
        }"""
        res_json = self.sg.Select_from_table(query=query, variables={"id":acid})    
        return res_json

    def fetch_grade_response(self, sid):
        sg = StrapiGraphql()
        ### fetch recent graded mark 
        
        query= """query getAssingment($assignmet_id:ID){
        assignment(id:$assignmet_id){
            data{
            id
            attributes{
                assignment_responses(pagination:{start:0,limit:1}
                 sort: "createdAt:desc"){
                data{
                    id
                    attributes{
                      reviewer{
                        data{
                          id
                        }
                      }
                      rubric_id
                      mark
                      content
                      llm_response
                      rubric_status
                      AdHoc
                    }
                }
                }
            }
            }
        }
        }"""
        res_json  = self.sg.Select_from_table(query=query, variables={"assignmet_id":sid})
        return res_json

    def has_mark(self,sid, **kwargs):
        data = self.fetch_grade_response(sid)
        responses = (data.get('data', {})
                        .get('assignment', {})
                        .get('data', {})
                        .get('attributes', {})
                        .get('assignment_responses', {})
                        .get('data', [])
        )

        if len(responses) == 0:
            return False
        
        for response in responses:
            if 'mark' in response.get('attributes', {}):
                return True

            return False
            
    def has_submission_been_graded(self, sid):
        return self.has_mark(sid)

    def get_dummy_rubrics_content_(self, smgrubric_id):

        query = """query getsmgRubric($id:ID){
                    smgRubric(id:$id){
                        data{
                        id
                        attributes{
                            content
                            target
                            smg_dummy_rubric{
                            data{
                                attributes{
                                content
                                }
                            }
                            }
                        }
                        }
                    }
                    }"""
        res = self.sg.Select_from_table(query, variables = {"id":smgrubric_id})
        smgdummyrubrics = res ['data']['smgRubric']['data']['attributes']['smg_dummy_rubric']['data']['attributes']['content']
        return smgdummyrubrics
    
    def get_rubrics_content_based_on_rubric_id(self, rubric_id):
        logger.log_info('get_rubrics_content_based_on_rubric_id', 
                        f'extracting rubrics for rubric_id={rubric_id}')
        
        query = """ query getrubrics ($id:ID!){
                    rubrics(pagination:{start:0,limit:200}, filters:{id:{eq:$id}} )
                                        {
                            data {
                            id
                            attributes {
                            
                                name
                                content
                                type
                                AdHoc
                            }
                            }
                        }
                        }"""
        rubricJson = self.sg.Select_from_table(
                            query=query, variables={"id": rubric_id})
        
        res = extract_gql_result(rubricJson, ['data','rubrics','data'])
        if len(res)>0:
            rubric =  res[0]
            resx = extract_gql_result(rubric, ['attributes','content'])
            if len(resx)>0:
                rubric = resx
                if rubric:
                    logger.good('rubric found')
                    return rubric
                else:
                    logger.warn('rubric not found')
                    return {}   
        else:
            logger.warn('rubric not found')
            return {}            
 
    def get_rubrics_content_from_smg_rubrics(self, rubric_id, dummy=False):
        query = """
        query getsmgrubrics ($id:ID!){
   smgRubrics(pagination:{start:0,limit:200}, filters:{id:{eq:$id}} )
					{
          
            data{
              id
              attributes{
                content
              	title
                tag
                smg_dummy_rubric{
                  data{
                    id
                  }
                  
                }
              }
              
            }
          }
}
        """
        rubricJson = self.sg.Select_from_table(
                            query=query, variables={"id": rubric_id})
        
        res = extract_gql_result(rubricJson, ['data','smgRubrics','data'])

        padd = 'In your response MAKE SURE that metrics keys are EXACTLY '
        try:
            tenxrubrics =  self.get_dummy_rubrics_content_(rubric_id)
            keys = ', '.join([x['title'] for x in tenxrubrics])
            padd += f' one of: {keys}'
        except:
            padd += ' as defined in the rubric'

        if len(res)>0:
            rubric =  res[0]   
            resx = extract_gql_result(rubric, ['attributes','content'])  
   
            if len(resx)>0:
                prompt =  resx +'/n' + padd
            else:
                prompt = ""
        else:
            prompt = ""

        if dummy:
            return prompt, tenxrubrics
        else:
            return prompt

    def get_rubrics(self, *args, **kwargs):
        try:
            # first try getting smg rubrics
            return self.get_rubrics_content_from_smg_rubrics(*args, **kwargs)
        except:
            # if that fails, try getting rubrics from rubrics table
            
            padd = 'In your evaluation MAKE SURE you use the following metrics keys EXACTLY as they are'
            try:
                res = self.get_rubrics_content_based_on_rubric_id(*args, **kwargs)
                keys = ', '.join([x['title'] for x in res])
                padd += f' one of: {keys}'
            except:
                padd += ' as defined in the rubric'

            if kwargs.get('dummy', True):
                return padd, res
            else:
                return json.dumps(res)   


    def save_to_assignment_response(self, params:dict):
    
        try:
            variables = {"id":params['assignment_id'],
                        "reviewer_id":params['reviewer_id'], #default for dev                        
                        "rubric_id": params['rubric_id'],
                        "AdHoc":{'assignment_id':params['assignment_id'],
                                 'vdb_id':params['vdb_id'],
                                 "vdb_name":params["vdb_name"]},
                        "mark": params['mark'],
                        "rubric_status":params['rubric_status'],                                 
                        "rubric":params['rubric'],                                 
                        "llm_response":params['llm_response'],
                        "rubric_type":"smart", 
                        }    
        
            query = """ mutation createAssignmentResponse(
                        $id: ID!
                        $reviewer_id: ID!
                        $rubric_id: String                        
                        $AdHoc:JSON
                        $mark: Float!
                        $rubric_status: ENUM_ASSIGNMENTRESPONSE_RUBRIC_STATUS!
                        $rubric: JSON                        
                        $llm_response: JSON
                        $rubric_type:String
                        ) {
                        createAssignmentResponse(
                            data: {
                            assignment: $id
                            reviewer: $reviewer_id
                            content: $rubric
                            AdHoc:$AdHoc
                            mark: $mark
                            rubric_id: $rubric_id
                            rubric_status: $rubric_status
                            llm_response:$llm_response
                            rubric_type:$rubric_type
                            }
                        ) {
                            data {
                            id
                            
                            }
                        }
                        }"""   
            res = self.sg.Select_from_table(query=query, variables=variables)            

        except Exception as e:
            print(f"unable to save result for id {params['id']} {e}")
     
     
#======================================================================================================
#=================================== TENX JOB MATCHES =================================================
#=====================================================================================================
#
def get_all_tenx_job_matches(run_stage='prod', raw=False, dataframe=True, applied=False, filter=""):
    #
    sg = StrapiGraphql(run_stage=run_stage)
    
    #
    gquery = '''
    query getJobMatches($type: String!, $applied: Boolean!, $page: Int!, $pageSize: Int!) {
        jobMatches(pagination: { page: $page, pageSize: $pageSize }, filters: {type: {eq: $type}, and: [{Applied:{eq:$applied}} %s]} ) {
            meta {
                pagination {
                    page
                    pageSize
                    total
                    pageCount
                }
            }          
            data {
                id           
                attributes {
                    trainee {
                        data {
                            id
                        }
                    }
                    slug
                    Applied
                    type
                    job {
                        data {
                            id
                            attributes {
                                slug
                            }
                        }                    
                    }                              
                }
            }
        }
    }
    '''%filter
    gvariables = {"type": "Algorithm", "applied":applied, "page": 1, "pageSize": 1000}

    if dataframe:
        jobmatchdf = pd.DataFrame()
    else:
        jobmatchdf = []
        
    reslist = []
    res = []
    while True:
        res, meta = sg.get_from_query(gquery, gvariables, dataframe=dataframe, raw=raw)
        reslist.append(res)
        if meta['pagination']['page'] == meta['pagination']['pageCount'] \
            or meta['pagination']['pageCount']==0 \
                or meta['pagination']['total']==0:
            break
        
        gvariables['page'] += 1
        

    if len(reslist) > 1 and dataframe:
        jobmatchdf = pd.concat(reslist)
    elif len(reslist) == 1:
        jobmatchdf = reslist[0]
        

    if len(jobmatchdf) > 0 and dataframe:
        for x in ['reference_job_uuid_', 'job:uuid:']:
            nt = jobmatchdf.slug.str.contains(x).sum()
            print(f'Number of jobs with prefix={x} in slug:', nt)
        jobmatchdf.info()
    else:
        print('No job matches found')
        pprint(meta)
    
    return jobmatchdf       


def delete_all_tenx_job_matches(jobmatchdf, run_stage='prod', **kwargs):  
    #
    sg = StrapiGraphql(run_stage=run_stage)
    
    #
    dquery = '''
    mutation deleteJobMatch($id: ID!){
        deleteJobMatch(id: $id) {
        data {
            id
            attributes {
            slug
            }
        }
        }
    }
    '''
    dvariables = {"id": ""}
    
    total = jobmatchdf.shape[0]
    deleted_job_matches = []
    iloop = 0
    for x, row in jobmatchdf[['id', 'trainee_id', 'job_id']].iterrows():            
        id = row.to_dict()['id']
        dvariables['id'] = id
        res, meta = sg.get_from_query(dquery, dvariables, dataframe=False)
        if res:
            deleted_job_matches.append(res)
            if iloop%20==0:
                print(f'==> {iloop}/{total} job matches deleted so far')

    return deleted_job_matches

def delete_tenx_duplicate_job_matches(jobmatchdf, run_stage='prod', **kwargs):  
    #
    sg = StrapiGraphql(run_stage=run_stage)
    
    #
    dquery = '''
    mutation deleteJobMatch($id: ID!){
        deleteJobMatch(id: $id) {
        data {
            id
            attributes {
            slug
            }
        }
        }
    }
    '''
    dvariables = {"id": ""}
    
    dfg = jobmatchdf[['id', 'trainee_id', 'job_id']].groupby(['trainee_id', 'job_id'])
    deleted_job_matches = []
    for name, group in dfg:
        if group.shape[0]>1:
            print('---')
            print(group.reset_index(drop=True))
            for x, row in group.iloc[0:-1].iterrows():
                id = row.to_dict()['id']
                dvariables['id'] = id
                res, meta = sg.get_from_query(dquery, dvariables, dataframe=False)
                if res:
                    deleted_job_matches.append(res)
                    print(res)
            print('---')

    return deleted_job_matches
  
  
def get_all_tenx_jobs(maxjobs=0, run_stage='prod', raw=False, dataframe=True, filter=""):
    #
    sg = StrapiGraphql(run_stage=run_stage)
    
    #
    page_size  = min(1000, maxjobs) if maxjobs > 0 else 1000
    query = '''
    query getJobs( $page: Int!, $pageSize: Int!) {
        jobs( pagination: { page: $page, pageSize: $pageSize %s } ) {     
            meta {
                pagination {
                    page
                    pageSize
                    total
                    pageCount
                }
            }      
            data {
                id           
                attributes {
                    Role
                    description
                    title
                    companyName                
                    link                
                    slug                           
                }
            }
        }
    }
    '''%filter
    
    variables = {"page": 1, "pageSize": page_size}

    if dataframe:
        tenxdf = pd.DataFrame()
    else:
        tenxdf = []
        
    reslist = []
    res = []

    while True:
        res, meta = sg.get_from_query(query, variables, dataframe=dataframe, raw=raw)
        reslist.append(res)
        if meta['pagination']['page'] == meta['pagination']['pageCount'] \
            or meta['pagination']['pageCount']==0 \
                or meta['pagination']['total']==0:            
            break
        variables['page'] += 1
        
        if len(reslist) > maxjobs and maxjobs > 0:
            break
        

    if len(reslist) > 1 and dataframe:
        tenxdf = pd.concat(reslist).drop_duplicates(subset=['slug'])
    elif len(reslist) == 1:
        tenxdf = reslist[0]

    if len(tenxdf) > 0 and dataframe:
        for x in ['reference_job_uuid_', 'job:uuid:']:
            nt = tenxdf.slug.str.contains(x).sum()
            logger.info(f'Number of jobs with prefix={x} in slug:', nt)
    else:
        logger.info('No jobs found')
        pprint(meta)  
        
    return tenxdf   