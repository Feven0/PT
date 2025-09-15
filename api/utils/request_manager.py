import copy

from api import config
from api.services import redis_client as rc
import api.utils.aws_utils as awsut
from api.utils import tenx_uiux as uiux
from api.utils import tenx_uiux_copy as uiux_copy
from api.utils.logger import LLPackerLogger

logger = LLPackerLogger(__file__)


class JobManagerBase:
    def __init__(self, run_stage='', **kwargs):
        log_level = kwargs.get('log_level', None)

        # Setting the logging level
        if log_level and isinstance(log_level, int):
            logger._logger.setLevel(log_level)

        # Setting the run stage
        if not run_stage:
            self.run_stage = config.strapi_stage
        else:
            self.run_stage = run_stage

        # Token and user role
        self.token = kwargs.get('strapi_token', kwargs.get('token', kwargs.get('user_token', '')))
        self.user_role = kwargs.get('user_role', '')

        # Kwargs to be used across the instance
        lskw = dict(run_stage=run_stage, strapi_token=self.token, user_role=self.user_role, log_level=log_level)
        self.lskw = lskw

        # Storing additional options from kwargs
        opts = dict(limit=0, dataframe=False, since=0, raw=True, verbose=-1)
        opts.update(kwargs)
        self.kwargs = opts

        # Initialize Redis client
        self.rclient = rc.RedisClient(run_stage=run_stage)


