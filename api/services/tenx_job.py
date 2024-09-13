import os, sys
import re
import copy
import json
from datetime import datetime, timedelta
import requests

#
# from pprint import pprint
# from turtle import up
# from typing import overload
# import httpx
# import asyncio
# from audioop import add
# from hmac import new
# from itertools import cycle
# from logging import exception
# from math import e, log
# from nis import match
# from warnings import filters
#

import pandas as pd
from markdown import markdown


from .pathfig import *

import tenx_job_recommender.tenx_ipersona.api.modules.cv_analysis as cv_analysis
from api import config

from api.database.job_schema import JobSchema
from api.services.strapi_graphql import StrapiGraphql
from api.services.strapi_methods import StrapiMethods

from api.utils.logger import LLPackerLogger


logger = LLPackerLogger(os.path.basename(__file__))

capitalize = lambda x: x[0].upper() + x[1:]


from api.modules.leap_base import LeapBaseClass as JobBaseClass
from api.modules.leap_job import JobSchema
from api.modules.leap_job_profile import JobProfileSchema
from api.modules.leap_user_profile import UserProfileSchema
from api.modules.leap_user_job_match import UserJobMatchSchema
from api.modules.leap_user_reaction import UserReactionSchema
from api.modules.leap_generate_assets import AssetGenerationSchema
       
    
class InsertAutoJobRecommendation:
    def __init__(self,  **kwargs) -> None:
     
        self.sm = StrapiMethods(**kwargs)
        self.sg = StrapiGraphql(**kwargs)
    
    def check_job_exists_gql(self, scol, sval):
                
        query = '''
        query getJobs($val: String!) {
            jobs(filters: { %s: { eq: $val }} ) {     
                data {
                    id           
                    attributes {
                        title
                        companyName
                        description
                        link
                        creator
                        slug
                        openDate
                        Role
                        Platform                         
                    }
                }
            }
        }
        '''%scol
        variables = {'val': sval}

        if scol in ['title', 'companyName', 'Role', 'Platform', 'creator', 'slug', 'openDate', 'link', 'description']:            
            res, _ = self.sg.execute_query(query, variables, dataframe=False)
        else:
            logger.error(f"Invalid column={scol} for job search!")
            return []
        
        return res[0]

    def check_job_exists(self, value, col='slug', andcol=[], andvalue=[], single=False,
                         op="eq", table="jobs", limit=0, psize=20, verbose=0):
        '''
        https://docs.strapi.io/dev-docs/api/rest/filters-locale-publication#filtering
        '''
       # sortquery="?sort[0]=title:asc&sort[1]=slug:desc'"
        # filterquery = f"?filters[slug][$eq]={payload['slug']}"
                
        
        if single:
            endpoint = f"?filters[{col}][{op}]={value}"
        else:
            endpoint = f"?pagination[page]=%s&pagination[pageSize]={psize}?filters[{col}][{op}]={value}"
        
        if andcol and andvalue:
            if isinstance(andcol, str):
                andcol = [andcol]
            if isinstance(andvalue, str):
                andvalue = [andvalue]
            assert len(andcol) == len(andvalue), "andcol and andvalue should have the same length"
            for i, (acol, avalue) in enumerate(zip(andcol, andvalue)):
                endpoint += f"&filters[{acol}][$eq]={avalue}"
                
        if verbose>0:
            logger.info(f"Checking if job exists with \n endpoint={endpoint} \n in table={table}...")
                                
        headers = {
                    "Authorization": f"Bearer {self.sm.token}",  
                    "Content-Type": "application/json"
                }
                
        def load_all_pages():
            res = {'data':[]}
            page = 1
            while True:     
                if single:              
                    ep = endpoint
                else:
                    ep = endpoint % page
                url = f"{self.sm.api_url.replace('graphql','api')}/{table}{ep}"
                r = requests.get(url, headers=headers).json()    
                
                if r['data']:
                    for item in r['data']:
                        att = item['attributes']
                        att['id'] = item['id']
                        res['data'].append(item)
                        
                    if page==1:
                        print('page count: ',r['meta']['pagination']['pageCount'])
                        print('total count: ',r['meta']['pagination']['total'])
                                            
                    if page < r['meta']['pagination']['pageCount'] and r['meta']['pagination']['total'] > len(res['data']):
                        print('page: ', page)
                        page += 1
                    else:
                        break    
                    
                    if limit > 0:
                        if len(res['data']) >= limit:
                            break  
                    if single:
                        break
                else:
                    break
                        
            return res 
                                
        #res = asyncio.run(load_all_pages())
        res = load_all_pages()
                
        return res
    
    
    def prepreocess_link(self, x):
        res = x.split("/")
        return '/'.join(res[:-1])
    
    def remove_non_ascii(self, string):
        return ''.join(char for char in string if ord(char) < 128)

    def clean_non_alph_numeric_character(self, x):
        if isinstance(x,str):
            res = re.sub(r'[^a-zA-Z0-9]', '', x)
        else:
            res ="unknown"
        return res

    def generate_single_slug(self, payload, add_date=True):
        title = payload.get('title', "tile:unknown")
        company = payload.get('company', 'company:unknown')
        if add_date:
            date =  datetime.now()
            sl = company +"-"+ title+"-"+ str(date)
        else:
            sl = company +"-"+ title
        
        return sl
                    
    def generate_slug(self,df):
        slug =[]

        for i, row in df.iterrows():
            sl = self.generate_single_slug(row)
            slug.append(sl)
        return slug

    def preprocess_df_jobs(self, df):

        df = df.rename(columns={"date":"openDate",
                                            "post_link":"link",})

        df['openDate'] = pd.to_datetime(df['openDate'], format='%Y-%m-%d')
        df['openDate'].fillna(df['openDate'].mode()[0], inplace=True)
        df['openDate']  = df['openDate'].map(lambda x: datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ'))
        df['description_html'] = df['description_html'].apply(lambda x: self.remove_non_ascii(x))
        df['Role']= df['role']
        df['Platform']="LinkedIn"
        df['creator']= "2"
        df['slug']= df['uuid'] if 'uuid' in df.columns else self.generate_slug(df)
        df ['link'] = df['link'].apply(lambda x: self.prepreocess_link(x))
        return df
    
        
    def insert_to_job_match (self, job_id,job, trainee_job, slug):
        # table= f"https://{root}.10academy.org/api/job-matches"

        table = "job-matches"

        sm = StrapiMethods()
        single_description = trainee_job[trainee_job['description']==job]
        single_description.drop_duplicates(subset=['Name'],inplace=True)
        # single_description.drop_duplicates(subset=['Name'],inplace=True)
        for index, row in single_description.iterrows():
            row_dict= {
                "job":str(job_id),
                "trainee":str(row['id']),
                "creator":2,
                "applied":False,
                "slug":slug,
                "type":"Algorithm", 
                "reson": str(row['MissingSkills']) #feedback
                
            }
            r = sm.insert_data(row_dict,table)
            
    
    def insert_to_jobs(self, df):
        
        # table= f"https://{root}.10academy.org/api/jobs"      
        table = "jobs"

        sm = StrapiMethods()
        job_df = df.drop_duplicates(subset=['description'])
        for index, row in job_df.iterrows():
            row_dict = {
                
                "companyName":row['company'],
                "description":row['description_html'].replace("\n",""),
                "title":row['title'], 
                "link":row['link'],
                "creator":row['creator'],
                "slug":row['slug'], 
                "openDate":row['openDate'],
                "Role":row['Role'],
                "Platform":row['Platform'] 
                }
        
            res = sm.insert_data(row_dict, table) 
            
            if res is None:
                logger.error(f"Unable to insert the following dict to tenx table={table}...........")
                logger.error(f"{row_dict}")
            else:
                logger.good(f"Successfully registered Job in Tenx table={table}!")
                self.insert_to_job_match ( job_id= res['data']['id'], job= row['description'], trainee_job=df, slug=row['slug'])


    def insert_recommended_data(self, df):
        
        assert isinstance(df, pd.DataFrame), "df should be a pandas dataframe"
        
        # df = get_recommendation_deta  ils()
        jobs_df = self.preprocess_df_jobs(df)
        if df.empty:
            logger.error("Unable to find recommendation data")
        else:
            logger.info("Inserting recommendation data...")
            self.insert_to_jobs( df=jobs_df)
            
          
    #---------------------------------------------      
    #---------------- SCV based algo -------------
    #---------------------------------------------
    def preprocess_single_job_entry(self, payload, uuid="", 
                                    platform="LinkedIn", creator="2"):
        
        
        openDate = payload.get('post_date', datetime.now())
        if isinstance(openDate, str):
            openDate = datetime.strptime(openDate, '%Y-%m-%d').isoformat()
        elif isinstance(openDate, datetime):
            openData = openDate.isoformat()
        else:
            openDate = datetime.now().isoformat()
            
        print('openDate:', openDate)
            
        email = payload.get('email', [])
        trainee_id = payload.get('tenx_trainee_id',[])
        alluser_id = payload.get('tenx_alluser_id', [])
        slug = uuid if uuid else self.generate_single_slug(payload)        
        link = payload.get('post_link', payload.get('link', ''))
        description_html = payload.get('description_html', '')
        title = payload.get('title', "")
        role = payload.get('role')
        company = payload.get('company')
        remark = payload.get('remark', "")
        output = {
            "company":company,
            "description_html":description_html.replace("\n",""),
            "title": title, 
            "link":link,
            "creator":creator,
            "slug":slug, 
            "openDate":openDate,
            "role":role,
            "platform":platform,
            "trainee_id":trainee_id,
            "alluser_id":alluser_id, 
            "email": email,   
            "remark": remark
            }
        
        valid = all([output['description_html'], output['link'], output['creator']])
        d = "\r link={}, \r description={}, \r creator={}".format(output['link'], output['description_html'], output['creator'])
        assert valid, f"Invalid Job payload! Missing required fields: {d}"
        
        return output, valid
   
       
    def insert_single_recommendation_entry(self, payload, **kwargs):
        
        table = "job-matches"        
        sm = kwargs.get('sm', self.sm)
        
        logger.divider(f"Inserting Recommendation to Tenx table={table} ...")
        

        jobid = payload['job_id']
        tid_list = payload['trainee_id']
        email_list = payload['email']
        rlist = []
        for tid, email in zip(tid_list, email_list): 
            try: 
                r = self.check_job_exists(payload['slug'], andcol=['job'], andvalue=[str(jobid)], table=table)
            except Exception as e:
                logger.error(f"Error checking job recommendation with slug={payload['slug']} and email={email} in Tenx!")
                r = {'data':[]}
                
            if r['data']:
                logger.good(f"Job Recommendation with slug={payload['slug']} and email={email} already exists in Tenx!")       
            else:                          
                row_dict= {
                    "job":str(jobid),
                    "trainee":str(tid),
                    "creator":2147,  #nana -> 2-Mahi, yabi-1429 (all user table)
                    "applied":False,
                    "slug": str(payload['slug']),
                    "type":"Algorithm", 
                    "reson": {'Professional Summary':"KNN Based Algorithm. Process follows LLMParse (Job) -> LLMGen (IdealProfile) -> SemanticMatch (TraineeProfile)"}                                        
                }

                r = sm.insert_data(row_dict,table)
                
            try:                
                data = r['data']
                if isinstance(data, list):
                    data = data[0]
                if isinstance(data, dict):   
                    ritem = {'email':email, 'tid':tid, 'tenx_rid':data['id']}
                    rlist.append(ritem)
                    logger.good(f"Successfully `Recommended` jobid={jobid} for email: {email}!")
            except:
                logger.error(f"Unable to register `Recommendation` in Tenx! Result from Job insertion: ")
                print(r)
                raise
                
        
        return rlist
               
    def associate_job_with_trainee(self, uuid, email, tid, slug="", job_id="", op='eq'):
        payload = {'slug': slug, 
                'remark':{}, 
                'email':email, 
                'trainee_id':tid}
        
        # quit if slug is not provided
        if not slug:
            logger.error(f'Invalid slug={slug} for job search!')
            return []
        
        # if job_id is not provided, check if job exists with slug
        if job_id:
            logger.info(f'Using provided job_id={job_id} ...')
            payload['job_id'] = job_id
        else:            
            logger.info(f'checking if job exists with slug={payload["slug"]} ...')
            res = self.check_job_exists(payload['slug'], table='jobs', op=op)
        
            data_list = res['data']
            if data_list:
                data_dict = data_list[0]
                logger.good(f"Job with slug={payload['slug']} already exists in Tenx!") 
                payload['job_id'] = data_dict['id']
            else:
                logger.error(f"Job with slug={payload['slug']} does not exist in Tenx!") 
                return []        
        
        # add single recommendation entry
        try:                             
            res = self.insert_single_recommendation_entry(payload)  
            logger.good(f"Successfully registered `Recommendation` in Tenx!")
            return res
        except Exception as e:  
            res = {}              
            logger.error(f"Unable to register `Recommendation` in Tenx! Result from Job insertion: ")
            print(data_dict)
            print('Error:', e)
            return []        
            
        
                    
    def insert_single_job_entry(self, payload, **kwargs):
        
        table = "jobs"        
        sm = kwargs.get('sm', self.sm)        

        logger.divider(f"Inserting Job to Tenx table={table} ...")
        row_dict = {
            
            "companyName":payload['company'],
            "description":payload['description_html'].replace("\n",""),
            "title":payload['title'], 
            "link":payload['link'],
            "creator":payload['creator'],
            "slug":payload['slug'], 
            "openDate":payload['openDate'],
            "Role":payload['role'],
            "Platform":payload['platform'] 
            }
    
        res = self.check_job_exists(payload['slug'], table=table)
        data_list = res['data']
        if data_list:
            data_dict = data_list[0]
            logger.good(f"Job with slug={payload['slug']} already exists in Tenx!") 
            old=True  
        else:      
            logger.info(f"Inserting Job with slug={payload['slug']} to Tenx table={table} ...")      
            res = sm.insert_data(row_dict, table) 
            old=False
            data_dict = res['data']
            if 'error' in res:
                logger.error(f"Unable to insert job to tenx! Response from Job entry is: ")
                logger.error(f"{res}")
        # 
        if data_dict:
            if not old:
                logger.good(f"Successfully registered `Job` in Tenx!")
            try:
                payload['job_id'] = data_dict['id']                 
                res = self.insert_single_recommendation_entry(payload)  
                logger.good(f"Successfully registered `Recommendation` in Tenx!")
                success = True
            except Exception as e:  
                res = {}              
                logger.error(f"Unable to register `Recommendation` in Tenx! Result from Job insertion: ")
                print(data_dict)
                print('Error:', e)
                success = False            
        else:
            logger.error(f"Unable to insert job & recommendation to tenx!")        
            success = False
            res = {} 
            
        return res
       
    def add_scv_matched_jobs(self, input):
        
        resdict = copy.deepcopy(input)
        assert isinstance(resdict, dict), "resdict should be a dictionary"
        
        res = []
        
        for job_uuid, data in resdict.items():
            person_ids = data.pop("person_ids",[])
            job_payload = data.pop('reference_job', {})
                        
            #
            if not job_payload:
                logger.error("Unable to find job payload")
                continue
            else:
                # check html description exists
                html_content = job_payload.get('html', job_payload.get('description_html',""))
                if html_content:
                    job_payload['description_html'] = html_content
                else:
                    logger.error("Unable to find job description")
                    continue
                    
                # Convert content to HTML and add it with description
                markdown_text_head = """
____
###
# The job you are looking for is here! Ensure to Apply before the deadline!                                
###
____
#
_**Auto Job Recommendation**_ thinks the following job matches your skill, knowledge, and experience. The recommendation is based comparing your profile with the job requirements. Moreover, To help you adjust your CV and cover letter, we have analysed the job description below and 10 other similar jobs, and extracted the key elements and synthesized an Ideal CV below. Make sure to check it out!
#
____
# **Job Description Begins Here**
#
____            
                """                
                if 'content' in data:                                                            
                    markdown_text_tail = """
___
###
# **Job Description Ends Here**
###
___


Below this line is _a profile adjustment recommendation_. To generate the below profile items, the current job is compared with 10 other similar jobs, and the required skill, knowledge, experience, and other relevant details are extracted and summarised. The extracted elements are optimised such that a person with similar (hence the name Ideal Profile) profile is likely to be selected by the team who advertised the job.  Our recommendation is therefore the following

1) _**highlight skills and knowledge listed below in your portfolio as well as when in follow up interviews and cover letters**_

2) _**if your skill is not strong in the the areas mentioned, upskill yourself for the future**_

Make sure to adjust your CV and cover letter accordingly! 

___
###
# **Ideal Profile for jobs like above Begins here**
###
___                           
                    """ + data['content']
                    html_content = markdown(markdown_text_tail)                
                    job_payload['description_html'] += html_content
                    
                
                # add header
                html_content = markdown(markdown_text_head)
                job_payload['description_html'] = html_content + job_payload['description_html']  
                           
                # check post link exists
                links = job_payload.get('links', '')
                if links:
                    for k in ['post_link', 'apply_end_date']:
                        if k in links:
                            job_payload[k] = [x.strip().replace(f'{k}:', '') for x in links.split(",") if k in x][0]
                            
                if not job_payload.get('post_link', ''):
                    logger.error("Unable to find post link")
                    continue                                
                    
                # add dates if exists
                dates = job_payload.get('dates', '')
                if dates:
                    for k in ['post_date', 'apply_end_date']:
                        if k in dates:
                            kval = [x.strip().replace(f'{k}:', '') for x in dates.split(",") if k in x][0]
                            print(k, kval, len(kval), dates.split(","))
                            job_payload[k] = kval.strip() if len(kval) > 0 else datetime.now().isoformat()
                            
                        
                # add remark if exists
                if 'remark' in data:
                    job_payload['remark'] = {'Professional Summary':data.get('remark', 
                                                     "KNN Based Algorithm. Process follows LLMParse(Job) -> LLMGen(IdealProfile) -> SemanticMatch(TraineeProfile)")
                    }
                else:
                    job_payload['remark'] = {}
            
            #
            if not person_ids:
                logger.error("Unable to find person ids")
                continue
            
            
            # Extract person ids
            if isinstance(person_ids, str):
                pid_list = [x.strip() for x in person_ids.split(", ") if x]
            elif isinstance(person_ids, list):       
                pid_list = person_ids
            else:         
                logger.error("Unable to parse person ids:")
                print(person_ids)
                continue
                        

            for k in ['email','tenx_trainee_id', 'tenx_alluser_id']:
                job_payload[k] = []
                
            for person_id in pid_list:
                for p in [x.strip() for x in person_id.split(",") if x]:
                    for k in ['email','tenx_trainee_id', 'tenx_alluser_id']:
                        if k in p:
                            v = p.replace(f"{k}:","").strip()
                            job_payload[k].append(v)


  
            #Inserting Job to Tenx 
            payload, valid = self.preprocess_single_job_entry(job_payload, uuid=job_uuid)
            
            if valid:
                res = self.insert_single_job_entry(payload)
                if res:
                    logger.good("Successfully registered Job and Recommendation in Tenx!")
                else:
                    logger.error("Unable to register Job/Recommend job!")
            else:
                logger.error("Invalid Job payload!")
                logger.info(f"{payload}")
                res = None
            
        return res
        
    


def associate_from_job_scv_uuid_map(job_scv_map, ajr=None, stage='prod', use_juuid=True, 
                                    person_autocut=2, knn_person=0, dataframe=True, 
                                    maxloop=0, offset=0, max_match=40, **kwargs):
    
    jsc = JobSchema()
    
    if ajr is None:
        ajr = InsertAutoJobRecommendation(run_stage=stage)
        
    email_counter = {}
    iloop = 0
    job_pcv_match = []
    job_match_res = []
    for juuid, suuid in job_scv_map.items():
        
        # check if maxloop is reached
        iloop += 1            
        if maxloop > 0:
            if iloop > maxloop:
                break
        if offset > 0:
            if iloop < offset:
                continue
                    
        # get job slug from uuid
        slug = f"job:uuid:{juuid}"
                
        # get job id from slug
        res = ajr.check_job_exists(slug, col='slug', single=True)
        data_list = res['data']
        if data_list:
            job_id = data_list[0]['id']
            logger.good(f"Job with slug={slug} already exists in Tenx as job_id={job_id}!")
        else:       
            logger.warn(f"Job with slug={slug} does not exist in Tenx! Skipping...")
            print(res)
            continue
        

    
        
        logger.divider("")        
        print('Job (tenx_id, slug): ', (job_id, slug))
        print('Simulated CV UUID: ', suuid)
        logger.divider("")
        
        if use_juuid:
            uuid = juuid
            class_name = 'Job'
        else:
            uuid = suuid
            class_name = 'SimulatedCV'
            
        object = jsc.weaviate.load_by_uuid(uuid, 
                                            class_name=class_name, 
                                            return_vector=True)
                
        if object:                                        
            res_person = jsc.search(vector=object[0]['vector'], 
                                    class_name='PersonCV',
                                    autocut=person_autocut, 
                                    limit=knn_person)
            if res_person:
                print('Number of Person CVs Matched to SCV: ', len(res_person))
                person_ids = [x['personid'] for x in res_person if 'personid' in x]
                match_distance = [x['distance'] for x in res_person if 'distance' in x]
                if len(person_ids) < 1:
                    logger.warn("No Person CVs Matched to SCV!")
                    continue                        
                
                trainee_list = {}
                for k in ['email','trainee_id', 'tenx_alluser_id']:
                    trainee_list[k] = []
                                
                item = []                
                for person_id, distance in zip(person_ids, match_distance):
                    entry = {'job_uuid': juuid, 'scv_uuid': suuid, 'distance': distance}
                    
                    skip_person = False
                    for p in [x.strip() for x in person_id.split(",") if x]:
                        for k in ['email','tenx_trainee_id', 'tenx_alluser_id']:
                            if k in p:
                                v = p.replace(f"{k}:","").strip()
                                entry[k] = v
                                if k=='tenx_trainee_id':
                                    trainee_list['trainee_id'].append(v)
                                else:
                                    trainee_list[k].append(v)
                                    
                                if k=='email':
                                    if v in email_counter:
                                        if email_counter[v] > max_match:
                                            skip_person = True
                                        email_counter[v] += 1
                                    else:
                                        email_counter[v] = 1
                                
                    if skip_person:
                        logger.warn(f'Skipping person with email={entry["email"]} as it has reached max_match limit={max_match}!')
                        continue
                    else:
                        item.append(entry)     
                    
                email = trainee_list['email']
                tid = trainee_list['trainee_id']
                print('Trainee Emails Matched: ', email)
                                
                res =  ajr.associate_job_with_trainee(juuid, email, tid, job_id=job_id, slug=slug, op='eq')
                
                #
                if res:
                    job_match_res.extend(res)      
                    #print('Person CVs Matched: ', item)
                    job_pcv_match.extend(item)       
                
    dfjpcv = job_pcv_match
    dftenxmatch = job_match_res
    if dataframe:
        try:
            dfjpcv = pd.DataFrame.from_records(job_pcv_match)
        except Exception as e:
            print(e)
            dfjpcv = job_pcv_match
            
        
    if dataframe:
        try:
            dftenxmatch = pd.DataFrame.from_records(job_match_res)
        except Exception as e:
            print(e)
            dftenxmatch = job_match_res
            
    return dfjpcv, dftenxmatch
    
if __name__ == "__main__":
    
    obj = InsertAutoJobRecommendation()
    # obj.insert_recommended_data()