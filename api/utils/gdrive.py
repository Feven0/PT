from __future__ import print_function
import os, sys
import pickle
import os.path
import io
import json
import copy
from datetime import date, datetime
#
import collections as cl
import cachetools.func
import functools

import numpy as np
import pandas as pd

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
import googleapiclient

#
from api.services.secret import get_auth
from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(__file__)

#https://developers.google.com/classroom/guides/auth
class gauth():
    guser = 'service'

    if guser=='service':
        fauth = 'admin-10ac-service.json'
        ftoken = 'admin_service_token.pickle'
        user_email = 'yabebal@10academy.org'
    else: 
        fauth = 'admin-10ac-oauth.json'
        ftoken = 'admin_oauth_token.pickle'
        user_email = None
        
class google_api():
    
    def __init__(self, 
                 token_file='token.pickle',
                 fauth='admin-10ac-service.json', 
                 SCOPES=None,
                 user_email=None,
                 verbose=1):
        
        if SCOPES is None:
            #reference: https://developers.google.com/classroom/guides/auth
            self.SCOPES = [
                #with ability to use files/images stored in drive
                'https://www.googleapis.com/auth/drive',
                #to edit slides
                'https://www.googleapis.com/auth/presentations',
                #to sheet
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                #ref: 
                #https://developers.google.com/admin-sdk/reports/v1/appendix/usage/customer
                #https://developers.google.com/admin-sdk/reports/reference/rest/v1/customerUsageReports/get
                'https://www.googleapis.com/auth/admin.reports.usage.readonly',
                #ref: 
                #https://developers.google.com/admin-sdk/reports/v1/updated-meet-metrics
                #https://developers.google.com/admin-sdk/reports/v1/quickstart/python
                'https://www.googleapis.com/auth/admin.reports.audit.readonly'
            ]
            root = 'https://www.googleapis.com/auth/'
            scopes = (
                "classroom.student-submissions.students.readonly",
                "classroom.profile.emails",
                "classroom.courses",
                "classroom.rosters",
                "classroom.profile.photos"
                 )
            scopes = list((root+e for e in scopes))
            self.SCOPES += scopes
        
        else:
            self.SCOPES = SCOPES
        
        #
        self.verbose = verbose
        
        #get credential file
        self.HOME = os.environ.get('HOME','~')
        
        if fauth is None:
            fauth = 'gclass_credentials.json'

        if os.path.exists(fauth):
            print(f'using fauth from {fauth}')
            self.fauth = fauth
            path = os.path.dirname(fauth)
        else:
            if os.path.exists(f'~/.env/{fauth}'):
                path = '~/.env'
            else:
                path = os.path.join(self.HOME, '.credentials')
            
            self.fauth = os.path.join(path, fauth)            

        self.token_file = os.path.join(path, 'gtoken',token_file)
        #print('token file',self.token_file)
        
        if self.verbose>1:
            print(f'fauth={self.fauth}')
            print(f'token_file={self.token_file}')

        if not os.path.exists(self.fauth):
            self.fauth = '/tmp/gclass_credentials.json'
            auth = get_auth(ssmkey='googleservice/tenxsaas',
                            envvar='GSPREAD_CONFIG',
                            fconfig=self.fauth)
        else:
            auth = json.load(open(self.fauth,'r'))
       
            
        if auth.get("type",'')=="service_account":
            #print(f'****** using service account: {self.fauth}')
            self.creds = self.get_service_account()
            if user_email:
                #print(f'delegating user: {user_email}')
                self.creds = self.creds.with_subject(user_email)
            else:
                print('service account is being used without delegation..')
                
        else:
            self.creds = self.get_token()

    def get_service_account(self):
        return (service_account.Credentials \
                    .from_service_account_file(self.fauth,scopes=self.SCOPES))
        
    def get_token(self):
        """Shows basic usage of the Slides API.
        Prints the number of slides and elments in a sample presentation.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        
        if os.path.exists(self.token_file):
            print(f'reading .. {self.token_file}')
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        else:
            print(f'{self.token_file} does not exist .. generating new token')

        
        # If there are no (valid) credentials available, let the user log in.
        if creds is None  or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print('auth, scope:',self.fauth, self.SCOPES)
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.fauth, self.SCOPES)
                creds = flow.run_local_server(port=0) #,open_browser=False
                
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                print(f'token written to {self.token_file}')
                pickle.dump(creds, token)

        return creds
    
    def get_service(self,name=['drive','sheet','slide','class','admin']):
        
        s = {}            
        if 'sheet' in name: 
            s['sheet'] = build('sheets', 'v4', credentials=self.creds)
            
        if 'drive' in name:        
            s['drive'] =  build('drive',  'v3', credentials=self.creds)
            
        if 'slide' in name:
            s['gslide'] = build('slides', 'v1', credentials=self.creds)
            
        if 'class' in name:
            s['class'] = build('classroom', 'v1', credentials=self.creds)
            
        if 'admin' in name:
            #https://developers.google.com/admin-sdk
            s['admin'] = build('admin', 'reports_v1', credentials=self.creds)
            
        
        return s
    
    def _mime_type(self, ftype):
        mtdict = {"folder":"application/vnd.google-apps.folder",
                    "file":"application/vnd.google-apps.file",
                    "doc":"application/vnd.google-apps.document",
                    "sheet":"application/vnd.google-apps.spreadsheet",
                    "slide":"application/vnd.google-apps.presentation",
                    "form":"application/vnd.google-apps.form",
                    "script":"application/vnd.google-apps.script",
                    "drawing":"application/vnd.google-apps.drawing",
                    "site":"application/vnd.google-apps.site",
                    "map":"application/vnd.google-apps.map",
                    "jam":"application/vnd.google-apps.jam",
                    "photo":"application/vnd.google-apps.photo",
                    "shortcut":"application/vnd.google-apps.shortcut",
                    "site":"application/vnd.google-apps.site",
                    "audio":"application/vnd.google-apps.audio",
                    "video":"application/vnd.google-apps.video",
                    'tsv':'text/tab-separated-values',
                    'jpeg':'image/jpeg',
                    'gif':'image/gif',
                    'dotx':'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
                    'docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'xls':'application/vnd.ms-excel',
                    'sxw':'application/vnd.sun.xml.writer',
                    'txt':'text/plain',
                    'text':'text/plain',
                    'tex':'text/plain',
                    'ods':'application/vnd.oasis.opendocument.spreadsheet',
                    'png':'image/png',
                    'doc':'application/msword',
                    'pdf':'application/pdf',
                    'json':'application/json',
                    'xltx':'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
                    'ppt':'application/vnd.ms-powerpoint',
                    'rtf':'application/rtf',
                    'potx':'application/vnd.openxmlformats-officedocument.presentationml.template',
                    'html':'text/html',
                    'odt':'application/vnd.oasis.opendocument.text',
                    'xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'ppsx':'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
                    'csv':'text/csv',
                    'odp':'application/vnd.oasis.opendocument.presentation',
                    'rtx':'text/richtext',
                    'zip':'application/zip',
                    'svg':'image/svg+xml'}
        
        return mtdict.get(ftype,'text/plain')
  
class gsheet(google_api):
    
    def __init__(self,sheetid, 
                 ftoken = 'token.pickle',
                 fauth = None,
                 sheetname = None):        
        
        
        super().__init__(fauth = fauth, token_file = ftoken)
        #print(ftoken, type(ftoken))
        #
        self.sheetid = sheetid
        self.sheetname = sheetname
        
        s = self.get_service()
        self.drive = s['drive'] 
        self.gsheet = s['sheet'] 
        
        self.sheet = self.gsheet.spreadsheets()
       

    def get_sheet_df(self,name, start='A',
                     end=None, iheader=0, idata=0, lastrow=0,    
                     major='COLUMNS'):  
        
        #get header
        if iheader>0:
            hrange = f'{name}!{start}{iheader}:{end}{iheader}'
            result = self.sheet.values().get(spreadsheetId=self.sheetid, 
                                                    range=hrange).execute()
            if idata==1:
                idata=2            
            self.all_columns = result.get('values', [])[0]
        else:
            iheader=0
            nrows = lastrow-idata+1
            self.all_columns=['']*nrows
            
        
        
        #get data
        if lastrow==0:
            drange = f'{name}'
            if idata>0:
                drange += f'!{start}{idata}'
                
            if end is not None:
                drange += f':{end}'              
                
        else:
            drange = f'{name}!{start}{idata}:{end}{lastrow}'

        result = self.sheet.values().get(spreadsheetId=self.sheetid, 
                                         range=drange,
                                         majorDimension=major).execute()
         
        values = result['values']

        if lastrow==0:
            df = pd.DataFrame(values).transpose()
            col = df.iloc[0].values
            df = df.drop([0])
            df.columns = col
        else:
            nrows = lastrow-idata+1
            data = {col:['']*nrows for col in self.key_columns}
            for col in self.key_columns:
                if col in self.all_columns:
                    ic = self.all_columns.index(col)
                    v = values[ic]
                    nv = len(v)
                    data[col][0:nv] = v
                        
            df = pd.DataFrame.from_dict(data)
        

        #df = df[:,self.key_columns].dropna(axis='columns', thresh=0.95) 
        
        return df

    def create_sheet(self,title):

        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        spreadsheet = self.sheet.create(body=spreadsheet,
                                        fields='spreadsheetId').execute()

        sheetid = spreadsheet.get('spreadsheetId')
        print('Spreadsheet ID: {0}'.format(sheetid))
        #
        return sheetid

        
    def df_to_sheet(self,df,name):

        response = self.sheet.values().update(
            spreadsheetId=self.sheetid,
            valueInputOption='RAW',
            range=f'{name}!A1',
            body=dict(
                majorDimension='ROWS',
                values=df.T.reset_index().T.values.tolist())
        ).execute()
        
        return response


    
    def write_df(self,df,name):
        
        values = [df.columns.values.tolist()]
        values.extend(df.T.reset_index().T.values.tolist())  
        
        data = [{'range' : name, 'values' : df}]
        body = {
            'value_input_option': 'RAW',
            'data': values }

        response = (self.sheet.values()
                    .batchUpdate(spreadsheetId=self.sheetid, body=body)
                    .execute()
                   )
        return response
    
    def sheet_update(self,body, major='COLUMNS'): 
        '''
        if you want to update multiple ranges 
        Refer: https://developers.google.com/sheets/api/guides/values
        '''
        
        result = self.sheet.values().batchUpdate(spreadsheetId=self.sheetid, 
                                                 body=body).execute()

        print('{0} cells updated.'.format(result.get('totalUpdatedCells')))        
        
        return result

    def single_update(self,name, row_list, loc='A1', major='COLUMNS'):  
        '''
        if you want to update a single row 
        Refer: https://developers.google.com/sheets/api/guides/values
        
        row_list must be a list of lists: e,g [[cell_1],[cell_2],..]
        '''        

        try:
            if not isinstance(row_list[0],list):
                values = [[x] for x in row_list]
            else:
                values = row_list
        except:
            print('row_list must be a list of lists: e,g [[cell_1],[cell_2],..]')
            return
            
        body = {'values': values}
        
        #get data
        #Ref: https://developers.google.com/sheets/api/guides/values
        value_input_option = 'RAW'
        #drange = f'{name}!{start}{istart}:{end}{iend}'
        drange = f'{name}!{loc}'
        result = self.sheet.values().update(spreadsheetId=self.sheetid, 
                                            range=drange,
                                            valueInputOption=value_input_option,
                                            body=body).execute()

        print('{0} cells updated.'.format(result.get('updatedCells')))        
        
        return result  

def get_prefix(folder, year="", month="", day="", hour="", 
               datefirst=False, dsep='/', hsep=' '):      
    
    if not datefirst and folder:
        PREFIX = folder
    else:
        PREFIX = ""
    
    for i, x in enumerate([year, month, day, hour]):
        if i==0:
            sep = '/'
        elif i==3:
            sep = hsep
        else:
            sep = dsep
        if x:
            if PREFIX:
                PREFIX = PREFIX + sep + str(x)
            else:
                PREFIX += str(x)
        else:
            break               
            
    if datefirst and folder:
        return PREFIX + '/' + folder
    else:
        return PREFIX  
    
class gdrive(google_api):
    '''
    Leap on Shared Drive: "1XYdbpf3lGJDd0bdiZr8BrMdVMe7EQpt_",
    Leap on My Drive: "0AAtElePllsNuUk9PVA"
    CB on Shared Drive: "1Pwsjx7OJVGxXr8z6E2ghQZKjPJ_yVyRV" 
    '''
    def __init__(self, 
                 drive_id="",
                 collection_id="",
                 ftoken='token.pickle',
                 fauth=None,
                 **kwargs):        
        
        
        super().__init__(fauth = fauth, token_file = ftoken, **kwargs)

        if not drive_id:
            logger.warn('Gdrive: Parent folder id is not provided. Using root drive id..')
            drive_id = 'root'
        else:
            logger.info(f'Gdrive: Parent folder id is provided: {drive_id}')
        
        
        s = self.get_service()
        self.drive = s['drive']
                
        self.drive_id = drive_id
        self.drive_link = "https://drive.google.com/drive/folders/{drive_id}"
        
        if collection_id:
            self.collection_id = collection_id            
        else:
            self.collection_id = self.drive_id
            
        self.common_filter = "trashed = false"    
            
        #logger.info(f'Using Common Query Filter: {self.common_filter}')
     
      
    def generate_upload_filename(self, remote_file_name, 
                                root_folder="", 
                                dtprefix=False, 
                                datefirst=False, 
                                dt=None,
                                **kwargs):
        rootdir = root_folder.strip()
        if dtprefix and dt is not None:
            if isinstance(dt, datetime):            
                year = dt.year
                month = dt.month
                day = dt.day
                rootdir = get_prefix(rootdir, year=str(year), 
                                            month=str(month), 
                                            day=str(day), 
                                            datefirst=datefirst)
            
        if rootdir.strip():
            file_name = os.path.join(rootdir.strip(), remote_file_name)
        else:
            file_name = remote_file_name
            
        return file_name
        
    def process_remote_path(self, remote_path, root_folder="", **kwargs):
        # generate file name            
        remote_file_name = self.generate_upload_filename(remote_path,
                                                root_folder=root_folder,
                                                dtprefix=kwargs.get('dtprefix',False), 
                                                datefirst=kwargs.get('datefirst',False),
                                                dt=kwargs.get('dt', None)
        )
                                
                                
        # get folder name and file name             
        folder_name = os.path.dirname(remote_file_name)
        file_name = os.path.basename(remote_file_name)
        ext = os.path.splitext(file_name)[1].replace(".", "")
        mimetype = self._mime_type(ext)

        return folder_name, file_name, ext, mimetype
                    
    def process_output(self,filesIn,**kwargs):
        
        files = copy.deepcopy(filesIn)
        
        rkey = kwargs.get('rkey','')
        
        if not files:
            return ""
        
        
        if rkey:
            if rkey=='link':
                rkey = 'webViewLink'
                
            if isinstance(files, dict):
                res = files.get(rkey, "")
            elif isinstance(files, list):
                res = [f.get(rkey, "") for f in files]
            else:
                res = files
        else:
            res = files
                        
        if res:
            if isinstance(res, list) and kwargs.get('single',False):
                res = res[0]
            
        return res
        
    def folder_exists_and_not_empty(self, folder_name, **kwargs):
        """Check if folder exists and not empty
        Returns: True if folder exists and not empty
        """
        isempty = False
        logger.info(f'Checking if folder {folder_name} exists and not empty ..')
        parent_id, parent_link = self.folder_exists(folder_name, **kwargs)
        if parent_id:
            files = self.search_file(f"'{parent_id}' in parents", isquery=True, **kwargs)
            if files:
                logger.good(f'Folder {folder_name} exists and not empty')
                isempty = True
            else:
                logger.info(f'Folder {folder_name} exists but empty', fg='yellow')
                isempty = False
        else:
            logger.info(f'Folder {folder_name} does not exist', fg='yellow')
            isempty = False
            
        return isempty, parent_id, parent_link

        
    def folder_exists_old(self, remote_path, parent_id=None, **kwargs):
        """Create a folder and prints the folder ID
        Returns : Folder Id
        """
        
        #
        folder_id = ""
        folder_link = ""
 
        #
        output = []
        exists = False
        sub_folders = remote_path.split("/")
        
        # create folder          
        try:                                    
            for i, name in enumerate(sub_folders):
                logger.info(f'Checking if folder with name: `{name}` of {remote_path} exists ..')
                if name:
                    files = self.search_file(name, isfolder=True, parent_id=parent_id)  
                    if files:                                                
                        folder_id = files[0].get("id")
                        folder_link = files[0].get("webViewLink")
                        output.append({'name':name, 'folder_id':folder_id, 'folder_link':folder_link})
                        
                        logger.good(f'Folder with name: {name} of {remote_path} exists! folder_id={files[0].get("id")}')
                        exists = True
                        parent_id = folder_id
                    else:
                        logger.info(f'Folder with name: {name} of {remote_path} does not exist!')
                        exists = False
                        break
                                                                                    
        except HttpError as error:            
            logger.error(f"Error occured during folder_exists operation:")
            logger.error(f'subfolders: {sub_folders}')
            logger.error(f'Error: {error}')
            
        if exists and output:
            folder_id = output[-1].get('folder_id')
            name = output[-1].get('name')
            folder_link = output[-1].get('folder_link') 
        else:
            folder_id = ""
            folder_link = ""              
            
        return folder_id, folder_link
          
        
     
    def folder_exists(self, remote_path, parent_id=None, **kwargs):
        """Create a folder and prints the folder ID
        Returns : Folder Id
        """
        
        #
        folder_id = ""
        folder_link = ""
 
        #
        output = []
        exists = False
        
        # create folder          
        try:    
            logger.info(f'Checking if folder with name: `{remote_path}`exists ..')
            files = self.search_file(remote_path, isfolder=True, parent_id=parent_id)  
            if files:                                                
                folder_id = files[0].get("id")
                folder_link = files[0].get("webViewLink")
                output = {'name':remote_path, 'folder_id':folder_id, 'folder_link':folder_link}
                
                logger.good(f'Folder with remote_path: {remote_path} of {remote_path} exists! folder_id={files[0].get("id")}')
                exists = True
                parent_id = folder_id
            else:
                logger.info(f'Folder with remote_path: {remote_path} of {remote_path} does not exist!')
                exists = False                                                                             
        except HttpError as error:            
            logger.error(f"Error occured during folder_exists operation:")
            logger.error(f'remote_path: {remote_path}')
            logger.error(f'Error: {error}')
            
        if not (exists and output):
            folder_id = ""
            folder_link = ""              
            
        return folder_id, folder_link
          
                  
    def file_exists(self, file_name, folder_name="", parent_id="", **kwargs):
        """Check if file exists
        Returns: True if file exists
        """
        file_id = ""
        file_link = ""
                    
        
        if folder_name:
            if not folder_name in file_name:
                file_name = os.path.join(folder_name, file_name)
        #  
        if not parent_id:
            logger.info(f'Checking if file={file_name} exists ..')      
            folder_name, file_name, ext, mimetype = self.process_remote_path(file_name, **kwargs)        
                    
            if folder_name:
                parent_id, parent_link = self.folder_exists(folder_name, **kwargs)
                if parent_id:
                    logger.good(f'Parent folder={folder_name} exists with id={parent_id}!')
            
        if not parent_id:
            logger.warn(f'Parent folder={folder_name} does not exist!')
        else:
            logger.info(f'Checking if file exists ..')     
            files = self.search_file(file_name, parent_id=parent_id)
            if files:
                file_id = self.process_output(files, single=True, rkey='id')
                file_link = self.process_output(files, single=True, rkey='webViewLink')                    
                logger.good(f'File {file_name} exists with id={file_id}!')
            else:
                logger.info(f'File {file_name} does not exist')

            
        return file_id, file_link
                          
                                  
    def get_metadata(self, file_id):
        """Get metadata of a file
        Returns: File metadata
        """
        # create drive api client
        service = self.drive
        file = {}
        try:
            # pylint: disable=maybe-no-member
            file = (service.files()
                    .get(fileId=file_id,
                         fields='files(id, name, webViewLink, mimeType, modifiedTime, createdTime, size, parents)')
                    .execute()
            )            

        except HttpError as error:
                logger.error(f"Error occured during get_metadata operation:")
                logger.error(f'file_id: {file_id}')
                logger.error(f'Error: {error}') 
                
        return self.process_output(file)
        
    def search_file(self, query, 
                    isquery=False, 
                    isfolder=False, 
                    page_size=10, 
                    parent_id="", 
                    **kwargs):
        """Search file in drive location
        Returns: List of files

        https://developers.google.com/drive/api/guides/search-files
        """
        service = self.drive

        files = []
        
        sfl_kwargs = {}
        
        # prepare query
        suffix = ""
        if isfolder and not isquery:
            suffix = "and mimeType = 'application/vnd.google-apps.folder'"
        
        # add ad hoc filter
        if isquery:       
            query = query + f" {suffix}"               
        else:
            query = f"name contains '{query}' {suffix}" 
             
        # add parent_id
        if parent_id:
            query += f" and '{parent_id}' in parents"
        else:
            if 'in parents' not in query:
                query += f" and '{self.collection_id}' in parents"
           
        # add common filter
        if self.common_filter and self.common_filter not in query:
            query += f" and {self.common_filter}"
            
        logger.info(f'Using Search Query: {query}', fg='pink')
                        
        #prepare kwargs
        sfl_kwargs.update(dict(spaces="drive",
                        corpora='drive',                        
                        driveId=self.drive_id,
                        includeItemsFromAllDrives=True,
                        supportsAllDrives=True,                          
                        orderBy='modifiedTime asc',
                        pageSize=page_size,                      
                        fields="nextPageToken, files(id, name, webViewLink, mimeType, modifiedTime, createdTime, size, parents)"
                        ) )
              
        # search for files             
        try:
            #                 
            page_token = None
            while True:      
                
                sfl_kwargs["pageToken"] = page_token
                      
                response = (
                    service.files()
                    .list(
                        q=query,                       
                        **sfl_kwargs
                    )
                    .execute()
                )                
                files.extend(response.get("files", []))
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    break
                                
        except HttpError as error:
            logger.error(f"Error occured during search:")
            logger.error(f'query: {query}')
            logger.error(f'sfl_kwargs: {sfl_kwargs}')
            logger.error(f'Error: {error}')
            
        return files
        
               
      
    def upload_file(self, local_file_name, folder_id=None, 
                    remote_path="", root_folder="", 
                    **kwargs):
        return self.upload_to_folder(local_file_name, 
                                     folder_id=folder_id, 
                                     remote_path=remote_path,
                                     root_folder=root_folder, 
                                     **kwargs)


    def upload_to_folder(self, local_file_name, 
                         remote_path="", 
                         folder_id=None, 
                         root_folder="", 
                         folder_ids={},
                         **kwargs):
        """Upload a file to the specified folder and prints file ID, folder ID
        Args: Id of the folder
        Returns: ID of the file uploaded
        """
        # create drive api client 
        service = self.drive
        file_id = ""
        file_link = ""
        folder_id = ""     
        
        if os.path.exists(local_file_name):
            
            if not remote_path:
                remote_path = os.path.basename(local_file_name)
                
            folder_name, file_name, ext, mimetype = self.process_remote_path(remote_path, 
                                                                            root_folder=root_folder, 
                                                                            **kwargs)
            if not folder_id:
                r = folder_ids.get(folder_name, None)
                if r:
                    folder_id = r.get('id')
                    folder_link = r.get('link')
            
            if folder_id:
                logger.good(f'Folder with folder_name={folder_name} exists with folder_id={folder_id}')
            else:
                if folder_name:
                    try:
                        # check if folder exists
                        folder_id, folder_link = self.folder_exists(folder_name)
                    except:
                        logger.warn(f'Failed to check if folder exists with folder_name={folder_name}!')
                        
                    if not folder_id:
                        logger.info(f'Folder with folder_name={folder_name} does not exist. Creating folder..')
                        try:
                            # create folder                
                            folder_id, folder_link = self.create_folder(folder_name, folder_ids=folder_ids)
                        except:
                            logger.warn(f'Failed to create folder with folder_name={folder_name}!')
                            
            
            file_metadata = {"name": file_name}
            if not folder_id: 
                folder_id = self.collection_id
            
            file_metadata["parents"] = [folder_id]
                
            file_id, file_link = self.file_exists(remote_path, parent_id=folder_id)

            #logger.debug(f'file_metadata: {file_metadata}, ext={ext}, mimetype: {mimetype}')
        
            try:
                # upload file
                media = MediaFileUpload(
                    local_file_name, mimetype=mimetype, resumable=True
                )
                # pylint: disable=maybe-no-member
                if not file_id:
                    logger.info(f'Uploading new file to google drive with file_name={file_name}..')
                    file = (
                        service.files()
                        .create(body=file_metadata, 
                                media_body=media, 
                                supportsAllDrives=True, 
                                fields="id, webViewLink")
                        .execute()
                    )
                else:
                    logger.info(f'Updating file_name={file_name} with file_id={file_id} in google drive..')
                    file = (
                        service.files()
                        .update(fileId=file_id, 
                                body=file_metadata, 
                                media_body=media, 
                                supportsAllDrives=True, 
                                fields="id, webViewLink")
                        .execute()
                    )
                    
                file_id = file.get("id")
                file_link = file.get("webViewLink")
                
            except HttpError as error:
                logger.error(f"Error occured during `upload_to_folder' operation:")
                logger.error(f'file_metadata: {file_metadata}, ext={ext}, mimetype: {mimetype}')
                logger.error(f'Error: {error}')  
                
            # if file_id:
            #     try:
            #         _ = self.share_with_everyone(file_id)
            #         logger.good(f'file_name={file_name} is uploaded with file_id={file_id} and shared to public!')
            #     except Exception as e:
            #         print(e)
            #         logger.warn(f'Upload-to-folder: Failed to share file with everyone for file_name={file_name}!')
        else:            
            logger.error(f'Local file does not exist: {local_file_name}')

        if kwargs.get('return_folder_link', False):
            return file_id, file_link, folder_id, folder_link
        else:
            return file_id, file_link
        

    def move_file_to_folder(self, file_id, folder_id):
        """Move specified file to the specified folder.
        Args:
            file_id: Id of the file to move.
            folder_id: Id of the folder
        Print: An object containing the new parent folder and other meta data
        Returns : Parent Ids for the file
        """
        # create drive api client
        service = self.drive

        try:
            # pylint: disable=maybe-no-member
            # Retrieve the existing parents to remove
            file = service.files().get(fileId=file_id, fields="parents").execute()
            previous_parents = ",".join(file.get("parents"))
            # Move the file to the new folder
            file = (
                service.files()
                .update(
                    fileId=file_id,
                    addParents=folder_id,
                    removeParents=previous_parents,
                    fields="id, parents",
                )
                .execute()
            )
            return file.get("parents")

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None      
        
    def share_file(self, real_file_id, share_list=[]):
        """Batch permission modification.
        Args:
            real_file_id: file Id
            real_user: User ID
            real_domain: Domain of the user ID
        Prints modified permissions
        
        Example 
        share_list = [ {
                "type": "user",  
                "role": "writer",
                "emailAddress": "user@example.com",
            },
            {
                "type": "domain",
                "role": "reader",
                "domain": "example.com",
            } 
            ]
        """
        # create drive api client
        service = self.drive

        try:
            ids = []
            file_id = real_file_id
            
            if len(share_list)==0:
                logger.info(f'Generating public link: anyone with the link can access')
                share_list = [{"role":"reader", "type":"anyone"}]

            def callback(request_id, response, exception):
                if exception:
                    # Handle error
                    logger.error(f"Error: {exception}")
                else:
                    ids.append(response.get("id"))

            # pylint: disable=maybe-no-member
            batch = service.new_batch_http_request(callback=callback)
            for body in share_list:
                batch.add(
                    service.permissions().create(
                        fileId=file_id,
                        body=body,
                        supportsAllDrives=True                        
                    )
                )
            #
            batch.execute()

        except HttpError as error:
            print(f"An error occurred: {error}")
            ids = None

        return ids   
    
    def share_with_everyone(self, object_id):
        # create drive api client
        service = self.drive
                
        logger.info(f'Sharing folder with everyone for id={object_id}..')
        payload = {
            "role": "reader",
            "type": "anyone"
        }
        # spaces="drive",
        # corpora='drive',                        
        # driveId=self.drive_id,
        # includeItemsFromAllDrives=True,
                                
        kwargs = dict(
                        )
        res = (service.permissions()
               .create(fileId=object_id, 
                       body=payload, 
                       supportsAllDrives=True)
               .execute()     
        )
        
        return res.get('id')
                
    def create_folder(self, folder_name, 
                      folder_ids={},
                      parent_id=None):
        """Create a folder and prints the folder ID
        Expects:
            folder_name
            folder_ids: dictionary of folder names and object e.g. {folder_name:{id:, link:}}
        Returns : Folder Id

        Load pre-authorized user credentials from the environment.
        TODO(developer) - See https://developers.google.com/identity
        for guides on implementing OAuth2 for the application.
        """
        # create drive api client 
        service = self.drive
        
        #
        folder_id = ""
        folder_link = ""

        # 
        if not parent_id:
            parent_id = self.collection_id
              
             
        # prepare folder metadata         
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }        
        if parent_id:
            file_metadata["parents"] = [parent_id] 

         
        # create folder          
        try:     
            # name = folder_name
            # # pylint: disable=maybe-no-member
            # file_metadata["name"] = name
            # logger.info(f'Creating gdrive folder: file_metadata: {file_metadata}')
            
            # file = service.files().create(body=file_metadata,  
            #                             supportsAllDrives=True,                                         
            #                             fields="id, webViewLink").execute()
            # folder_id = file.get("id")
            # folder_link = file.get("webViewLink")
            # output.append({'name':name, 'folder_id':folder_id, 'folder_link':folder_id})
                                
            # file_metadata["parents"] = [folder_id] 
                               
                               
            # 1. check if folders and sub-folders exist
            path_items = folder_name.split("/")
            for name in path_items:
                file = folder_ids.get(name, None)
                if not file:
                    folder_id, folder_link = self.folder_exists(name, parent_id=parent_id)
                    if folder_id:
                        folder_ids[name] = {'folder_id':folder_id, 'folder_link':folder_link}
                        parent_id = folder_id
            
            
            # 2. create folders and sub-folders that does not exist
            output = {}
            for i, name in enumerate(path_items):
                logger.info(f'Creating folder with name: {name} of {folder_name} ..')
                if name:
                    # pylint: disable=maybe-no-member
                    file_metadata["name"] = name
                    
                    file = folder_ids.get(name, None)
                    if not file:                                                
                        logger.info(f'Creating gdrive folder: file_metadata: {file_metadata}')
                        file = service.files().create(body=file_metadata,  
                                                    supportsAllDrives=True,                                         
                                                    fields="id, webViewLink").execute()
                        folder_ids[name] = file
                    folder_id = file.get("id")
                    folder_link = file.get("webViewLink")
                    output = {'name':name, 'folder_id':folder_id, 'folder_link':folder_id}
                                        
                    file_metadata["parents"] = [folder_id]                        
        except HttpError as error:            
            logger.error(f"Error occured during create folder operation:")
            logger.error(f'metadata: {file_metadata}')
            logger.error(f'Error: {error}')
            
        if output:
            folder_id = output.get('folder_id')
            name = output.get('name')
            folder_link = output.get('folder_link')
            try:                    
                logger.info(f'Change permission of folder_name={name} with folder_id={folder_id}..')
                try:
                    _ = self.share_with_everyone(folder_id)
                except:
                    logger.warn(f'Failed to share folder with everyone for folder_name={name}!')
                    
                logger.info(f'Folder link for folder_name={name}: {folder_link}') 
            except HttpError as error:            
                logger.error(f"Error occured during share folder operation:")
                logger.error(f'folder_id: {folder_id}')
                logger.error(f'Error: {error}')                    
            
        return folder_id, folder_link                
    
    def delete_object(self, file_id):
        """Delete a file or folder
        Args: Id of the file or folder
        Returns: None
        """
        # create drive api client
        service = self.drive

        try:
            # pylint: disable=maybe-no-member
            service.files().delete(fileId=file_id).execute()
            logger.info(f'File with id={file_id} is deleted!')
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            
    def download_file(self, file_id, local_file_name):
        """Download a file
        Args: Id of the file to download
        Returns: None
        """
        # create drive api client
        service = self.drive

        try:
            # pylint: disable=maybe-no-member
            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(local_file_name, "wb")
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))
        except HttpError as error:
            print(f"An error occurred: {error}")
            
    def download_file_by_name(self, file_name, local_file_name):
        """Download a file by name
        Args: Name of the file to download
        Returns: None
        """
        # create drive api client
        service = self.drive

        try:
            # pylint: disable=maybe-no-member
            files = (
                service.files()
                .list(q=f"name='{file_name}'", fields="files(id)")
                .execute()
            )
            file_id = files.get("files", [])[0].get("id")
            self.download_file(file_id, local_file_name)
        except HttpError as error:
            print(f"An error occurred: {error}")
            
    def trash_object(self, file_id):
        """Trash a file
        Args: Id of the file to trash
        Returns: None
        """
        # create drive api client
        service = self.drive

        try:
            # pylint: disable=maybe-no-member
            service.files().update(fileId=file_id, body={"trashed": True}).execute()
        except HttpError as error:
            print(f"An error occurred: {error}")
            
    def untrash_object(self, file_id):
        """Untrash a file
        Args: Id of the file to untrash
        Returns: None
        """
        # create drive api client
        service = self.drive

        try:
            # pylint: disable=maybe-no-member
            service.files().update(fileId=file_id, body={"trashed": False}).execute()
        except HttpError as error:
            print(f"An error occurred: {error}")
            
    def empty_trash(self):
        """Empty trash
        Returns: None
        """
        # create drive api client
        service = self.drive

        try:
            # pylint: disable=maybe-no-member
            service.files().emptyTrash().execute()
        except HttpError as error:
            print(f"An error occurred: {error}")
            
    def delete_folder_contents(self, folder_id):
        """Delete all files in a folder
        Args: Id of the folder
        Returns: None
        """
        # create drive api client
        service = self.drive

        try:
            # pylint: disable=maybe-no-member
            files = (
                service.files()
                .list(q=f"'{folder_id}' in parents", fields="files(id)")
                .execute()
            )
            for file in files.get("files", []):
                self.delete_object(file.get("id"))
        except HttpError as error:
            print(f"An error occurred: {error}")
            
    def delete_folder(self, folder_id):
        return self.delete_object(folder_id)
    
    def delete_file(self, file_id):
        return self.delete_object(file_id)    
            
    def delete_folder_if_exists(self, file_name, **kwargs):
        """Delete a file if it exists
        Args: Name of the file to delete
        Returns: None
        """
        # create drive api client
        service = self.drive

        try:
            # pylint: disable=maybe-no-member
            folder_id, folder_link = self.folder_exists(file_name)
            if folder_id:
                self.delete_object(folder_id)
        except HttpError as error:
            print(f"An error occurred: {error}")
            


def GetFolderTree(drive_id, **kwargs):
    return getfilelist(folder_id, **kwargs).getFolderTree()


def GetFileList(folder_id, **kwargs):
    return getfilelist(folder_id, **kwargs).getFileList()

   
def DownloadFile(file_id, file = io.BytesIO(), **kwargs):
    """Downloads a file
    Args:
        real_file_id: ID of the file to download
    Returns : IO object with location.
    """
    
    self = google_api(**kwargs)
    service = self.get_service()['drive']
    
    try:
        # pylint: disable=maybe-no-member
        request = service.files().get_media(fileId=file_id)        
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")
        
    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None
    finally:
        service.close()

    return file.getvalue() 
    
        
def client_wrapper(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        close=False
        if args[0].service is None:              
            args[0].service = args[0].get_service()['drive']
            close=True 
            
        res = func(*args, **kwargs)
        
        if close:
            try:
                args[0].service.close()
                args[0].service = None
            except:
                pass
                        
        return res
            
    return wrapper
        
class getfilelist(google_api):
                
    """
    This is a python library to retrieve the file list with the folder tree
    from the specific folder of Google Drive.

    - This library retrieves all files from a folder in own Google Drive and shared Drives.
    - All files include the folder structure in Google Drive.
    - Only folder tree can be also retrieved.

    usage:
    resource = {
        "api_key": api_key,
        # "oauth2": auth,
        # "service_account": credentials,
        "id": "#####",
        "fields": "files(id,name)",
    }

    res = getfilelist.GetFileList(resource)

    res = getfilelist.GetFolderTree(resource)

    __author__ = "Kanshi TANAIKE (tanaike@hotmail.com)"
    __copyright__ = "Copyright 2018, Kanshi TANAIKE"
    __license__ = "MIT"
    __version__ = "1.0.5"
    """  

    def __init__(self, 
                 folder_id,
                 ftoken='token.pickle',
                 fields="files(id,name)",
                 fauth=None,
                 **kwargs):        
        
        
        super().__init__(fauth = fauth, token_file = ftoken, **kwargs)


        resource = { 
                    'id': folder_id,
                    "fields": fields
                    }
        self.id = resource["id"] if "id" in resource.keys() else None
        self.fields = resource["fields"] if "fields" in resource.keys(
        ) else None
        
        self.service = None
        
        #
        self.e = {}
        self.e["chkAuth"] = self.__checkauth(resource)
        self.__init()

    def __checkauth(self, resource):
        if hasattr(self, "service"):
            return True
        return False
    
    @client_wrapper
    def __getList(self, ptoken, q, fields):
        if "driveId" in self.e["searchedFolder"]:
            driveId = self.e["searchedFolder"].get("driveId")
            return self.service.files().list(q=q, fields=fields, orderBy="name", 
                                             pageSize=1000, pageToken=ptoken or "", 
                                             includeItemsFromAllDrives=True, 
                                             supportsAllDrives=True, corpora="drive", 
                                             driveId=driveId).execute()
        else:
            return self.service.files().list(q=q, fields=fields, orderBy="name", 
                                             pageSize=1000, pageToken=ptoken or "", 
                                             includeItemsFromAllDrives=True, 
                                             supportsAllDrives=True).execute()

    def __getListLoop(self, q, fields, values):
        nextPageToken = ""
        while True:
            res = self.__getList(nextPageToken, q, fields)
            values.extend(res.get("files"))
            nextPageToken = res.get("nextPageToken")
            if nextPageToken is None:
                break
        return values

    def __getFilesFromFolder(self, folderTree):
        f = cl.OrderedDict()
        f["searchedFolder"] = self.e["searchedFolder"]
        f["folderTree"] = folderTree
        f["fileList"] = []
        if self.fields is None:
            self.fields = "files(createdTime,description,id,mimeType,modifiedTime,name,owners,parents,permissions,shared,size,webContentLink,webViewLink),nextPageToken"
        elif self.fields.find("nextPageToken") == -1:
            self.fields += ",nextPageToken"
        for i, e in enumerate(folderTree["folders"]):
            q = "'%s' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed=false" % e
            fm = self.__getListLoop(q, self.fields, [])
            fe = {"files": []}
            fe["folderTree"] = folderTree["id"][i]
            fe["files"].extend(fm)
            f["fileList"].append(fe)
        f["totalNumberOfFolders"] = len(f["folderTree"]["folders"])
        f["totalNumberOfFiles"] = sum(len(e["files"]) for e in f["fileList"])
        return f

    def __getDlFoldersS(self, searchFolderName, fr):
        fT = cl.OrderedDict()
        fT["id"] = []
        fT["names"] = []
        fT["folders"] = []
        fT["id"].append([fr["search"]])
        fT["names"].append(searchFolderName)
        fT["folders"].append(fr["search"])
        for e in fr["temp"]:
            for f in e:
                fT["folders"].append(f["id"])
                tmp = []
                tmp.extend(f["tree"])
                tmp.append(f["id"])
                fT["id"].append(tmp)
                fT["names"].append(f["name"])
        return fT

    def __getAllfoldersRecursively(self, idd, parents, folders):
        q = "'%s' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false" % idd
        fields = "files(id,mimeType,name,parents,size),nextPageToken"
        files = self.__getListLoop(q, fields, [])
        temp = []
        p = list(parents)
        p.append(idd)
        for e in files:
            obj = {"name": e.get("name"), "id": e.get(
                "id"), "parent": e.get("parents")[0], "tree": p}
            temp.append(obj)
        if len(temp) > 0:
            folders["temp"].append(temp)
            for e in temp:
                self.__getAllfoldersRecursively(
                    e.get("id"), e.get("tree"), folders)
        return folders

    def __getFolderTreeRecursively(self):
        folderTr = {"search": self.e["searchedFolder"]["id"], "temp": []}
        value = self.__getAllfoldersRecursively(
            self.e["searchedFolder"]["id"], [], folderTr)
        return self.__getDlFoldersS(self.e["searchedFolder"].get("name"), value)

    def __createFolderTreeID(self, fm, idd, parents, fls):
        temp = []
        p = list(parents)
        p.append(idd)
        for e in fm:
            if ("parents" in e) and (len(e["parents"]) > 0) and (e["parents"][0] == idd):
                t = {"name": e["name"], "id": e["id"],
                     "parent": e["parents"][0], "tree": p}
                temp.append(t)
        if len(temp) > 0:
            fls["temp"].append(temp)
            for e in temp:
                self.__createFolderTreeID(fm, e["id"], e["tree"], fls)
        return fls

    def __getFromAllFolders(self):
        q = "mimeType='application/vnd.google-apps.folder' and trashed=false"
        fields = "files(id,mimeType,name,parents,size),nextPageToken"
        files = self.__getListLoop(q, fields, [])
        tr = {"search": self.e["searchedFolder"]["id"], "temp": []}
        value = self.__createFolderTreeID(
            files, self.e["searchedFolder"]["id"], [], tr)
        return self.__getDlFoldersS(self.e["searchedFolder"]["name"], value)

    @client_wrapper
    def __getFileInf(self):
        fields = "createdTime,id,mimeType,modifiedTime,name,owners,parents,shared,webContentLink,webViewLink,driveId"
        return self.service.files().get(fileId=self.id, fields=fields, supportsAllDrives=True).execute()

    def __init(self):
        self.e["rootId"] = self.id is None or self.id.lower() == "root"
        if not self.e["chkAuth"] and self.e["rootId"]:
            try:
                raise ValueError(
                    "Error: All folders in Google Drive cannot be retrieved using API key. Please use OAuth2.")
            except ValueError as err:
                print(err)
                sys.exit(1)
        self.id = "root" if self.e["rootId"] else self.id
        try:
            self.e["searchedFolder"] = self.__getFileInf()
        except googleapiclient.errors.HttpError:
            print("Error: Folder ID of '%s' cannot be retrieved. Please confirm whether the folder ID is existing, or the owner of file is that of account. If you want to retrieve other user's folder, please check whether the folder is shared." % self.id)
            sys.exit(1)
        self.e["method"] = (self.e["chkAuth"] or self.e["rootId"]
                            ) and not self.e["searchedFolder"].get("shared")
        return

    def getFileList(self):
        """This is a method for retrieving file list."""
        folderTree = self.__getFromAllFolders(
        ) if self.e["method"] else self.__getFolderTreeRecursively()
        return self.__getFilesFromFolder(folderTree)

    def getFolderTree(self):
        """This is a method for retrieving folder tree."""
        return self.__getFromAllFolders() if self.e["method"] else self.__getFolderTreeRecursively()            