class JobReactionManager(JobManagerBase):
    def __init__(self, run_stage='', table_title="", **kwargs) -> None:
        super().__init__(run_stage=run_stage, **kwargs)

        # Defining the UI/UX table
        self.keep_columns = []
        self.alias_columns = {}
        self.cursor = {}
        self.job_profile_id = {}, 
        self.job_title = {},
        self.company_name = {},
        self.location = {},
        self.url = {},
        # self.uiuxbt = uiux.BaseTable(title=table_title, )
        self.uiuxbt = uiux.BaseTable(title=table_title, cursor=self.cursor)
        self.uiuxbt_copy = uiux_copy.BaseTable(title=table_title, cursor=self.cursor)


        # Table column views for different devices
        desktop_view = ['job_title', 'job_match_score', 'job_match', 'score', 'complete_interviews_count', 'incomplete_interviews_count', 'total_interviews_count', 'expand']
        tablet_view = ['job_title', 'job_match_score', 'job_match', 'score', 'complete_interviews_count', 'incomplete_interviews_count', 'total_interviews_count', 'expand']
        mobile_view = ['job_title', 'job_match_score', 'job_match', 'score', 'complete_interviews_count', 'incomplete_interviews_count', 'total_interviews_count', 'expand']
        sorting = ['job_title', 'job_match_score', 'job_match', 'score', 'complete_interviews_count', 'incomplete_interviews_count', 'total_interviews_count']
        link_icon = []
        # download_icon = []
        expand_icon = ["expand"]
        keep_columns = ["expand"]

        # Columns configuration for the session jobs
        self.jobs_columns = {
            'job_profile_id': {'label': 'Job Profile ID', 'ctype': 'string', 'options': []},
            'reaction_id': {'label': 'Reaction ID', 'ctype': 'string', 'options': []},
            'job_title': {'label': 'Job Title', 'ctype': 'string', 'options': []},
            'job_match_score': {'label': 'Job Match Score', 'ctype': 'string', 'options': []},
            'job_match': {'label': 'Job Match', 'ctype': 'string', 'options': []},
            'complete_interviews_count': {'label': 'Complete Interview Count', 'ctype': 'number', 'options': []},
            'incomplete_interviews_count': {'label': 'Incomplete Interview Count', 'ctype': 'number', 'options': []},
            'total_interviews_count': {'label': 'Total Interview Coun    t', 'ctype': 'number', 'options': []},
            'score': {'label': 'Score', 'ctype': 'string', 'options': []},
            'expand': {'label':'Detail', 'ctype':'expand', 'csource':'details','cformat':'page', 'options':[]}
        }
        
        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.jobs_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.jobs_columns[x]['intablet'] = True
        for x in mobile_view:
            self.jobs_columns[x]['inmobile'] = True
        for x in sorting:
            self.jobs_columns[x]['sorting'] = False
        for x in link_icon:
            self.jobs_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.jobs_columns[x]['icon'] = self.uiuxbt.create_expand_icon("job_profile_id")
        for x in keep_columns:
            self.keep_columns.append(x)
        # Only assign icons if the list is not empty
        # if link_icon:
        #     for x in link_icon:
        #         self.jobs_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        # else:
        #     for x in self.jobs_columns.keys():
        #         self.jobs_columns[x]['icon'] = None  # Or False if preferred

        # if download_icon:
        #     for x in download_icon:
        #         self.jobs_columns[x]['icon'] = self.uiuxbt.create_download_icon()
        # else:
        #     for x in self.jobs_columns.keys():
        #         self.jobs_columns[x]['icon'] = None  # Or False if preferred

        
        # Colums configuration for the admin overview
        desktop_view = ['interviews_count', 'job_profile_count', 'user_profile_count', 'complete_sessions', 'incomplete_sessions', 'total_interview_sessions', 'day_sessions', 'week_sessions', 'month_sessions', 'year_sessions', 'today_sessions', 'current_week_sessions', 'current_month_sessions', 'current_year_sessions', 'daily_sessions_by_month']
        tablet_view = ['interviews_count', 'job_profile_count', 'user_profile_count', 'complete_sessions', 'incomplete_sessions', 'total_interview_sessions', 'day_sessions', 'week_sessions', 'month_sessions', 'year_sessions', 'today_sessions', 'current_week_sessions', 'current_month_sessions', 'current_year_sessions', 'daily_sessions_by_month']
        mobile_view = ['interviews_count', 'job_profile_count', 'user_profile_count', 'complete_sessions', 'incomplete_sessions', 'total_interview_sessions', 'day_sessions', 'week_sessions', 'month_sessions', 'year_sessions', 'today_sessions', 'current_week_sessions', 'current_month_sessions', 'current_year_sessions', 'daily_sessions_by_month']
        sorting = ['interviews_count', 'job_profile_count', 'user_profile_count', 'complete_sessions', 'incomplete_sessions', 'total_interview_sessions', 'day_sessions', 'week_sessions', 'month_sessions', 'year_sessions', 'today_sessions', 'current_week_sessions', 'current_month_sessions', 'current_year_sessions', 'daily_sessions_by_month']
        link_icon = []
        expand_icon = ["expand"]
        keep_columns = ["expand"]

        self.admin_overview_columns = {
            'interviews_count': {'label': 'Interviews Count', 'ctype': 'number', 'options': []},
            'job_profile_count': {'label': 'Job Profile Count', 'ctype': 'number', 'options': []},
            'user_profile_count': {'label': 'User Profile Count', 'ctype': 'number', 'options': []},
            'complete_sessions': {'label': 'Complete Sessions', 'ctype': 'number', 'options': []},
            'incomplete_sessions': {'label': 'Incomplete Sessions', 'ctype': 'number', 'options': []},
            'total_interview_sessions': {'label': 'Total Interviews', 'ctype': 'number', 'options': []},
            'day_sessions': {'label': 'Day Sessions', 'ctype': 'number', 'options': []},
            'week_sessions': {'label': 'Weak Sessions', 'ctype': 'number', 'options': []},
            'month_sessions': {'label': 'Month Sessions', 'ctype': 'number', 'options': []},
            'year_sessions': {'label': 'Year Sessions', 'ctype': 'number', 'options': []},
            'today_sessions': {'label': 'Today Sessions', 'ctype': 'number', 'options': []},
            'current_week_sessions': {'label': 'Current Week Sessions', 'ctype': 'number', 'options': []},
            'current_month_sessions': {'label': 'Current Month Sessions', 'ctype': 'number', 'options': []},
            'current_year_sessions': {'label': 'Current Year Sessions', 'ctype': 'number', 'options': []},
            'daily_sessions_by_month': {'label': 'Daily Sessions By Month', 'ctype': 'number', 'options': []},
            'expand': {'label':'Detail', 'ctype':'expand', 'csource':'details','cformat':'page', 'options':[]}

        }

        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.admin_overview_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.admin_overview_columns[x]['intablet'] = True
        for x in mobile_view:
            self.admin_overview_columns[x]['inmobile'] = True
        for x in sorting:
            self.admin_overview_columns[x]['sorting'] = False
        for x in link_icon:
            self.admin_overview_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.admin_overview_columns[x]['icon'] = self.uiuxbt.create_expand_icon("user_profile_id")
        for x in keep_columns:
            self.keep_columns.append(x)
        # Only assign icons if the list is not empty
        # if link_icon:
        #     for x in link_icon:
        #         self.admin_overview_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        # else:
        #     for x in self.admin_overview_columns.keys():
        #         self.admin_overview_columns[x]['icon'] = None  # Or False if preferred

        # if download_icon:
        #     for x in download_icon:
        #         self.admin_overview_columns[x]['icon'] = self.uiuxbt.create_download_icon()
        # else:
        #     for x in self.admin_overview_columns.keys():
        #         self.admin_overview_columns[x]['icon'] = None  # Or False if preferred

        # Colums configuration for the admin alluser info
        desktop_view = ['user_profile_id', 'all_user_id', 'name', 'role', 'batch', 'gender', 'nationality', 'job_count', 'total_interviews_count', 'complete_sessions_count', 'incomplete_sessions_count']
        tablet_view = ['user_profile_id', 'all_user_id', 'name', 'role', 'batch', 'gender', 'nationality', 'job_count', 'total_interviews_count', 'complete_sessions_count', 'incomplete_sessions_count']
        mobile_view = ['user_profile_id', 'all_user_id', 'name', 'role', 'batch', 'gender', 'nationality', 'job_count', 'total_interviews_count', 'complete_sessions_count', 'incomplete_sessions_count']
        sorting = ['all_user_id', 'user_profile_id', 'name', 'role', 'batch', 'gender', 'nationality', 'job_count', 'total_interviews_count', 'complete_sessions_count', 'incomplete_sessions_count']
        link_icon = []
        expand_icon = ["expand"]
        keep_columns = ["expand"]

        self.admin_alluser_columns = {
            'user_profile_id': {'label': 'User Profile ID', 'ctype': 'string', 'options': []},
            'all_user_id': {'label': 'All User ID', 'ctype': 'string', 'options': []},
            'name': {'label': 'Name', 'ctype': 'string', 'options': []},
            'role': {'label': 'Role', 'ctype': 'string', 'options': []},
            'batch': {'label': 'Batch', 'ctype': 'string', 'options': []},
            'gender': {'label': 'Gender', 'ctype': 'string', 'options': []},
            'nationality': {'label': 'Nationality', 'ctype': 'string', 'options': []},
            'job_count': {'label': 'Job Count', 'ctype': 'number', 'options': []},
            'total_interviews_count': {'label': 'Total Interviews Count', 'ctype': 'number', 'options': []},
            'complete_sessions_count': {'label': 'Complete Sessions Count', 'ctype': 'number', 'options': []},
            'incomplete_sessions_count': {'label': 'Incomplete Sessions Count', 'ctype': 'number', 'options': []},
            'expand': {'label':'Detail', 'ctype':'expand', 'csource':'details','cformat':'page', 'options':[]}
        }

        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.admin_alluser_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.admin_alluser_columns[x]['intablet'] = True
        for x in mobile_view:
            self.admin_alluser_columns[x]['inmobile'] = True
        for x in sorting:
            self.admin_alluser_columns[x]['sorting'] = False
        for x in link_icon:
            self.admin_alluser_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.admin_alluser_columns[x]['icon'] = self.uiuxbt.create_expand_icon("user_profile_id")
        for x in keep_columns:
            self.keep_columns.append(x)
        # Only assign icons if the list is not empty
        # if link_icon:
        #     for x in link_icon:
        #         self.admin_alluser_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        # else:
        #     for x in self.admin_alluser_columns.keys():
        #         self.admin_alluser_columns[x]['icon'] = None  # Or False if preferred

        # if download_icon:
        #     for x in download_icon:
        #         self.admin_alluser_columns[x]['icon'] = self.uiuxbt.create_download_icon()
        # else:
        #     for x in self.admin_alluser_columns.keys():
        #         self.admin_alluser_columns[x]['icon'] = None  # Or False if preferred

        
        # Colums configuration for the admin jobs info
        desktop_view = ['job_profile_id', 'job_title', 'total_interviews_count', 'complete_sessions_count', 'incomplete_sessions_count', 'company_name', 'location', 'url']
        tablet_view = ['job_profile_id', 'job_title', 'total_interviews_count', 'complete_sessions_count', 'incomplete_sessions_count', 'company_name', 'location', 'url']
        mobile_view = ['job_profile_id', 'job_title', 'total_interviews_count', 'complete_sessions_count', 'incomplete_sessions_count', 'company_name', 'location', 'url']
        sorting = ['job_profile_id', 'job_title', 'total_interviews_count', 'complete_sessions_count', 'incomplete_sessions_count', 'company_name', 'location', 'url']
        link_icon = []
        expand_icon = ["expand"]
        keep_columns = ["expand"]

        self.admin_jobs_columns = {
            'job_profile_id': {'label': 'Job Profile ID', 'ctype': 'string', 'options': []},
            'job_title': {'label': 'Job Title', 'ctype': 'string', 'options': []},
            'total_interviews_count': {'label': 'Total Interviews Count', 'ctype': 'number', 'options': []},
            'complete_sessions_count': {'label': 'Complete Sessions Count', 'ctype': 'number', 'options': []},
            'incomplete_sessions_count': {'label': 'Incomplete Sessions Count', 'ctype': 'number', 'options': []},
            'company_name': {'label': 'Company Name', 'ctype': 'string', 'options': []},
            'location': {'label': 'Location','ctype': 'string', 'options': []},
            'url': {'label': 'URL', 'ctype': 'string', 'options': []},
            'expand': {'label':'Detail', 'ctype':'expand', 'csource':'details','cformat':'page', 'options':[]}

        }

        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.admin_jobs_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.admin_jobs_columns[x]['intablet'] = True
        for x in mobile_view:
            self.admin_jobs_columns[x]['inmobile'] = True
        for x in sorting:
            self.admin_jobs_columns[x]['sorting'] = False
        for x in link_icon:
            self.admin_jobs_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.admin_jobs_columns[x]['icon'] = self.uiuxbt.create_expand_icon("job_profile_id")
        for x in keep_columns:
            self.keep_columns.append(x)
        # Only assign icons if the list is not empty
        # if link_icon:
        #     for x in link_icon:
        #         self.admin_jobs_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        # else:
        #     for x in self.admin_jobs_columns.keys():
        #         self.admin_jobs_columns[x]['icon'] = None  # Or False if preferred

        # if download_icon:
        #     for x in download_icon:
        #         self.admin_jobs_columns[x]['icon'] = self.uiuxbt.create_download_icon()
        # else:
        #     for x in self.admin_jobs_columns.keys():
        #         self.admin_jobs_columns[x]['icon'] = None  # Or False if preferred

        # Colums configuration for the admin alluser performance info
        desktop_view = ['user_profile_id', 'all_user_id', 'name', 'role', 'batch', 'nationality', 'metrics']
        tablet_view = ['user_profile_id', 'all_user_id', 'name', 'role', 'batch', 'nationality', 'metrics']
        mobile_view = ['user_profile_id', 'all_user_id', 'name', 'role', 'batch', 'nationality', 'metrics']
        sorting = ['user_profile_id', 'all_user_id', 'name', 'role', 'batch', 'nationality', 'metrics']
        link_icon = []
        expand_icon = ["expand"]
        keep_columns = ["expand"]

        self.admin_allusers_performance_columns = {
            'user_profile_id': {'label': 'User Profile ID', 'ctype': 'string', 'options': []},
            'all_user_id': {'label': 'All User ID', 'ctype': 'string', 'options': []},
            'name': {'label': 'Name', 'ctype': 'string', 'options': []},
            'role': {'label': 'Role', 'ctype': 'string', 'options': []},
            'batch': {'label': 'Batch', 'ctype': 'string', 'options': []},
            'gender': {'label': 'Gender', 'ctype': 'string', 'options': []},
            'nationality': {'label': 'Nationality', 'ctype': 'string', 'options': []},            
            'metrics': {'label': 'Metrics', 'ctype': 'string', 'options': []},
            'expand': {'label':'Detail', 'ctype':'expand', 'csource':'details','cformat':'page', 'options':[]}
        }

        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.admin_allusers_performance_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.admin_allusers_performance_columns[x]['intablet'] = True
        for x in mobile_view:
            self.admin_allusers_performance_columns[x]['inmobile'] = True
        for x in sorting:
            self.admin_allusers_performance_columns[x]['sorting'] = False
        for x in link_icon:
            self.admin_allusers_performance_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.admin_allusers_performance_columns[x]['icon'] = self.uiuxbt.create_expand_icon("user_profile_id")
        for x in keep_columns:
            self.keep_columns.append(x)
        # Only assign icons if the list is not empty
        # if link_icon:
        #     for x in link_icon:
        #         self.admin_allusers_performance_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        # else:
        #     for x in self.admin_allusers_performance_columns.keys():
        #         self.admin_allusers_performance_columns[x]['icon'] = None  # Or False if preferred

        # if download_icon:
        #     for x in download_icon:
        #         self.admin_allusers_performance_columns[x]['icon'] = self.uiuxbt.create_download_icon()
        # else:
        #     for x in self.admin_allusers_performance_columns.keys():
        #         self.admin_allusers_performance_columns[x]['icon'] = None  # Or False if preferred

        # Colums configuration for the admin each job info
        desktop_view = ['user_profile_id', 'trainee_name', 'total_interview_count', 'complete_sessions_count', 'incomplete_sessions_count', 'average_score', 'expand']
        tablet_view = ['user_profile_id', 'trainee_name', 'total_interview_count', 'complete_sessions_count', 'incomplete_sessions_count', 'average_score', 'expand']
        mobile_view = ['user_profile_id', 'trainee_name', 'total_interview_count', 'complete_sessions_count', 'incomplete_sessions_count', 'average_score', 'expand']
        sorting = ['user_profile_id', 'trainee_name', 'total_interview_count', 'complete_sessions_count', 'incomplete_sessions_count', 'average_score', 'expand']
        link_icon = []
        expand_icon = ["expand"]
        keep_columns = ["expand"]
        
        self.admin_each_job_columns = {
            "trainee_name": {'label': 'Trainee Name', 'ctype': 'string', 'options': []},
            'total_interview_count': {'label': 'Total Interview Count', 'ctype': 'number', 'options': []},
            'complete_sessions_count': {'label': 'Complete Sessions Count', 'ctype': 'number', 'options': []},
            'incomplete_sessions_count': {'label': 'Incomplete Sessions Count', 'ctype': 'number', 'options': []},
            # "individual_scores": {'label': 'Individual Scores', 'ctype': 'list', 'options': []},
            "average_score": {'label': 'Average Score', 'ctype': 'string', 'options': []},
            "user_profile_id": {'label': 'User Profile ID', 'ctype': 'string', 'options': []},
            'expand': {'label':'Detail', 'ctype':'expand', 'csource':'details','cformat':'page', 'options':[]},

        }
        
        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.admin_each_job_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.admin_each_job_columns[x]['intablet'] = True
        for x in mobile_view:
            self.admin_each_job_columns[x]['inmobile'] = True
        for x in sorting:
            self.admin_each_job_columns[x]['sorting'] = False
        for x in link_icon:
            self.admin_each_job_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.admin_each_job_columns[x]['icon'] = self.uiuxbt.create_expand_icon("user_profile_id")
        for x in keep_columns:
            self.keep_columns.append(x)

        
        # Colums configuration for the admin each job info
        desktop_view = ['user_profile_id', 'trainee_name', 'total_interview_count', 'complete_sessions_count', 'incomplete_sessions_count', 'average_score', 'expand']
        tablet_view = ['user_profile_id', 'trainee_name', 'total_interview_count', 'complete_sessions_count', 'incomplete_sessions_count', 'average_score', 'expand']
        mobile_view = ['user_profile_id', 'trainee_name', 'total_interview_count', 'complete_sessions_count', 'incomplete_sessions_count', 'average_score', 'expand']
        sorting = ['user_profile_id', 'trainee_name', 'total_interview_count', 'complete_sessions_count', 'incomplete_sessions_count', 'average_score', 'expand']
        link_icon = []
        expand_icon = ["expand"]
        keep_columns = ["expand"]
        
        self.admin_each_challenge_columns = {
            "trainee_name": {'label': 'Trainee Name', 'ctype': 'string', 'options': []},
            'total_interview_count': {'label': 'Total Interview Count', 'ctype': 'number', 'options': []},
            'complete_sessions_count': {'label': 'Complete Sessions Count', 'ctype': 'number', 'options': []},
            'incomplete_sessions_count': {'label': 'Incomplete Sessions Count', 'ctype': 'number', 'options': []},
            # "individual_scores": {'label': 'Individual Scores', 'ctype': 'list', 'options': []},
            "average_score": {'label': 'Average Score', 'ctype': 'string', 'options': []},
            "user_profile_id": {'label': 'User Profile ID', 'ctype': 'string', 'options': []},
            'expand': {'label':'Detail', 'ctype':'expand', 'csource':'details','cformat':'page', 'options':[]},

        }
        
        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.admin_each_challenge_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.admin_each_challenge_columns[x]['intablet'] = True
        for x in mobile_view:
            self.admin_each_challenge_columns[x]['inmobile'] = True
        for x in sorting:
            self.admin_each_challenge_columns[x]['sorting'] = False
        for x in link_icon:
            self.admin_each_challenge_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.admin_each_challenge_columns[x]['icon'] = self.uiuxbt.create_expand_icon("user_profile_id")
        for x in keep_columns:
            self.keep_columns.append(x)


        # Colums configuration for the admin each job info
        desktop_view = ['id', 'name', 'type', 'tag', 'description', 'tinder_job_profiles', 'expand']
        tablet_view = ['id', 'name', 'type', 'tag', 'description', 'tinder_job_profiles', 'expand']
        mobile_view = ['id', 'name', 'type', 'tag', 'description', 'tinder_job_profiles', 'expand']
        sorting = ['id', 'name', 'type', 'tag', 'description', 'tinder_job_profiles', 'expand']
        link_icon = []
        expand_icon = ["expand"]
        keep_columns = ["expand"]
        
        self.template_columns = {
            'id': {'label': 'Template ID', 'ctype': 'string', 'options': []},
            'name': {'label': 'Name', 'ctype': 'string', 'options': []},
            'type': {'label': 'Type', 'ctype': 'string', 'options': []},
            'tag': {'label': 'Tag', 'ctype': 'tag_list', 'options': []},
            'description': {'label': 'Description', 'ctype': 'string', 'options': []},
            'tinder_job_profiles': {'label': 'Job Profiles Count', 'ctype': 'number', 'options': []},
            'expand': {'label':'Detail', 'ctype':'expand', 'csource':'details','cformat':'page', 'options':[]},

        }
        
        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.template_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.template_columns[x]['intablet'] = True
        for x in mobile_view:
            self.template_columns[x]['inmobile'] = True
        for x in sorting:
            self.template_columns[x]['sorting'] = False
        for x in link_icon:
            self.template_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.template_columns[x]['icon'] = self.uiuxbt.create_expand_icon("id")
        for x in keep_columns:
            self.keep_columns.append(x)

        # Colums configuration for the admin each job info
        desktop_view = ['id', 'name', 'type', 'tag', 'description', 'tinder_job_profiles', 'expand']
        tablet_view = ['id', 'name', 'type', 'tag', 'description', 'tinder_job_profiles', 'expand']
        mobile_view = ['id', 'name', 'type', 'tag', 'description', 'tinder_job_profiles', 'expand']
        sorting = ['id', 'name', 'type', 'tag', 'description', 'tinder_job_profiles', 'expand']
        link_icon = []
        expand_icon = ["expand"]
        keep_columns = ["expand"]
        
        self.template_columns = {
            'id': {'label': 'Template ID', 'ctype': 'string', 'options': []},
            'name': {'label': 'Name', 'ctype': 'string', 'options': []},
            'type': {'label': 'Type', 'ctype': 'string', 'options': []},
            'tag': {'label': 'Tag', 'ctype': 'tag_list', 'options': []},
            'description': {'label': 'Description', 'ctype': 'string', 'options': []},
            'tinder_job_profiles': {'label': 'Job Profiles Count', 'ctype': 'number', 'options': []},
            'expand': {'label':'Detail', 'ctype':'expand', 'csource':'details','cformat':'page', 'options':[]},

        }
        
        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.template_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.template_columns[x]['intablet'] = True
        for x in mobile_view:
            self.template_columns[x]['inmobile'] = True
        for x in sorting:
            self.template_columns[x]['sorting'] = False
        for x in link_icon:
            self.template_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.template_columns[x]['icon'] = self.uiuxbt.create_expand_icon("id")
        for x in keep_columns:
            self.keep_columns.append(x)



        # Colums configuration for the admin job by template_id info
        desktop_view = ['title', 'company','level', 'job_link']
        tablet_view = ['title', 'company','level', 'job_link']
        mobile_view = ['title', 'company','level', 'job_link']
        sorting = ['title', 'company','level', 'job_link']
        link_icon = ['job_link']
        expand_icon = []
        keep_columns = []
        

        self.job_by_template_columns = {
            'job_id': {'label': 'Job ID', 'ctype': 'string', 'options': []},
            'title': {'label': 'Title', 'ctype': 'string', 'options': []},
            'company': {'label': 'Company', 'ctype': 'string', 'options': []},
            'level': {'label': 'Level', 'ctype': 'string', 'options': []},
            'job_link': {'label': 'Apply linK', 'ctype': 'icon', 'options': []},
            # 'preview': {'label':'Preview', 'ctype':'preview', 'csource':'preview','cformat':'page', 'options':[]},

        }
        
        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.job_by_template_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.job_by_template_columns[x]['intablet'] = True
        for x in mobile_view:
            self.job_by_template_columns[x]['inmobile'] = True
        for x in sorting:
            self.job_by_template_columns[x]['sorting'] = False
        for x in link_icon:
            self.job_by_template_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.job_by_template_columns[x]['icon'] = self.uiuxbt.create_preview_icon("job_id")
        for x in keep_columns:
            self.keep_columns.append(x)


        # Colums configuration for the admin challenge by template_id info
        desktop_view = ['title', 'preview']
        tablet_view = ['title', 'preview']
        mobile_view = ['title', 'preview']
        sorting = ['title', 'preview']
        link_icon = []
        expand_icon = ["preview"]
        keep_columns = ["preview"]
        

        self.challenge_by_template_columns = {
            'challenge_id': {'label': 'Challenge ID', 'ctype': 'string', 'options': []},
            'title': {'label': 'Title', 'ctype': 'string', 'options': []},
            'subtitle': {'label': 'Subtitle', 'ctype': 'string', 'options': []},
            'preview': {'label':'Preview', 'ctype':'preview', 'csource':'preview','cformat':'page', 'options':[]},
        }
        
        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.challenge_by_template_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.challenge_by_template_columns[x]['intablet'] = True
        for x in mobile_view:
            self.challenge_by_template_columns[x]['inmobile'] = True
        for x in sorting:
            self.challenge_by_template_columns[x]['sorting'] = False
        for x in link_icon:
            self.challenge_by_template_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.challenge_by_template_columns[x]['icon'] = self.uiuxbt.create_preview_icon("challenge_id")
        for x in keep_columns:
            self.keep_columns.append(x)

        # Colums configuration for the admin challenge by template_id info
        desktop_view = ['tag', "trainee_name", 'email', 'title', 'total_interview_count', "average_score", 'preview' ]
        tablet_view = ['tag', "trainee_name", 'email', 'title', 'total_interview_count', "average_score", 'preview']
        mobile_view = ['tag', "trainee_name", 'email', 'title', 'total_interview_count', "average_score", 'preview']
        sorting = ['tag', "trainee_name", 'email', 'title', 'total_interview_count', "average_score", 'preview']
        link_icon = []
        expand_icon = ["preview"]
        keep_columns = ["preview"]
        

        self.interview_by_template_columns = {
            "trainee_name": {'label': 'Trainee Name', 'ctype': 'string', 'options': []},
            "email": {'label': 'Trainee Email', 'ctype': 'string', 'options': []},
            'title': {'label': 'Title', 'ctype': 'string', 'options': []},
            'total_interview_count': {'label': 'Total Interview Count', 'ctype': 'number', 'options': []},
            "average_score": {'label': 'Average Score', 'ctype': 'string', 'options': []},            'user_profile_id': {'label': 'User Profile ID', 'ctype': 'string', 'options': []},
            'complete_sessions_count': {'label': 'Complete Sessions Count', 'ctype': 'number', 'options': []},
            'incomplete_sessions_count': {'label': 'Incomplete Sessions Count', 'ctype': 'number', 'options': []},
            'tag': {'label': 'Tag', 'ctype': 'string', 'options': []},
            'template_id': {'label': 'Template ID', 'ctype': 'string', 'options': []},
            'user_profile_id': {'label': 'User Profile ID', 'ctype': 'string', 'options': []},
            'job_profile_id': {'label': 'Job Profile ID', 'ctype': 'string', 'options': []},
            'challenge_id': {'label': 'Challenge ID', 'ctype': 'string', 'options': []},
            'preview': {'label':'Preview', 'ctype':'preview', 'csource':'preview','cformat':'page', 'options':[]},
        }
        
        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.interview_by_template_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.interview_by_template_columns[x]['intablet'] = True
        for x in mobile_view:
            self.interview_by_template_columns[x]['inmobile'] = True
        for x in sorting:
            self.interview_by_template_columns[x]['sorting'] = False
        for x in link_icon:
            self.interview_by_template_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.interview_by_template_columns[x]['icon'] = self.uiuxbt.create_preview_icon("")
        for x in keep_columns:
            self.keep_columns.append(x)


        # Table column views for different devices
        desktop_view = ['challenge_title', 'score', 'complete_interviews_count', 'incomplete_interviews_count', 'total_interviews_count', 'expand']
        tablet_view = ['challenge_title', 'score', 'complete_interviews_count', 'incomplete_interviews_count', 'total_interviews_count', 'expand']
        mobile_view = ['challenge_title', 'score', 'complete_interviews_count', 'incomplete_interviews_count', 'total_interviews_count', 'expand']
        sorting = ['challenge_title', 'score', 'complete_interviews_count', 'incomplete_interviews_count', 'total_interviews_count']
        link_icon = []
        # download_icon = []
        expand_icon = ["expand"]
        keep_columns = ["expand"]

        # Columns configuration for the session jobs
        self.challenge_columns = {
            'challenge_id': {'label': 'Challenge ID', 'ctype': 'string', 'options': []},
            'challenge_title': {'label': 'Challenge Title', 'ctype': 'string', 'options': []},
            'complete_interviews_count': {'label': 'Complete Interview Count', 'ctype': 'number', 'options': []},
            'incomplete_interviews_count': {'label': 'Incomplete Interview Count', 'ctype': 'number', 'options': []},
            'total_interviews_count': {'label': 'Total Interview Count', 'ctype': 'number', 'options': []},
            'score': {'label': 'Score', 'ctype': 'string', 'options': []},
            'expand': {'label':'Detail', 'ctype':'expand', 'csource':'details','cformat':'page', 'options':[]}
        }
        
        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.challenge_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.challenge_columns[x]['intablet'] = True
        for x in mobile_view:
            self.challenge_columns[x]['inmobile'] = True
        for x in sorting:
            self.challenge_columns[x]['sorting'] = False
        for x in link_icon:
            self.challenge_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.challenge_columns[x]['icon'] = self.uiuxbt.create_expand_icon("challenge_id")
        for x in keep_columns:
            self.keep_columns.append(x)


        # Table column views for different devices - Template Engagement
        desktop_view = ['template_title', 'template_type', 'score', 'complete_interviews_count', 'incomplete_interviews_count', 'total_interviews_count', 'expand']
        tablet_view = ['template_title', 'template_type', 'score', 'complete_interviews_count', 'incomplete_interviews_count', 'total_interviews_count', 'expand']
        mobile_view = ['template_title', 'template_type', 'score', 'complete_interviews_count', 'incomplete_interviews_count', 'total_interviews_count', 'expand']
        sorting = ['template_title', 'template_type', 'score', 'complete_interviews_count', 'incomplete_interviews_count', 'total_interviews_count']
        link_icon = []
        # download_icon = []
        expand_icon = ["expand"]
        keep_columns = ["expand"]

        # Columns configuration for template engagement
        self.template_engagement_columns = {
            'template_id': {'label': 'Template ID', 'ctype': 'string', 'options': []},
            'template_title': {'label': 'Template Title', 'ctype': 'string', 'options': []},
            'template_type': {'label': 'Template Type', 'ctype': 'string', 'options': []},
            'complete_interviews_count': {'label': 'Complete Interview Count', 'ctype': 'number', 'options': []},
            'incomplete_interviews_count': {'label': 'Incomplete Interview Count', 'ctype': 'number', 'options': []},
            'total_interviews_count': {'label': 'Total Interview Count', 'ctype': 'number', 'options': []},
            'score': {'label': 'Score', 'ctype': 'string', 'options': []},
            'expand': {'label':'Detail', 'ctype':'expand', 'csource':'details','cformat':'page', 'options':[]}
        }
        
        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.template_engagement_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.template_engagement_columns[x]['intablet'] = True
        for x in mobile_view:
            self.template_engagement_columns[x]['inmobile'] = True
        for x in sorting:
            self.template_engagement_columns[x]['sorting'] = False
        for x in link_icon:
            self.template_engagement_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.template_engagement_columns[x]['icon'] = self.uiuxbt.create_expand_icon("template_id")
        for x in keep_columns:
            self.keep_columns.append(x)


        # Table column views for different devices
        desktop_view = ['interview_count', 'type', 'title', 'score', 'expand']
        tablet_view = ['interview_count', 'type', 'title', 'score', 'expand']
        mobile_view = ['interview_count', 'type', 'title', 'score', 'expand']
        sorting = ['interview_count', 'type', 'title', 'score']
        link_icon = []
        # download_icon = []
        expand_icon = ["expand"]
        keep_columns = ["expand"]

        # Columns configuration for the session jobs
        self.engagement_all_columns = {
            'reaction_id': {'label': 'Reaction ID', 'ctype': 'string', 'options': []},
            'challenge_id': {'label': 'Challenge ID', 'ctype': 'string', 'options': []},
            'job_profile_id': {'label': 'Job Profile ID', 'ctype': 'string', 'options': []},
            'user_profile_id': {'label': 'User Profile ID', 'ctype': 'string', 'options': []},
            'template_id': {'label': 'Template ID', 'ctype': 'string', 'options': []},
            # 'context_id': {'label': 'Context ID', 'ctype': 'string', 'options': []},
            'interview_count': {'label': 'Interview Count', 'ctype': 'number', 'options': []},
            'type': {'label': 'Type', 'ctype': 'number', 'options': []},
            'title': {'label': 'Title', 'ctype': 'string', 'options': []},
            'score': {'label': 'Score', 'ctype': 'string', 'options': []},
            'expand': {'label':'Detail', 'ctype':'expand', 'csource':'details','cformat':'page', 'options':[]}
        }
        
        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.engagement_all_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.engagement_all_columns[x]['intablet'] = True
        for x in mobile_view:
            self.engagement_all_columns[x]['inmobile'] = True
        for x in sorting:
            self.engagement_all_columns[x]['sorting'] = False
        for x in link_icon:
            self.engagement_all_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.engagement_all_columns[x]['icon'] = self.uiuxbt.create_expand_icon("user_profile_id")
        for x in keep_columns:
            self.keep_columns.append(x)

        # Colums configuration for the admin tinder template info
        desktop_view = ['name', 'tag', 'description', 'expand']
        tablet_view = ['name', 'tag', 'description', 'expand']
        mobile_view = ['name', 'tag', 'description', 'expand']
        sorting = ['name', 'tag', 'description', 'expand']
        link_icon = []
        expand_icon = ["expand"]
        keep_columns = ["expand"]

        self.tinder_template_columns = {
            'template_id': {'label': 'Template ID', 'ctype': 'string', 'options': []},
            'name': {'label': 'Name', 'ctype': 'string', 'options': []},
            'tag': {'label': 'Tag', 'ctype': 'string', 'options': []},
            'description': {'label': 'Description', 'ctype': 'string', 'options': []},
            'expand': {'label':'Detail', 'ctype':'expand', 'csource':'details','cformat':'page', 'options':[]},
        }
        
        # Set column visibility for different devices and icons
        for x in desktop_view:
            self.tinder_template_columns[x]['indesktop'] = True
        for x in tablet_view:
            self.tinder_template_columns[x]['intablet'] = True
        for x in mobile_view:
            self.tinder_template_columns[x]['inmobile'] = True
        for x in sorting:
            self.tinder_template_columns[x]['sorting'] = False
        for x in link_icon:
            self.tinder_template_columns[x]['icon'] = self.uiuxbt.create_link_icon()
        for x in expand_icon:
            self.tinder_template_columns[x]['icon'] = self.uiuxbt.create_expand_icon("template_id")
        for x in keep_columns:
            self.keep_columns.append(x)

        # Initialize the table
        self.table = self.uiuxbt.table

    def _remove_empty_columns(self, rows, colmap):
        """Remove empty columns from the table based on row data."""
        rm_columns = []
        for c, cval in colmap.items():
            col_vals = [r.get(c, '') for r in rows if r.get(c, '')]
            if len(col_vals) == 0 and c not in self.keep_columns:
                rm_columns.append(c)

        # Remove columns from the table configuration
        for crow in self.uiuxbt.table['columns']:
            if crow['name'] in rm_columns:
                self.uiuxbt.table['columns'].remove(crow)

        # Remove columns from the rows
        for r in rows:
            for c in rm_columns:
                _ = r.pop(c, "")

        logger.good(f'Removed the following empty columns from reaction table: {rm_columns}')
        return rows

    def prepare_table(self, 
                    params, 
                    cursor, 
                    job_profile_id, 
                    job_title,
                    company_name,
                    location,
                    url,
                    kind, 
                    **kwargs):
        """Prepare a table for displaying reaction data."""
        rows = []
        pkey = None
        self.cursor = cursor
        if kind == 'jobs':
            pkey = 'attributes'
            colmap = self.jobs_columns
        elif kind == 'admin_overview':
            colmap = self.admin_overview_columns
        elif kind == 'admin_alluser':
            colmap = self.admin_alluser_columns
        elif kind == 'admin_jobs':
            colmap = self.admin_jobs_columns
        elif kind == 'admin_allusers_performance':
            colmap = self.admin_allusers_performance_columns
        elif kind == 'admin_each_job':
            colmap = self.admin_each_job_columns 
    

        for c, cval in colmap.items():
            cval['name'] = c
            _ = self.uiuxbt.add_column(**cval)

        strifnone = lambda x: x if x else ''

        # Remove empty columns and add rows to the table
        if rows:
            rows = self._remove_empty_columns(params, colmap)
            _ = self.uiuxbt.add_rows(rows)
        else:
            _ = self.uiuxbt.add_rows(
                params, 
                cursor,
                job_profile_id, 
                job_title,
                company_name,
                location,
                url)

        return self.uiuxbt.table

    def prepare_table_challenge(self, 
                    params, 
                    cursor, 
                    challenge_id, 
                    challenge_title,
                    kind, 
                    **kwargs):
        """Prepare a table for displaying reaction data."""
        rows = []
        pkey = None
        self.cursor = cursor
        if kind == 'jobs':
            pkey = 'attributes'
            colmap = self.jobs_columns
        elif kind == 'admin_overview':
            colmap = self.admin_overview_columns
        elif kind == 'admin_alluser':
            colmap = self.admin_alluser_columns
        elif kind == 'admin_jobs':
            colmap = self.admin_jobs_columns
        elif kind == 'admin_allusers_performance':
            colmap = self.admin_allusers_performance_columns
        elif kind == 'admin_each_job':
            colmap = self.admin_each_job_columns 
        elif kind == 'admin_each_challenge':
            colmap = self.admin_each_challenge_columns 

        for c, cval in colmap.items():
            cval['name'] = c
            _ = self.uiuxbt.add_column(**cval)

        strifnone = lambda x: x if x else ''

        # Remove empty columns and add rows to the table
        if rows:
            rows = self._remove_empty_columns(params, colmap)
            _ = self.uiuxbt.add_rows_for_challenge(rows)
        else:
            _ = self.uiuxbt.add_rows_for_challenge(
                params, 
                cursor,
                challenge_id, 
                challenge_title
               )

        return self.uiuxbt.table

    def prepare_engagement_table(self, 
                        params, 
                        cursor, 
                        kind, 
                        **kwargs):
            """Prepare a table for displaying reaction data."""
            rows = []
            pkey = None
            self.cursor = cursor
            if kind == 'jobs':
                pkey = 'attributes'
                colmap = self.jobs_columns
            elif kind == 'admin_overview':
                colmap = self.admin_overview_columns
            elif kind == 'admin_alluser':
                colmap = self.admin_alluser_columns
            elif kind == 'admin_jobs':
                colmap = self.admin_jobs_columns
            elif kind == 'admin_allusers_performance':
                colmap = self.admin_allusers_performance_columns
            elif kind == 'admin_each_job':
                colmap = self.admin_each_job_columns 
            elif kind == 'challenge':
                colmap = self.challenge_columns 
            elif kind == 'engagment-all':
                colmap = self.engagement_all_columns 
            elif kind == 'template':
                colmap = self.template_engagement_columns 

            for c, cval in colmap.items():
                cval['name'] = c
                _ = self.uiuxbt_copy.add_column(**cval)

            strifnone = lambda x: x if x else ''

            # Remove empty columns and add rows to the table
            if rows:
                rows = self._remove_empty_columns(params, colmap)
                _ = self.uiuxbt_copy.add_rows_for_engagment(rows)
            else:
                _ = self.uiuxbt_copy.add_rows_for_engagment(params, cursor)

            return self.uiuxbt_copy.table
    

    def prepare_template_table(self, 
                        params, 
                        cursor, 
                        kind, 
                        **kwargs):
            """Prepare a table for displaying reaction data."""
            rows = []
            pkey = None
            self.cursor = cursor
            if kind == 'jobs':
                pkey = 'attributes'
                colmap = self.jobs_columns
            elif kind == 'admin_overview':
                colmap = self.admin_overview_columns
            elif kind == 'admin_alluser':
                colmap = self.admin_alluser_columns
            elif kind == 'admin_jobs':
                colmap = self.admin_jobs_columns
            elif kind == 'admin_allusers_performance':
                colmap = self.admin_allusers_performance_columns
            elif kind == 'admin_each_job':
                colmap = self.admin_each_job_columns 
            elif kind == 'template':
                colmap = self.template_columns
            elif kind == 'job_by_template':
                colmap = self.job_by_template_columns
            elif kind == 'challenge_by_template':
                colmap = self.challenge_by_template_columns
            elif kind == 'interview_by_template':
                colmap = self.interview_by_template_columns
            elif kind == 'tinder_template':
                colmap = self.tinder_template_columns

            for c, cval in colmap.items():
                cval['name'] = c
                _ = self.uiuxbt.add_column(**cval)

            strifnone = lambda x: x if x else ''

            # Remove empty columns and add rows to the table
            if rows:
                rows = self._remove_empty_columns(params, colmap)
                _ = self.uiuxbt.add_rows_for_template(rows)
            else:
                _ = self.uiuxbt.add_rows_for_template(params, cursor)
            
            return self.uiuxbt.table
