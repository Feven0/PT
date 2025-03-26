import os, sys
import re
import json
import copy

from .pathfig import *

from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))

class BaseTable():
    def __init__(self, **kwargs):
        self.table = self.init_structure(**kwargs)
        
    def create_filter_options(self, data):
        options = []
        if isinstance(data, dict):
            for key, value in data.items():
                options.append({
                    "name": key,
                    "value": value
                })
        elif isinstance(data, list):            
            for item in data:
                if isinstance(item, dict):
                    options.append({
                        "name": item.get("name", ""),
                        "value": item.get("value", "")
                    })
                elif isinstance(item, str):
                    options.append({
                        "name": item,
                        "value": item
                    })
                else:
                    logger.warn("Invalid data type for filter options: expects list of dict or string")
                    continue
        else:
            logger.warn("Invalid data type for filter options: expects list or dict")
            
        return options
    
    def column_type(self, dtype, format="", source=""):
        '''
        "type":{
            "dtype": "string, date, datetime, tag, link, tag_list, html",
            "format": "date format if type is date; etc.",
            "source": "alias to another column name if view data is different from search data"				                   
        }        
        '''      
        if dtype.lower() not in ['string', 'number', 'date', 'datetime', 'tag', 
                                 'link', 'tag_list', 'html', 'api', 
                                 'expand']:
            logger.warn(f"Invalid column type: {dtype.lower()}")
            dtype = 'string'
        if dtype.lower().startswith('date') and not format:
            logger.warn("Date type requires format. Using default format: 'YYYY-MM-DD'")
            format = 'YYYY-MM-DD'
        if dtype.lower() == 'html' and not source:
            logger.warn("Defining HTML type without source")
        
        return {
            "dtype": dtype.lower(),
            "format": format,
            "source": source
        }
        
    def create_icon(self, iformat, source="", itype="icon_only"):
        '''
        "icon":{
            "type": "with_text,icon_only",
            "source":"If the icon is an avatar will take the source from the data provided ",
            "icon": "first-letter, download, link, avatar,expand"
        }
        '''       
        if not iformat:
            return {}
        if iformat=='avatar' and not source:
            logger.warn("Avatar icon requires source")
            return {}
        
        if iformat not in ['first-letter', 'download', 'link', 'avatar', 'expand']:
            logger.warn("Invalid icon format")
            return {}
        if itype not in ['with_text', 'icon_only']:
            logger.warn("Invalid icon type: using itype='icon_only'")
            itype='icon_only'
            
        return {
            "type": itype,
            "source": source,
            "icon": iformat
        }
    
    def create_first_letter_icon(self):
        return self.create_icon('first-letter', itype='with_text')
    
    def create_download_icon(self):
        return self.create_icon('download')
    
    def create_link_icon(self):
        return self.create_icon('link')
    
    def create_avatar_icon(self, source):
        return self.create_icon('avatar', source)
    
    def create_expand_icon(self, source):
        return self.create_icon('expand', source)    
    
    def visible(self, mobile=False, tablet=False, desktop=False):
        return {"mobile":mobile, "tablet":tablet, "desktop":desktop}    
        
    def add_column(self, name, label="", sorting=False, icon={}, 
                   ctype='string', cformat="", csource="",
                   inmobile=False, intablet=False, indesktop=False, 
                   options=[], **kwargs):
      
        has_filter = len(options) > 0
        has_icon = True if icon else False
        if not label:
            label = name.capitalize()
        column = {
            "name": name,
            "label": label,
            'type': self.column_type(ctype, cformat, csource),        
            "show": self.visible(inmobile, intablet, indesktop),            
            "sorting": sorting,
            "has_icon": has_icon,
            "icon": icon if has_icon else {},    
            "has_filter": has_filter
        }
        if has_filter:
            column["filter"] = {
                "options": self.create_filter_options(options)
            }   
        self.table["columns"].append(column)
        
        return self.table["columns"]
        
    def make_expandable(self, value=True):
        self.table["expandable"] = value
        
    def allow_edit(self, value=True):
        self.table["allowEditColumn"] = value
        
    def allow_row_selection(self, value=True):
        self.table["allowRowSelection"] = value
        
    def allow_download(self, value=True):
        self.table["downloadPermission"] = value
        
    def allow_search(self, value=True):
        self.table["searchPermission"] = value
        
    def set_pagination(self, num=50):
        self.table["pagination"] = num
        
    def set_size(self, size='middle'):
        self.table["size"] = size
        
    def allow_email(self, value=True):
        self.table["email"] = value
        
    def add_rows(self, 
                dataIn, 
                cursor, 
                job_profile_id, 
                job_title,
                company_name,
                location,
                url,
                **kwargs):
        data = copy.deepcopy(dataIn)
        #self.table['cursor'] = cursor  
        self.table['job_profile_id'] = job_profile_id
        self.table['job_title'] = job_title
        self.table['company_name'] = company_name
        self.table['location'] = location
        self.table['url'] = url

        # Check if data is a dictionary
        if isinstance(data, dict):
            # Add the entire dictionary (including nested lists) directly to the table's data
            self.table["data"].append(data)
            return self.table["data"]

        # If data is already a list, process each item
        if not isinstance(data, list):
            logger.warn("Data passed is not a list or dict")
            return self.table["data"]
        
        if not len(data) > 0:
            logger.warn("Empty data passed")
            return self.table["data"]
        
        if not isinstance(data[0], dict):
            logger.warn(f"Invalid data type for row: expects dict or list of dict. Passed {type(data[0])}")
            return self.table["data"]
            
        if len(self.table["columns"]) == 0:
            logger.warn("No columns defined for the table")
            return self.table["data"]
        
        # If it's a list of dictionaries, handle it as usual
        rows = self.table["data"]
        
        for item in data:
            row = {}
            # Add expandable content if it exists
            for x in ["expandableContent", "subdata"]:
                if x in item.keys():
                    row["expandableContent"] = item[x]
                    self.make_expandable(True)
                    break
            
            for col in self.table["columns"]:
                name = col["name"]
                row[name] = item.get(name, "")
            
            self.table["data"].append(row)
        
        return self.table["data"]
    
    def add_rows_for_engagment(self, 
                dataIn, 
                cursor,
                **kwargs):
        data = copy.deepcopy(dataIn)
        self.table['cursor'] = cursor  

        # Check if data is a dictionary
        if isinstance(data, dict):
            # Add the entire dictionary (including nested lists) directly to the table's data
            self.table["data"].append(data)
            return self.table["data"]

        # If data is already a list, process each item
        if not isinstance(data, list):
            logger.warn("Data passed is not a list or dict")
            return self.table["data"]
        
        if not len(data) > 0:
            logger.warn("Empty data passed")
            return self.table["data"]
        
        if not isinstance(data[0], dict):
            logger.warn(f"Invalid data type for row: expects dict or list of dict. Passed {type(data[0])}")
            return self.table["data"]
            
        if len(self.table["columns"]) == 0:
            logger.warn("No columns defined for the table")
            return self.table["data"]
        
        # If it's a list of dictionaries, handle it as usual
        rows = self.table["data"]
        
        for item in data:
            row = {}
            # Add expandable content if it exists
            for x in ["expandableContent", "subdata"]:
                if x in item.keys():
                    row["expandableContent"] = item[x]
                    self.make_expandable(True)
                    break
            
            for col in self.table["columns"]:
                name = col["name"]
                row[name] = item.get(name, "")
            
            self.table["data"].append(row)
        
        return self.table["data"]
    
    def init_structure(self, **kwargs):
        cursor = kwargs.get('cursor', {})
        job_profile_id = kwargs.get('job_profile_id', None)
        job_title = kwargs.get('job_title', None)
        company_name = kwargs.get('company_name', None)
        location = kwargs.get('location', None)
        url = kwargs.get('url', None)

        # Create a dictionary to hold the non-empty values
        additional_fields = {}

        if job_profile_id:
            additional_fields["job_profile_id"] = job_profile_id

        if job_title:
            additional_fields["job_title"] = job_title

        if company_name:
            additional_fields["company_name"] = company_name

        if location:
            additional_fields["location"] = location

        if url:
            additional_fields["url"] = url

        # Construct the table with mandatory fields
        table = {
            "view_type": "table",
            "order": kwargs.get('order', 1),
            "title": kwargs.get('title', ""),
            "data": kwargs.get('data', []),
            "columns": kwargs.get('columns', []),
            "expandable": kwargs.get('expandable', False),
            "allowEditColumn": kwargs.get('allowEditColumn', True),
            "counterName": kwargs.get("counterName", "record(s)"),
            "allowRowSelection": kwargs.get('expandable', True),
            "downloadPermission": kwargs.get('downloadPermission', True),
            "searchPermission": kwargs.get('searchPermission', True),
            "pagination": kwargs.get('pagination', 25),
            "size": kwargs.get('size', 'middle'),
            "email": kwargs.get('email', False),
            "cursor": cursor
        }

        table.update(additional_fields)

        return table

   
   
# {'job_competency_name': 'Data Management',
#    'best_matched_user_competency': 'Data Management',
#    'matched_skills': [{'name':'attention to detail','score':0},
#     'accuracy',
#     'basic data management principles',
#     'basic computer literacy'],
#    'missing_skills': [],
#    'match_score': 'high',
#    'confidence': 'high'},    