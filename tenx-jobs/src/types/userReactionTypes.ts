export type Cursor = {
  query:      string;
  filter:     string;
  page:       number;
  page_size:  number;
  total:      number;
  page_count: number;
}

export type IconType = {
  type:   string;
  source: string;
  icon:   string;
}

export interface Show {
  mobile:  boolean;
  tablet:  boolean;
  desktop: boolean;
}


export interface Type {
  dtype:  string;
  format: string;
  source: string;
}

export type Datum = {
    user_reaction_id: string;
    company_name:     string;
    job_title:        string;
    job_location:     string;
    salary_range:     string;
    match_status:     string;
    match_score:      number;
    user_reaction:    string;
    apply_status:     string;
    applyLink:        string;
    createdAt:        string;
    job_id:           string;
    job_profile_id:   string;
    user_profile_id:  string;
    job_trainee_id:   string;
    all_user_id:      string;
    expand_reaction:  string;
}

export interface Option {
  name:  string;
  value: string;
}

export interface Filter {
  options: Option[];
}

export type Column = {
  name:       string;
  label:      string;
  type:       Type;
  show:       Show;
  sorting:    boolean;
  has_icon:   boolean;
  icon:       IconType;
  has_filter: boolean;
  filter?:    Filter;
}

export type T_Reactions = {
    view_type:            string;
    order:              number;
    title:              string;
    data:               Datum[];
    columns:            Column[];
    expandable:         boolean;
    allowEditColumn:    boolean;
    counterName:        string;
    allowRowSelection:  boolean;
    downloadPermission: boolean;
    searchPermission:   boolean;
    pagination:         number;
    size:               string;
    email:              boolean;
}


export type T_UserReaction = {
  all_user_id: string;
  reactions: T_Reactions[]
  cursor: Cursor;
  status: number;
  message: string;
}