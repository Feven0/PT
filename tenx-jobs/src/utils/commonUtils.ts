import moment from 'moment';
import { cl, mo, mi, corporate, classic_view, minimalistic_view, modern_view, corporate_view } from "../assets";

export const capitalize = (str: string) => {
  return str?.charAt(0).toUpperCase() + str?.slice(1).toLowerCase();
}

export const matchStatuses = [
  { value: 'like', display: 'Like' },
  { value: 'super_like', display: 'Super Like' },
  { value: 'not_interested', display: 'Not Interested' },
  { value: 'not_this_but_fits', display: 'Not This But Fits' },
  { value: 'not_this_and_all_like_this', display: 'Not This And All Like This' }
];

export const reportStatus = [
  { value: 'link_not_working', display: 'Link Not Working' },
  { value: 'job_expired', display: 'Job Expired' },
  { value: 'scam_fraud_inappropriate', display: 'Scam/Fraud/Inappropriate' },
  { value: 'other', display: 'Other' },
];

export const reportDuplicate = [
  {
    value: "before_this_job",
    display: "Before this job"
  },
  {
    value: "today",
    display: "Today"
  },
  {
    value: "before_today",
    display: "Before today"
  }
]

export const checkboxOptions = [
  "Responsibilities",
  "Role",
  "Required Attributes"
];

export const sectionMap: { [key: string]: string } = {
  "Responsibilities": "job_responsibilities",
  "Role": "job_role",
  "Required Attributes": "job_requirements"
};

export const capitalizeFirstChar = (str: string): string => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
};


export const formatDateToYYYYMMDD = (dateString: string | null): string => {
  if (dateString === null) {
    return '';
  }
  return moment(dateString).format('YYYY-MM-DD');
};


export const getInitials = (username: string): string => {
  const nameParts = username.split(' ');
  if (nameParts.length > 1) {
    return `${nameParts[0].charAt(0)}${nameParts[1].charAt(0)}`.toUpperCase();
  }
  return username.charAt(0).toUpperCase();
};
export const getRandomColor = () => {
  const letters = '0123456789ABCDEF';
  let color = '#';
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}


export const normalizeType = (type: string) => {
  let normalized = type.toLowerCase().replace(/\s+/g, '-');
  
  const customMappings: Record<string, string> = {
    'internship': 'intern',
    'intern': 'internship',
  };

  if (customMappings[normalized]) {
    normalized = customMappings[normalized];
  }

  return normalized;
};

export const categories = ['skills', 'certificates', 'tools', 'knowledge', 'abilities'];
export const tags = ['include', 'exclude'];

export const templates = [
  {
    template_name: 'Classic',
    image: cl,
    image2: {
      name: 'classic',
      value: classic_view
    },
    template_id: '2',
    max_work_experience: 3,
    max_projects: 3,
    max_page: 2,
  },
  {
    template_name: 'Modern',
    image: mo,
    image2: {
      name: 'modern',
      value: modern_view
    },
    template_id: '1',
    max_work_experience: 4,
    max_projects: 4,
    max_page: 3,
  },
  {
    template_name: 'Minimalistic',
    image: mi,
    image2: {
      name: 'minimalistic',
      value: minimalistic_view
    },
    template_id: '3',
    max_work_experience: 2,
    max_projects: 2,
    max_page: 1,
  },
  {
  template_name: 'Corporate',
  image: corporate,
  image2: {
    name: 'corporate',
    value: corporate_view
  },
  template_id: '4',
  max_work_experience: 2,
  max_projects: 2,
  max_page: 1,
}
];

export const priorityLevels = ["high", "medium", "low"] as const;

export const priorities: Array<{ label: string; value: 'high' | 'medium' | 'low' }> = [
  { label: 'High', value: 'high' },
  { label: 'Medium', value: 'medium' },
  { label: 'Low', value: 'low' },
];

export const switchConfig = {
  'hide_action_bar': 'Hide Action Bar',
  'hide_bottom_navigation': 'Hide Bottom Navigation Bar'
};

export const defaultVisibility = [
  { 
    name: 'hide_action_bar', 
    default: true, 
    description: 'Hide or Not the Floating Action Bar' 
  },
  { name: 'hide_bottom_navigation', 
    default: true, 
    description: 'Hide or Not the Bottom Navigation Bar' 
  }
];


export const KeywordTags = [
  'skills',
  'certificates',
  'tools',
  'knowledge',
  'abilities',
] as const;


export const sources = [
  'Training',
  'Grade',
  'Github',
  'CV',
  'Web',
  'Document',
  'Other',
  "Gmeet",
  "Slack",
  "Email"
];

export const SFIA_Dimension = [
  "Autonomy",
  "Complexity",
  "Influence",
  "Business",
  "Knowledge"
];


export const allEmploymentTypes = ['full-time', 'contract', 'part-time', 'intern'];
export const  allCompanySizes = ['small', 'medium', 'large', 'enterprise'];
export const  allExperienceLevels = ['entry', 'mid', 'senior', 'lead'];
export const newJobApplication = ["Applied", "Ready to apply", "Interested"];
export const format = 'YYYY-MM-DD';
