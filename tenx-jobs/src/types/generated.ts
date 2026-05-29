export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
  Date: { input: any; output: any; }
  DateTime: { input: any; output: any; }
  JSON: { input: any; output: any; }
  Upload: { input: any; output: any; }
};

export type AllUser = {
  __typename?: 'AllUser';
  Batch?: Maybe<Scalars['Int']['output']>;
  RefCreate?: Maybe<ReferenceRelationResponseCollection>;
  chat_informations?: Maybe<ChatInformationRelationResponseCollection>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  email: Scalars['String']['output'];
  exchanges?: Maybe<ExchangeRelationResponseCollection>;
  grades?: Maybe<GradeRelationResponseCollection>;
  groups?: Maybe<GroupRelationResponseCollection>;
  image_link?: Maybe<Scalars['String']['output']>;
  job_matches?: Maybe<JobMatchRelationResponseCollection>;
  job_review_responses?: Maybe<JobReviewResponseRelationResponseCollection>;
  job_rubrics?: Maybe<JobRubricRelationResponseCollection>;
  jobs?: Maybe<JobRelationResponseCollection>;
  messages?: Maybe<MessageRelationResponseCollection>;
  name: Scalars['String']['output'];
  notification_statuses?: Maybe<NotificationStatusRelationResponseCollection>;
  notifications?: Maybe<NotificationRelationResponseCollection>;
  profile_information?: Maybe<ProfileInformationEntityResponse>;
  references?: Maybe<ReferenceRelationResponseCollection>;
  reviewer?: Maybe<ReviewerEntityResponse>;
  reviews?: Maybe<ReviewRelationResponseCollection>;
  role: Enum_Alluser_Role;
  smg_criteria?: Maybe<SmgCriterionRelationResponseCollection>;
  smg_criterion_metrics?: Maybe<SmgCriterionMetricRelationResponseCollection>;
  smg_metric_prompts?: Maybe<SmgMetricPromptRelationResponseCollection>;
  smg_prompt_templates?: Maybe<SmgPromptTemplateRelationResponseCollection>;
  smg_rubrics?: Maybe<SmgRubricRelationResponseCollection>;
  tinder_user_profiles?: Maybe<TinderUserProfileRelationResponseCollection>;
  tinder_user_reactions?: Maybe<TinderUserReactionRelationResponseCollection>;
  trainee?: Maybe<TraineeEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  user?: Maybe<UsersPermissionsUserEntityResponse>;
};


export type AllUserRefCreateArgs = {
  filters?: InputMaybe<ReferenceFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserChat_InformationsArgs = {
  filters?: InputMaybe<ChatInformationFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserExchangesArgs = {
  filters?: InputMaybe<ExchangeFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserGradesArgs = {
  filters?: InputMaybe<GradeFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserGroupsArgs = {
  filters?: InputMaybe<GroupFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserJob_MatchesArgs = {
  filters?: InputMaybe<JobMatchFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserJob_Review_ResponsesArgs = {
  filters?: InputMaybe<JobReviewResponseFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserJob_RubricsArgs = {
  filters?: InputMaybe<JobRubricFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserJobsArgs = {
  filters?: InputMaybe<JobFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserMessagesArgs = {
  filters?: InputMaybe<MessageFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserNotification_StatusesArgs = {
  filters?: InputMaybe<NotificationStatusFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserNotificationsArgs = {
  filters?: InputMaybe<NotificationFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserReferencesArgs = {
  filters?: InputMaybe<ReferenceFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserReviewsArgs = {
  filters?: InputMaybe<ReviewFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserSmg_CriteriaArgs = {
  filters?: InputMaybe<SmgCriterionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserSmg_Criterion_MetricsArgs = {
  filters?: InputMaybe<SmgCriterionMetricFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserSmg_Metric_PromptsArgs = {
  filters?: InputMaybe<SmgMetricPromptFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserSmg_Prompt_TemplatesArgs = {
  filters?: InputMaybe<SmgPromptTemplateFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserSmg_RubricsArgs = {
  filters?: InputMaybe<SmgRubricFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserTinder_User_ProfilesArgs = {
  filters?: InputMaybe<TinderUserProfileFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AllUserTinder_User_ReactionsArgs = {
  filters?: InputMaybe<TinderUserReactionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type AllUserEntity = {
  __typename?: 'AllUserEntity';
  attributes?: Maybe<AllUser>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type AllUserEntityResponse = {
  __typename?: 'AllUserEntityResponse';
  data?: Maybe<AllUserEntity>;
};

export type AllUserEntityResponseCollection = {
  __typename?: 'AllUserEntityResponseCollection';
  data: Array<AllUserEntity>;
  meta: ResponseCollectionMeta;
};

export type AllUserFiltersInput = {
  Batch?: InputMaybe<IntFilterInput>;
  RefCreate?: InputMaybe<ReferenceFiltersInput>;
  and?: InputMaybe<Array<InputMaybe<AllUserFiltersInput>>>;
  chat_informations?: InputMaybe<ChatInformationFiltersInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  email?: InputMaybe<StringFilterInput>;
  exchanges?: InputMaybe<ExchangeFiltersInput>;
  grades?: InputMaybe<GradeFiltersInput>;
  groups?: InputMaybe<GroupFiltersInput>;
  id?: InputMaybe<IdFilterInput>;
  image_link?: InputMaybe<StringFilterInput>;
  job_matches?: InputMaybe<JobMatchFiltersInput>;
  job_review_responses?: InputMaybe<JobReviewResponseFiltersInput>;
  job_rubrics?: InputMaybe<JobRubricFiltersInput>;
  jobs?: InputMaybe<JobFiltersInput>;
  messages?: InputMaybe<MessageFiltersInput>;
  name?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<AllUserFiltersInput>;
  notification_statuses?: InputMaybe<NotificationStatusFiltersInput>;
  notifications?: InputMaybe<NotificationFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<AllUserFiltersInput>>>;
  profile_information?: InputMaybe<ProfileInformationFiltersInput>;
  references?: InputMaybe<ReferenceFiltersInput>;
  reviewer?: InputMaybe<ReviewerFiltersInput>;
  reviews?: InputMaybe<ReviewFiltersInput>;
  role?: InputMaybe<StringFilterInput>;
  smg_criteria?: InputMaybe<SmgCriterionFiltersInput>;
  smg_criterion_metrics?: InputMaybe<SmgCriterionMetricFiltersInput>;
  smg_metric_prompts?: InputMaybe<SmgMetricPromptFiltersInput>;
  smg_prompt_templates?: InputMaybe<SmgPromptTemplateFiltersInput>;
  smg_rubrics?: InputMaybe<SmgRubricFiltersInput>;
  tinder_user_profiles?: InputMaybe<TinderUserProfileFiltersInput>;
  tinder_user_reactions?: InputMaybe<TinderUserReactionFiltersInput>;
  trainee?: InputMaybe<TraineeFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  user?: InputMaybe<UsersPermissionsUserFiltersInput>;
};

export type AllUserInput = {
  Batch?: InputMaybe<Scalars['Int']['input']>;
  RefCreate?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  chat_informations?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  email?: InputMaybe<Scalars['String']['input']>;
  exchanges?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  grades?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  groups?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  image_link?: InputMaybe<Scalars['String']['input']>;
  job_matches?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  job_review_responses?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  job_rubrics?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  jobs?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  messages?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  name?: InputMaybe<Scalars['String']['input']>;
  notification_statuses?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  notifications?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  profile_information?: InputMaybe<Scalars['ID']['input']>;
  references?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  reviewer?: InputMaybe<Scalars['ID']['input']>;
  reviews?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  role?: InputMaybe<Enum_Alluser_Role>;
  smg_criteria?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  smg_criterion_metrics?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  smg_metric_prompts?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  smg_prompt_templates?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  smg_rubrics?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  tinder_user_profiles?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  tinder_user_reactions?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  trainee?: InputMaybe<Scalars['ID']['input']>;
  user?: InputMaybe<Scalars['ID']['input']>;
};

export type AllUserRelationResponseCollection = {
  __typename?: 'AllUserRelationResponseCollection';
  data: Array<AllUserEntity>;
};

export type Assignment = {
  __typename?: 'Assignment';
  assignment_category?: Maybe<AssignmentCategoryEntityResponse>;
  assignment_peer_gradings?: Maybe<AssignmentPeerGradingRelationResponseCollection>;
  assignment_responses?: Maybe<AssignmentResponseRelationResponseCollection>;
  assignment_submission_content: Scalars['JSON']['output'];
  assignment_type: Enum_Assignment_Assignment_Type;
  best_submissions?: Maybe<BestSubmissionRelationResponseCollection>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  gclass_submission_identifier: Scalars['JSON']['output'];
  repo?: Maybe<RepoEntityResponse>;
  smg_criterion_results?: Maybe<SmgCriterionResultRelationResponseCollection>;
  trainee?: Maybe<TraineeEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type AssignmentAssignment_Peer_GradingsArgs = {
  filters?: InputMaybe<AssignmentPeerGradingFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AssignmentAssignment_ResponsesArgs = {
  filters?: InputMaybe<AssignmentResponseFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AssignmentBest_SubmissionsArgs = {
  filters?: InputMaybe<BestSubmissionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AssignmentSmg_Criterion_ResultsArgs = {
  filters?: InputMaybe<SmgCriterionResultFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type AssignmentCategory = {
  __typename?: 'AssignmentCategory';
  assignments?: Maybe<AssignmentRelationResponseCollection>;
  batch?: Maybe<BatchEntityResponse>;
  best_submissions?: Maybe<BestSubmissionRelationResponseCollection>;
  challenge_sections?: Maybe<ChallengeSectionRelationResponseCollection>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  current_rubric?: Maybe<Scalars['String']['output']>;
  due_date?: Maybe<Scalars['DateTime']['output']>;
  form?: Maybe<FormEntityResponse>;
  name: Scalars['String']['output'];
  reviewers?: Maybe<ReviewerRelationResponseCollection>;
  rubric_type?: Maybe<Scalars['String']['output']>;
  rubrics?: Maybe<RubricRelationResponseCollection>;
  smg_rubrics?: Maybe<SmgRubricRelationResponseCollection>;
  status: Enum_Assignmentcategory_Status;
  topic: Scalars['String']['output'];
  total_mark: Scalars['Int']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type AssignmentCategoryAssignmentsArgs = {
  filters?: InputMaybe<AssignmentFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AssignmentCategoryBest_SubmissionsArgs = {
  filters?: InputMaybe<BestSubmissionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AssignmentCategoryChallenge_SectionsArgs = {
  filters?: InputMaybe<ChallengeSectionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AssignmentCategoryReviewersArgs = {
  filters?: InputMaybe<ReviewerFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AssignmentCategoryRubricsArgs = {
  filters?: InputMaybe<RubricFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type AssignmentCategorySmg_RubricsArgs = {
  filters?: InputMaybe<SmgRubricFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type AssignmentCategoryEntity = {
  __typename?: 'AssignmentCategoryEntity';
  attributes?: Maybe<AssignmentCategory>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type AssignmentCategoryEntityResponse = {
  __typename?: 'AssignmentCategoryEntityResponse';
  data?: Maybe<AssignmentCategoryEntity>;
};

export type AssignmentCategoryEntityResponseCollection = {
  __typename?: 'AssignmentCategoryEntityResponseCollection';
  data: Array<AssignmentCategoryEntity>;
  meta: ResponseCollectionMeta;
};

export type AssignmentCategoryFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<AssignmentCategoryFiltersInput>>>;
  assignments?: InputMaybe<AssignmentFiltersInput>;
  batch?: InputMaybe<BatchFiltersInput>;
  best_submissions?: InputMaybe<BestSubmissionFiltersInput>;
  challenge_sections?: InputMaybe<ChallengeSectionFiltersInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  current_rubric?: InputMaybe<StringFilterInput>;
  due_date?: InputMaybe<DateTimeFilterInput>;
  form?: InputMaybe<FormFiltersInput>;
  id?: InputMaybe<IdFilterInput>;
  name?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<AssignmentCategoryFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<AssignmentCategoryFiltersInput>>>;
  reviewers?: InputMaybe<ReviewerFiltersInput>;
  rubric_type?: InputMaybe<StringFilterInput>;
  rubrics?: InputMaybe<RubricFiltersInput>;
  smg_rubrics?: InputMaybe<SmgRubricFiltersInput>;
  status?: InputMaybe<StringFilterInput>;
  topic?: InputMaybe<StringFilterInput>;
  total_mark?: InputMaybe<IntFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type AssignmentCategoryInput = {
  assignments?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  batch?: InputMaybe<Scalars['ID']['input']>;
  best_submissions?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  challenge_sections?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  current_rubric?: InputMaybe<Scalars['String']['input']>;
  due_date?: InputMaybe<Scalars['DateTime']['input']>;
  form?: InputMaybe<Scalars['ID']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  reviewers?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  rubric_type?: InputMaybe<Scalars['String']['input']>;
  rubrics?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  smg_rubrics?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  status?: InputMaybe<Enum_Assignmentcategory_Status>;
  topic?: InputMaybe<Scalars['String']['input']>;
  total_mark?: InputMaybe<Scalars['Int']['input']>;
};

export type AssignmentCategoryRelationResponseCollection = {
  __typename?: 'AssignmentCategoryRelationResponseCollection';
  data: Array<AssignmentCategoryEntity>;
};

export type AssignmentEntity = {
  __typename?: 'AssignmentEntity';
  attributes?: Maybe<Assignment>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type AssignmentEntityResponse = {
  __typename?: 'AssignmentEntityResponse';
  data?: Maybe<AssignmentEntity>;
};

export type AssignmentEntityResponseCollection = {
  __typename?: 'AssignmentEntityResponseCollection';
  data: Array<AssignmentEntity>;
  meta: ResponseCollectionMeta;
};

export type AssignmentFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<AssignmentFiltersInput>>>;
  assignment_category?: InputMaybe<AssignmentCategoryFiltersInput>;
  assignment_peer_gradings?: InputMaybe<AssignmentPeerGradingFiltersInput>;
  assignment_responses?: InputMaybe<AssignmentResponseFiltersInput>;
  assignment_submission_content?: InputMaybe<JsonFilterInput>;
  assignment_type?: InputMaybe<StringFilterInput>;
  best_submissions?: InputMaybe<BestSubmissionFiltersInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  gclass_submission_identifier?: InputMaybe<JsonFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<AssignmentFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<AssignmentFiltersInput>>>;
  repo?: InputMaybe<RepoFiltersInput>;
  smg_criterion_results?: InputMaybe<SmgCriterionResultFiltersInput>;
  trainee?: InputMaybe<TraineeFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type AssignmentInput = {
  assignment_category?: InputMaybe<Scalars['ID']['input']>;
  assignment_peer_gradings?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  assignment_responses?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  assignment_submission_content?: InputMaybe<Scalars['JSON']['input']>;
  assignment_type?: InputMaybe<Enum_Assignment_Assignment_Type>;
  best_submissions?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  gclass_submission_identifier?: InputMaybe<Scalars['JSON']['input']>;
  repo?: InputMaybe<Scalars['ID']['input']>;
  smg_criterion_results?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  trainee?: InputMaybe<Scalars['ID']['input']>;
};

export type AssignmentPeerGrading = {
  __typename?: 'AssignmentPeerGrading';
  assignment?: Maybe<AssignmentEntityResponse>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  trainee?: Maybe<TraineeEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type AssignmentPeerGradingEntity = {
  __typename?: 'AssignmentPeerGradingEntity';
  attributes?: Maybe<AssignmentPeerGrading>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type AssignmentPeerGradingEntityResponse = {
  __typename?: 'AssignmentPeerGradingEntityResponse';
  data?: Maybe<AssignmentPeerGradingEntity>;
};

export type AssignmentPeerGradingEntityResponseCollection = {
  __typename?: 'AssignmentPeerGradingEntityResponseCollection';
  data: Array<AssignmentPeerGradingEntity>;
  meta: ResponseCollectionMeta;
};

export type AssignmentPeerGradingFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<AssignmentPeerGradingFiltersInput>>>;
  assignment?: InputMaybe<AssignmentFiltersInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<AssignmentPeerGradingFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<AssignmentPeerGradingFiltersInput>>>;
  trainee?: InputMaybe<TraineeFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type AssignmentPeerGradingInput = {
  assignment?: InputMaybe<Scalars['ID']['input']>;
  trainee?: InputMaybe<Scalars['ID']['input']>;
};

export type AssignmentPeerGradingRelationResponseCollection = {
  __typename?: 'AssignmentPeerGradingRelationResponseCollection';
  data: Array<AssignmentPeerGradingEntity>;
};

export type AssignmentRelationResponseCollection = {
  __typename?: 'AssignmentRelationResponseCollection';
  data: Array<AssignmentEntity>;
};

export type AssignmentResponse = {
  __typename?: 'AssignmentResponse';
  AdHoc?: Maybe<Scalars['JSON']['output']>;
  assignment?: Maybe<AssignmentEntityResponse>;
  content?: Maybe<Scalars['JSON']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  llm_response?: Maybe<Scalars['JSON']['output']>;
  mark: Scalars['Float']['output'];
  returned: Scalars['Boolean']['output'];
  reviewer?: Maybe<ReviewerEntityResponse>;
  rubric_id?: Maybe<Scalars['String']['output']>;
  rubric_status?: Maybe<Enum_Assignmentresponse_Rubric_Status>;
  rubric_type?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type AssignmentResponseEntity = {
  __typename?: 'AssignmentResponseEntity';
  attributes?: Maybe<AssignmentResponse>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type AssignmentResponseEntityResponse = {
  __typename?: 'AssignmentResponseEntityResponse';
  data?: Maybe<AssignmentResponseEntity>;
};

export type AssignmentResponseEntityResponseCollection = {
  __typename?: 'AssignmentResponseEntityResponseCollection';
  data: Array<AssignmentResponseEntity>;
  meta: ResponseCollectionMeta;
};

export type AssignmentResponseFiltersInput = {
  AdHoc?: InputMaybe<JsonFilterInput>;
  and?: InputMaybe<Array<InputMaybe<AssignmentResponseFiltersInput>>>;
  assignment?: InputMaybe<AssignmentFiltersInput>;
  content?: InputMaybe<JsonFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  llm_response?: InputMaybe<JsonFilterInput>;
  mark?: InputMaybe<FloatFilterInput>;
  not?: InputMaybe<AssignmentResponseFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<AssignmentResponseFiltersInput>>>;
  returned?: InputMaybe<BooleanFilterInput>;
  reviewer?: InputMaybe<ReviewerFiltersInput>;
  rubric_id?: InputMaybe<StringFilterInput>;
  rubric_status?: InputMaybe<StringFilterInput>;
  rubric_type?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type AssignmentResponseInput = {
  AdHoc?: InputMaybe<Scalars['JSON']['input']>;
  assignment?: InputMaybe<Scalars['ID']['input']>;
  content?: InputMaybe<Scalars['JSON']['input']>;
  llm_response?: InputMaybe<Scalars['JSON']['input']>;
  mark?: InputMaybe<Scalars['Float']['input']>;
  returned?: InputMaybe<Scalars['Boolean']['input']>;
  reviewer?: InputMaybe<Scalars['ID']['input']>;
  rubric_id?: InputMaybe<Scalars['String']['input']>;
  rubric_status?: InputMaybe<Enum_Assignmentresponse_Rubric_Status>;
  rubric_type?: InputMaybe<Scalars['String']['input']>;
};

export type AssignmentResponseRelationResponseCollection = {
  __typename?: 'AssignmentResponseRelationResponseCollection';
  data: Array<AssignmentResponseEntity>;
};

export type AssignmentSubmissionSummary = {
  __typename?: 'AssignmentSubmissionSummary';
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  late_submission?: Maybe<Scalars['Int']['output']>;
  missing_submission?: Maybe<Scalars['Int']['output']>;
  other_information?: Maybe<Scalars['JSON']['output']>;
  publishedAt?: Maybe<Scalars['DateTime']['output']>;
  rank: Scalars['String']['output'];
  total_assignment_per_week?: Maybe<Scalars['Int']['output']>;
  trainee?: Maybe<TraineeEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  week: Scalars['String']['output'];
};

export type AssignmentSubmissionSummaryEntity = {
  __typename?: 'AssignmentSubmissionSummaryEntity';
  attributes?: Maybe<AssignmentSubmissionSummary>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type AssignmentSubmissionSummaryEntityResponse = {
  __typename?: 'AssignmentSubmissionSummaryEntityResponse';
  data?: Maybe<AssignmentSubmissionSummaryEntity>;
};

export type AssignmentSubmissionSummaryEntityResponseCollection = {
  __typename?: 'AssignmentSubmissionSummaryEntityResponseCollection';
  data: Array<AssignmentSubmissionSummaryEntity>;
  meta: ResponseCollectionMeta;
};

export type AssignmentSubmissionSummaryFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<AssignmentSubmissionSummaryFiltersInput>>>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  late_submission?: InputMaybe<IntFilterInput>;
  missing_submission?: InputMaybe<IntFilterInput>;
  not?: InputMaybe<AssignmentSubmissionSummaryFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<AssignmentSubmissionSummaryFiltersInput>>>;
  other_information?: InputMaybe<JsonFilterInput>;
  publishedAt?: InputMaybe<DateTimeFilterInput>;
  rank?: InputMaybe<StringFilterInput>;
  total_assignment_per_week?: InputMaybe<IntFilterInput>;
  trainee?: InputMaybe<TraineeFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  week?: InputMaybe<StringFilterInput>;
};

export type AssignmentSubmissionSummaryInput = {
  late_submission?: InputMaybe<Scalars['Int']['input']>;
  missing_submission?: InputMaybe<Scalars['Int']['input']>;
  other_information?: InputMaybe<Scalars['JSON']['input']>;
  publishedAt?: InputMaybe<Scalars['DateTime']['input']>;
  rank?: InputMaybe<Scalars['String']['input']>;
  total_assignment_per_week?: InputMaybe<Scalars['Int']['input']>;
  trainee?: InputMaybe<Scalars['ID']['input']>;
  week?: InputMaybe<Scalars['String']['input']>;
};

export type AssignmentSubmissionSummaryRelationResponseCollection = {
  __typename?: 'AssignmentSubmissionSummaryRelationResponseCollection';
  data: Array<AssignmentSubmissionSummaryEntity>;
};

export type Batch = {
  __typename?: 'Batch';
  Batch: Scalars['Int']['output'];
  Class_link: Scalars['String']['output'];
  Communication_link: Scalars['String']['output'];
  additional_info?: Maybe<Scalars['JSON']['output']>;
  assignment_categories?: Maybe<AssignmentCategoryRelationResponseCollection>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  portfolios?: Maybe<PortfolioRelationResponseCollection>;
  reviewers?: Maybe<ReviewerRelationResponseCollection>;
  trainees?: Maybe<TraineeRelationResponseCollection>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type BatchAssignment_CategoriesArgs = {
  filters?: InputMaybe<AssignmentCategoryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type BatchPortfoliosArgs = {
  filters?: InputMaybe<PortfolioFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type BatchReviewersArgs = {
  filters?: InputMaybe<ReviewerFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type BatchTraineesArgs = {
  filters?: InputMaybe<TraineeFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type BatchCompetency = {
  __typename?: 'BatchCompetency';
  averageCompetency?: Maybe<Scalars['JSON']['output']>;
  batch?: Maybe<Scalars['Int']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  publishedAt?: Maybe<Scalars['DateTime']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  week?: Maybe<Scalars['String']['output']>;
};

export type BatchCompetencyEntity = {
  __typename?: 'BatchCompetencyEntity';
  attributes?: Maybe<BatchCompetency>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type BatchCompetencyEntityResponse = {
  __typename?: 'BatchCompetencyEntityResponse';
  data?: Maybe<BatchCompetencyEntity>;
};

export type BatchCompetencyEntityResponseCollection = {
  __typename?: 'BatchCompetencyEntityResponseCollection';
  data: Array<BatchCompetencyEntity>;
  meta: ResponseCollectionMeta;
};

export type BatchCompetencyFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<BatchCompetencyFiltersInput>>>;
  averageCompetency?: InputMaybe<JsonFilterInput>;
  batch?: InputMaybe<IntFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<BatchCompetencyFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<BatchCompetencyFiltersInput>>>;
  publishedAt?: InputMaybe<DateTimeFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  week?: InputMaybe<StringFilterInput>;
};

export type BatchCompetencyInput = {
  averageCompetency?: InputMaybe<Scalars['JSON']['input']>;
  batch?: InputMaybe<Scalars['Int']['input']>;
  publishedAt?: InputMaybe<Scalars['DateTime']['input']>;
  week?: InputMaybe<Scalars['String']['input']>;
};

export type BatchEntity = {
  __typename?: 'BatchEntity';
  attributes?: Maybe<Batch>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type BatchEntityResponse = {
  __typename?: 'BatchEntityResponse';
  data?: Maybe<BatchEntity>;
};

export type BatchEntityResponseCollection = {
  __typename?: 'BatchEntityResponseCollection';
  data: Array<BatchEntity>;
  meta: ResponseCollectionMeta;
};

export type BatchFiltersInput = {
  Batch?: InputMaybe<IntFilterInput>;
  Class_link?: InputMaybe<StringFilterInput>;
  Communication_link?: InputMaybe<StringFilterInput>;
  additional_info?: InputMaybe<JsonFilterInput>;
  and?: InputMaybe<Array<InputMaybe<BatchFiltersInput>>>;
  assignment_categories?: InputMaybe<AssignmentCategoryFiltersInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<BatchFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<BatchFiltersInput>>>;
  portfolios?: InputMaybe<PortfolioFiltersInput>;
  reviewers?: InputMaybe<ReviewerFiltersInput>;
  trainees?: InputMaybe<TraineeFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type BatchInput = {
  Batch?: InputMaybe<Scalars['Int']['input']>;
  Class_link?: InputMaybe<Scalars['String']['input']>;
  Communication_link?: InputMaybe<Scalars['String']['input']>;
  additional_info?: InputMaybe<Scalars['JSON']['input']>;
  assignment_categories?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  portfolios?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  reviewers?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  trainees?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
};

export type BatchRelationResponseCollection = {
  __typename?: 'BatchRelationResponseCollection';
  data: Array<BatchEntity>;
};

export type BestSubmission = {
  __typename?: 'BestSubmission';
  BestFor?: Maybe<Scalars['String']['output']>;
  Tag?: Maybe<Scalars['String']['output']>;
  assignment?: Maybe<AssignmentEntityResponse>;
  assignment_category?: Maybe<AssignmentCategoryEntityResponse>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  file: Scalars['JSON']['output'];
  reviewer?: Maybe<ReviewerEntityResponse>;
  star?: Maybe<Scalars['Int']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type BestSubmissionEntity = {
  __typename?: 'BestSubmissionEntity';
  attributes?: Maybe<BestSubmission>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type BestSubmissionEntityResponse = {
  __typename?: 'BestSubmissionEntityResponse';
  data?: Maybe<BestSubmissionEntity>;
};

export type BestSubmissionEntityResponseCollection = {
  __typename?: 'BestSubmissionEntityResponseCollection';
  data: Array<BestSubmissionEntity>;
  meta: ResponseCollectionMeta;
};

export type BestSubmissionFiltersInput = {
  BestFor?: InputMaybe<StringFilterInput>;
  Tag?: InputMaybe<StringFilterInput>;
  and?: InputMaybe<Array<InputMaybe<BestSubmissionFiltersInput>>>;
  assignment?: InputMaybe<AssignmentFiltersInput>;
  assignment_category?: InputMaybe<AssignmentCategoryFiltersInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  file?: InputMaybe<JsonFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<BestSubmissionFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<BestSubmissionFiltersInput>>>;
  reviewer?: InputMaybe<ReviewerFiltersInput>;
  star?: InputMaybe<IntFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type BestSubmissionInput = {
  BestFor?: InputMaybe<Scalars['String']['input']>;
  Tag?: InputMaybe<Scalars['String']['input']>;
  assignment?: InputMaybe<Scalars['ID']['input']>;
  assignment_category?: InputMaybe<Scalars['ID']['input']>;
  file?: InputMaybe<Scalars['JSON']['input']>;
  reviewer?: InputMaybe<Scalars['ID']['input']>;
  star?: InputMaybe<Scalars['Int']['input']>;
};

export type BestSubmissionRelationResponseCollection = {
  __typename?: 'BestSubmissionRelationResponseCollection';
  data: Array<BestSubmissionEntity>;
};

export type Blog = {
  __typename?: 'Blog';
  Image?: Maybe<UploadFileEntityResponse>;
  content?: Maybe<Scalars['String']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  creator?: Maybe<Scalars['String']['output']>;
  date?: Maybe<Scalars['Date']['output']>;
  description?: Maybe<Scalars['String']['output']>;
  priority: Scalars['Int']['output'];
  publishedAt?: Maybe<Scalars['DateTime']['output']>;
  title?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  urlSlug?: Maybe<Scalars['String']['output']>;
};

export type BlogEntity = {
  __typename?: 'BlogEntity';
  attributes?: Maybe<Blog>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type BlogEntityResponse = {
  __typename?: 'BlogEntityResponse';
  data?: Maybe<BlogEntity>;
};

export type BlogEntityResponseCollection = {
  __typename?: 'BlogEntityResponseCollection';
  data: Array<BlogEntity>;
  meta: ResponseCollectionMeta;
};

export type BlogFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<BlogFiltersInput>>>;
  content?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  creator?: InputMaybe<StringFilterInput>;
  date?: InputMaybe<DateFilterInput>;
  description?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<BlogFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<BlogFiltersInput>>>;
  priority?: InputMaybe<IntFilterInput>;
  publishedAt?: InputMaybe<DateTimeFilterInput>;
  title?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  urlSlug?: InputMaybe<StringFilterInput>;
};

export type BlogInput = {
  Image?: InputMaybe<Scalars['ID']['input']>;
  content?: InputMaybe<Scalars['String']['input']>;
  creator?: InputMaybe<Scalars['String']['input']>;
  date?: InputMaybe<Scalars['Date']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  priority?: InputMaybe<Scalars['Int']['input']>;
  publishedAt?: InputMaybe<Scalars['DateTime']['input']>;
  title?: InputMaybe<Scalars['String']['input']>;
  urlSlug?: InputMaybe<Scalars['String']['input']>;
};

export type BooleanFilterInput = {
  and?: InputMaybe<Array<InputMaybe<Scalars['Boolean']['input']>>>;
  between?: InputMaybe<Array<InputMaybe<Scalars['Boolean']['input']>>>;
  contains?: InputMaybe<Scalars['Boolean']['input']>;
  containsi?: InputMaybe<Scalars['Boolean']['input']>;
  endsWith?: InputMaybe<Scalars['Boolean']['input']>;
  eq?: InputMaybe<Scalars['Boolean']['input']>;
  gt?: InputMaybe<Scalars['Boolean']['input']>;
  gte?: InputMaybe<Scalars['Boolean']['input']>;
  in?: InputMaybe<Array<InputMaybe<Scalars['Boolean']['input']>>>;
  lt?: InputMaybe<Scalars['Boolean']['input']>;
  lte?: InputMaybe<Scalars['Boolean']['input']>;
  ne?: InputMaybe<Scalars['Boolean']['input']>;
  not?: InputMaybe<BooleanFilterInput>;
  notContains?: InputMaybe<Scalars['Boolean']['input']>;
  notContainsi?: InputMaybe<Scalars['Boolean']['input']>;
  notIn?: InputMaybe<Array<InputMaybe<Scalars['Boolean']['input']>>>;
  notNull?: InputMaybe<Scalars['Boolean']['input']>;
  null?: InputMaybe<Scalars['Boolean']['input']>;
  or?: InputMaybe<Array<InputMaybe<Scalars['Boolean']['input']>>>;
  startsWith?: InputMaybe<Scalars['Boolean']['input']>;
};

export type ChallengeDocument = {
  __typename?: 'ChallengeDocument';
  EndDate?: Maybe<Scalars['DateTime']['output']>;
  StartDate?: Maybe<Scalars['DateTime']['output']>;
  Status: Scalars['Boolean']['output'];
  Title: Scalars['String']['output'];
  batch?: Maybe<Scalars['Int']['output']>;
  challenge_sections?: Maybe<ChallengeSectionRelationResponseCollection>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  layout?: Maybe<Scalars['JSON']['output']>;
  reviewer?: Maybe<ReviewerEntityResponse>;
  slug: Scalars['String']['output'];
  subtitle?: Maybe<Scalars['String']['output']>;
  type?: Maybe<Enum_Challengedocument_Type>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  week: Scalars['String']['output'];
};


export type ChallengeDocumentChallenge_SectionsArgs = {
  filters?: InputMaybe<ChallengeSectionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type ChallengeDocumentEntity = {
  __typename?: 'ChallengeDocumentEntity';
  attributes?: Maybe<ChallengeDocument>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type ChallengeDocumentEntityResponse = {
  __typename?: 'ChallengeDocumentEntityResponse';
  data?: Maybe<ChallengeDocumentEntity>;
};

export type ChallengeDocumentEntityResponseCollection = {
  __typename?: 'ChallengeDocumentEntityResponseCollection';
  data: Array<ChallengeDocumentEntity>;
  meta: ResponseCollectionMeta;
};

export type ChallengeDocumentFiltersInput = {
  EndDate?: InputMaybe<DateTimeFilterInput>;
  StartDate?: InputMaybe<DateTimeFilterInput>;
  Status?: InputMaybe<BooleanFilterInput>;
  Title?: InputMaybe<StringFilterInput>;
  and?: InputMaybe<Array<InputMaybe<ChallengeDocumentFiltersInput>>>;
  batch?: InputMaybe<IntFilterInput>;
  challenge_sections?: InputMaybe<ChallengeSectionFiltersInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  layout?: InputMaybe<JsonFilterInput>;
  not?: InputMaybe<ChallengeDocumentFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<ChallengeDocumentFiltersInput>>>;
  reviewer?: InputMaybe<ReviewerFiltersInput>;
  slug?: InputMaybe<StringFilterInput>;
  subtitle?: InputMaybe<StringFilterInput>;
  type?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  week?: InputMaybe<StringFilterInput>;
};

export type ChallengeDocumentInput = {
  EndDate?: InputMaybe<Scalars['DateTime']['input']>;
  StartDate?: InputMaybe<Scalars['DateTime']['input']>;
  Status?: InputMaybe<Scalars['Boolean']['input']>;
  Title?: InputMaybe<Scalars['String']['input']>;
  batch?: InputMaybe<Scalars['Int']['input']>;
  challenge_sections?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  layout?: InputMaybe<Scalars['JSON']['input']>;
  reviewer?: InputMaybe<Scalars['ID']['input']>;
  slug?: InputMaybe<Scalars['String']['input']>;
  subtitle?: InputMaybe<Scalars['String']['input']>;
  type?: InputMaybe<Enum_Challengedocument_Type>;
  week?: InputMaybe<Scalars['String']['input']>;
};

export type ChallengeDocumentRelationResponseCollection = {
  __typename?: 'ChallengeDocumentRelationResponseCollection';
  data: Array<ChallengeDocumentEntity>;
};

export type ChallengeSection = {
  __typename?: 'ChallengeSection';
  EditHistory?: Maybe<Scalars['JSON']['output']>;
  Tag: Scalars['String']['output'];
  assignment_categories?: Maybe<AssignmentCategoryRelationResponseCollection>;
  challenge_documents?: Maybe<ChallengeDocumentRelationResponseCollection>;
  content?: Maybe<Scalars['JSON']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  hasFeedback?: Maybe<Scalars['Boolean']['output']>;
  references?: Maybe<ReferenceRelationResponseCollection>;
  reviewer?: Maybe<ReviewerEntityResponse>;
  slug: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type ChallengeSectionAssignment_CategoriesArgs = {
  filters?: InputMaybe<AssignmentCategoryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type ChallengeSectionChallenge_DocumentsArgs = {
  filters?: InputMaybe<ChallengeDocumentFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type ChallengeSectionReferencesArgs = {
  filters?: InputMaybe<ReferenceFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type ChallengeSectionEntity = {
  __typename?: 'ChallengeSectionEntity';
  attributes?: Maybe<ChallengeSection>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type ChallengeSectionEntityResponse = {
  __typename?: 'ChallengeSectionEntityResponse';
  data?: Maybe<ChallengeSectionEntity>;
};

export type ChallengeSectionEntityResponseCollection = {
  __typename?: 'ChallengeSectionEntityResponseCollection';
  data: Array<ChallengeSectionEntity>;
  meta: ResponseCollectionMeta;
};

export type ChallengeSectionFiltersInput = {
  EditHistory?: InputMaybe<JsonFilterInput>;
  Tag?: InputMaybe<StringFilterInput>;
  and?: InputMaybe<Array<InputMaybe<ChallengeSectionFiltersInput>>>;
  assignment_categories?: InputMaybe<AssignmentCategoryFiltersInput>;
  challenge_documents?: InputMaybe<ChallengeDocumentFiltersInput>;
  content?: InputMaybe<JsonFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  hasFeedback?: InputMaybe<BooleanFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<ChallengeSectionFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<ChallengeSectionFiltersInput>>>;
  references?: InputMaybe<ReferenceFiltersInput>;
  reviewer?: InputMaybe<ReviewerFiltersInput>;
  slug?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type ChallengeSectionInput = {
  EditHistory?: InputMaybe<Scalars['JSON']['input']>;
  Tag?: InputMaybe<Scalars['String']['input']>;
  assignment_categories?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  challenge_documents?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  content?: InputMaybe<Scalars['JSON']['input']>;
  hasFeedback?: InputMaybe<Scalars['Boolean']['input']>;
  references?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  reviewer?: InputMaybe<Scalars['ID']['input']>;
  slug?: InputMaybe<Scalars['String']['input']>;
};

export type ChallengeSectionRelationResponseCollection = {
  __typename?: 'ChallengeSectionRelationResponseCollection';
  data: Array<ChallengeSectionEntity>;
};

export type ChatInformation = {
  __typename?: 'ChatInformation';
  chat_info?: Maybe<AllUserEntityResponse>;
  com_score?: Maybe<Scalars['Float']['output']>;
  comm_rank?: Maybe<Scalars['String']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  message_rank: Scalars['String']['output'];
  publishedAt?: Maybe<Scalars['DateTime']['output']>;
  shared_link_rank: Scalars['String']['output'];
  total_mentions: Scalars['Int']['output'];
  total_message: Scalars['Int']['output'];
  total_shared_links?: Maybe<Scalars['Int']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  week: Scalars['String']['output'];
};

export type ChatInformationEntity = {
  __typename?: 'ChatInformationEntity';
  attributes?: Maybe<ChatInformation>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type ChatInformationEntityResponse = {
  __typename?: 'ChatInformationEntityResponse';
  data?: Maybe<ChatInformationEntity>;
};

export type ChatInformationEntityResponseCollection = {
  __typename?: 'ChatInformationEntityResponseCollection';
  data: Array<ChatInformationEntity>;
  meta: ResponseCollectionMeta;
};

export type ChatInformationFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<ChatInformationFiltersInput>>>;
  chat_info?: InputMaybe<AllUserFiltersInput>;
  com_score?: InputMaybe<FloatFilterInput>;
  comm_rank?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  message_rank?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<ChatInformationFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<ChatInformationFiltersInput>>>;
  publishedAt?: InputMaybe<DateTimeFilterInput>;
  shared_link_rank?: InputMaybe<StringFilterInput>;
  total_mentions?: InputMaybe<IntFilterInput>;
  total_message?: InputMaybe<IntFilterInput>;
  total_shared_links?: InputMaybe<IntFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  week?: InputMaybe<StringFilterInput>;
};

export type ChatInformationInput = {
  chat_info?: InputMaybe<Scalars['ID']['input']>;
  com_score?: InputMaybe<Scalars['Float']['input']>;
  comm_rank?: InputMaybe<Scalars['String']['input']>;
  message_rank?: InputMaybe<Scalars['String']['input']>;
  publishedAt?: InputMaybe<Scalars['DateTime']['input']>;
  shared_link_rank?: InputMaybe<Scalars['String']['input']>;
  total_mentions?: InputMaybe<Scalars['Int']['input']>;
  total_message?: InputMaybe<Scalars['Int']['input']>;
  total_shared_links?: InputMaybe<Scalars['Int']['input']>;
  week?: InputMaybe<Scalars['String']['input']>;
};

export type ChatInformationRelationResponseCollection = {
  __typename?: 'ChatInformationRelationResponseCollection';
  data: Array<ChatInformationEntity>;
};

export type DataDictionary = {
  __typename?: 'DataDictionary';
  applicationEmail: Scalars['String']['output'];
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  email: Scalars['String']['output'];
  familyName: Scalars['String']['output'];
  fullName: Scalars['String']['output'];
  gclassId: Scalars['String']['output'];
  givenName: Scalars['String']['output'];
  publishedAt?: Maybe<Scalars['DateTime']['output']>;
  slackId: Scalars['String']['output'];
  slackUName: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type DataDictionaryEntity = {
  __typename?: 'DataDictionaryEntity';
  attributes?: Maybe<DataDictionary>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type DataDictionaryEntityResponse = {
  __typename?: 'DataDictionaryEntityResponse';
  data?: Maybe<DataDictionaryEntity>;
};

export type DataDictionaryEntityResponseCollection = {
  __typename?: 'DataDictionaryEntityResponseCollection';
  data: Array<DataDictionaryEntity>;
  meta: ResponseCollectionMeta;
};

export type DataDictionaryFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<DataDictionaryFiltersInput>>>;
  applicationEmail?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  email?: InputMaybe<StringFilterInput>;
  familyName?: InputMaybe<StringFilterInput>;
  fullName?: InputMaybe<StringFilterInput>;
  gclassId?: InputMaybe<StringFilterInput>;
  givenName?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<DataDictionaryFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<DataDictionaryFiltersInput>>>;
  publishedAt?: InputMaybe<DateTimeFilterInput>;
  slackId?: InputMaybe<StringFilterInput>;
  slackUName?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type DataDictionaryInput = {
  applicationEmail?: InputMaybe<Scalars['String']['input']>;
  email?: InputMaybe<Scalars['String']['input']>;
  familyName?: InputMaybe<Scalars['String']['input']>;
  fullName?: InputMaybe<Scalars['String']['input']>;
  gclassId?: InputMaybe<Scalars['String']['input']>;
  givenName?: InputMaybe<Scalars['String']['input']>;
  publishedAt?: InputMaybe<Scalars['DateTime']['input']>;
  slackId?: InputMaybe<Scalars['String']['input']>;
  slackUName?: InputMaybe<Scalars['String']['input']>;
};

export type DateFilterInput = {
  and?: InputMaybe<Array<InputMaybe<Scalars['Date']['input']>>>;
  between?: InputMaybe<Array<InputMaybe<Scalars['Date']['input']>>>;
  contains?: InputMaybe<Scalars['Date']['input']>;
  containsi?: InputMaybe<Scalars['Date']['input']>;
  endsWith?: InputMaybe<Scalars['Date']['input']>;
  eq?: InputMaybe<Scalars['Date']['input']>;
  gt?: InputMaybe<Scalars['Date']['input']>;
  gte?: InputMaybe<Scalars['Date']['input']>;
  in?: InputMaybe<Array<InputMaybe<Scalars['Date']['input']>>>;
  lt?: InputMaybe<Scalars['Date']['input']>;
  lte?: InputMaybe<Scalars['Date']['input']>;
  ne?: InputMaybe<Scalars['Date']['input']>;
  not?: InputMaybe<DateFilterInput>;
  notContains?: InputMaybe<Scalars['Date']['input']>;
  notContainsi?: InputMaybe<Scalars['Date']['input']>;
  notIn?: InputMaybe<Array<InputMaybe<Scalars['Date']['input']>>>;
  notNull?: InputMaybe<Scalars['Boolean']['input']>;
  null?: InputMaybe<Scalars['Boolean']['input']>;
  or?: InputMaybe<Array<InputMaybe<Scalars['Date']['input']>>>;
  startsWith?: InputMaybe<Scalars['Date']['input']>;
};

export type DateTimeFilterInput = {
  and?: InputMaybe<Array<InputMaybe<Scalars['DateTime']['input']>>>;
  between?: InputMaybe<Array<InputMaybe<Scalars['DateTime']['input']>>>;
  contains?: InputMaybe<Scalars['DateTime']['input']>;
  containsi?: InputMaybe<Scalars['DateTime']['input']>;
  endsWith?: InputMaybe<Scalars['DateTime']['input']>;
  eq?: InputMaybe<Scalars['DateTime']['input']>;
  gt?: InputMaybe<Scalars['DateTime']['input']>;
  gte?: InputMaybe<Scalars['DateTime']['input']>;
  in?: InputMaybe<Array<InputMaybe<Scalars['DateTime']['input']>>>;
  lt?: InputMaybe<Scalars['DateTime']['input']>;
  lte?: InputMaybe<Scalars['DateTime']['input']>;
  ne?: InputMaybe<Scalars['DateTime']['input']>;
  not?: InputMaybe<DateTimeFilterInput>;
  notContains?: InputMaybe<Scalars['DateTime']['input']>;
  notContainsi?: InputMaybe<Scalars['DateTime']['input']>;
  notIn?: InputMaybe<Array<InputMaybe<Scalars['DateTime']['input']>>>;
  notNull?: InputMaybe<Scalars['Boolean']['input']>;
  null?: InputMaybe<Scalars['Boolean']['input']>;
  or?: InputMaybe<Array<InputMaybe<Scalars['DateTime']['input']>>>;
  startsWith?: InputMaybe<Scalars['DateTime']['input']>;
};

export enum Enum_Alluser_Role {
  Applicant = 'applicant',
  Staff = 'staff',
  Trainee = 'trainee'
}

export enum Enum_Assignmentcategory_Status {
  Completed = 'Completed',
  Done = 'Done',
  NotStarted = 'Not_started',
  Ongoing = 'Ongoing'
}

export enum Enum_Assignmentresponse_Rubric_Status {
  FullRubric = 'full_rubric',
  NoRubric = 'no_rubric',
  PartialRubric = 'partial_rubric'
}

export enum Enum_Assignment_Assignment_Type {
  Image = 'image',
  Link = 'link',
  Mixed = 'mixed',
  Other = 'other',
  Pdf = 'pdf',
  Video = 'video'
}

export enum Enum_Challengedocument_Type {
  NonTechnical = 'non_technical',
  Other = 'other',
  Technical = 'technical'
}

export enum Enum_Log_Action_Type {
  Login = 'login',
  Logout = 'logout',
  Other = 'other'
}

export enum Enum_Portfolio_Status {
  Available = 'available',
  Hired = 'hired'
}

export enum Enum_Reviewcategory_Review_Type {
  Evaluation = 'evaluation',
  Review = 'review',
  SelfEvaluation = 'self_evaluation'
}

export enum Enum_Reviewcategory_Status {
  Done = 'Done',
  NotStarted = 'Not_started',
  Ongoing = 'Ongoing'
}

export enum Enum_Tinderuserprofile_Credibility {
  Guessed = 'guessed',
  Inferred = 'inferred',
  SelfReported = 'self_reported',
  Unknown = 'unknown',
  Validated = 'validated'
}

export enum Enum_Tinderuserprofile_Profile_Type {
  Character = 'character',
  Competency = 'competency',
  Culture = 'culture',
  Hobby = 'hobby',
  Information = 'information',
  Language = 'language',
  Other = 'other',
  Preference = 'preference',
  Random = 'random'
}

export enum Enum_Tinderuserreaction_Overall_Reaction {
  HighlyInterested = 'highly_interested',
  Interested = 'interested',
  NotInterested = 'not_interested',
  NotThisAndAllLikeThis = 'not_this_and_all_like_this',
  NotThisButFits = 'not_this_but_fits'
}

export enum Enum_Trainee_Status {
  Accepted = 'Accepted',
  NotAccepted = 'Not_Accepted'
}

export type Exchange = {
  __typename?: 'Exchange';
  batch?: Maybe<Scalars['Int']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  messages?: Maybe<MessageRelationResponseCollection>;
  participants?: Maybe<AllUserRelationResponseCollection>;
  topic: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type ExchangeMessagesArgs = {
  filters?: InputMaybe<MessageFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type ExchangeParticipantsArgs = {
  filters?: InputMaybe<AllUserFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type ExchangeEntity = {
  __typename?: 'ExchangeEntity';
  attributes?: Maybe<Exchange>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type ExchangeEntityResponse = {
  __typename?: 'ExchangeEntityResponse';
  data?: Maybe<ExchangeEntity>;
};

export type ExchangeEntityResponseCollection = {
  __typename?: 'ExchangeEntityResponseCollection';
  data: Array<ExchangeEntity>;
  meta: ResponseCollectionMeta;
};

export type ExchangeFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<ExchangeFiltersInput>>>;
  batch?: InputMaybe<IntFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  messages?: InputMaybe<MessageFiltersInput>;
  not?: InputMaybe<ExchangeFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<ExchangeFiltersInput>>>;
  participants?: InputMaybe<AllUserFiltersInput>;
  topic?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type ExchangeInput = {
  batch?: InputMaybe<Scalars['Int']['input']>;
  messages?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  participants?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  topic?: InputMaybe<Scalars['String']['input']>;
};

export type ExchangeRelationResponseCollection = {
  __typename?: 'ExchangeRelationResponseCollection';
  data: Array<ExchangeEntity>;
};

export type FileInfoInput = {
  alternativeText?: InputMaybe<Scalars['String']['input']>;
  caption?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
};

export type FloatFilterInput = {
  and?: InputMaybe<Array<InputMaybe<Scalars['Float']['input']>>>;
  between?: InputMaybe<Array<InputMaybe<Scalars['Float']['input']>>>;
  contains?: InputMaybe<Scalars['Float']['input']>;
  containsi?: InputMaybe<Scalars['Float']['input']>;
  endsWith?: InputMaybe<Scalars['Float']['input']>;
  eq?: InputMaybe<Scalars['Float']['input']>;
  gt?: InputMaybe<Scalars['Float']['input']>;
  gte?: InputMaybe<Scalars['Float']['input']>;
  in?: InputMaybe<Array<InputMaybe<Scalars['Float']['input']>>>;
  lt?: InputMaybe<Scalars['Float']['input']>;
  lte?: InputMaybe<Scalars['Float']['input']>;
  ne?: InputMaybe<Scalars['Float']['input']>;
  not?: InputMaybe<FloatFilterInput>;
  notContains?: InputMaybe<Scalars['Float']['input']>;
  notContainsi?: InputMaybe<Scalars['Float']['input']>;
  notIn?: InputMaybe<Array<InputMaybe<Scalars['Float']['input']>>>;
  notNull?: InputMaybe<Scalars['Boolean']['input']>;
  null?: InputMaybe<Scalars['Boolean']['input']>;
  or?: InputMaybe<Array<InputMaybe<Scalars['Float']['input']>>>;
  startsWith?: InputMaybe<Scalars['Float']['input']>;
};

export type Form = {
  __typename?: 'Form';
  assignment_categories?: Maybe<AssignmentCategoryRelationResponseCollection>;
  content?: Maybe<Scalars['JSON']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  formType?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  review_categories?: Maybe<ReviewCategoryRelationResponseCollection>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type FormAssignment_CategoriesArgs = {
  filters?: InputMaybe<AssignmentCategoryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type FormReview_CategoriesArgs = {
  filters?: InputMaybe<ReviewCategoryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type FormEntity = {
  __typename?: 'FormEntity';
  attributes?: Maybe<Form>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type FormEntityResponse = {
  __typename?: 'FormEntityResponse';
  data?: Maybe<FormEntity>;
};

export type FormEntityResponseCollection = {
  __typename?: 'FormEntityResponseCollection';
  data: Array<FormEntity>;
  meta: ResponseCollectionMeta;
};

export type FormFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<FormFiltersInput>>>;
  assignment_categories?: InputMaybe<AssignmentCategoryFiltersInput>;
  content?: InputMaybe<JsonFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  formType?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  name?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<FormFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<FormFiltersInput>>>;
  review_categories?: InputMaybe<ReviewCategoryFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type FormInput = {
  assignment_categories?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  content?: InputMaybe<Scalars['JSON']['input']>;
  formType?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  review_categories?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
};

export type GenericMorph = AllUser | Assignment | AssignmentCategory | AssignmentPeerGrading | AssignmentResponse | AssignmentSubmissionSummary | Batch | BatchCompetency | BestSubmission | Blog | ChallengeDocument | ChallengeSection | ChatInformation | DataDictionary | Exchange | Form | GithubAnalysisDetail | GithubAnalysisSummary | GithubBranchCommitHistory | GithubReposMeta | GithubUserMeta | Gmeet | Grade | Group | I18NLocale | Job | JobAppliecationStatus | JobAsset | JobMatch | JobReviewResponse | JobRubric | JobTrainee | Log | Message | Notification | NotificationStatus | Portfolio | PortfolioGroup | Preference | ProfileInformation | PublicLog | Reference | Repo | Review | ReviewCategory | ReviewResponse | Reviewer | Rubric | SmgCriterion | SmgCriterionMetric | SmgCriterionResult | SmgDummyRubric | SmgMetricPrompt | SmgPromptTemplate | SmgRubric | TinderAssetGeneration | TinderJobProfile | TinderUserJobMatch | TinderUserProfile | TinderUserReaction | Trainee | UploadFile | UsersPermissionsPermission | UsersPermissionsRole | UsersPermissionsUser | WeekCompetency;

export type GithubAnalysisDetail = {
  __typename?: 'GithubAnalysisDetail';
  analysis_details: Scalars['JSON']['output'];
  batch: Scalars['Int']['output'];
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  repo?: Maybe<RepoEntityResponse>;
  run_number?: Maybe<Scalars['String']['output']>;
  trainee?: Maybe<TraineeEntityResponse>;
  trainee_id: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  week: Scalars['String']['output'];
};

export type GithubAnalysisDetailEntity = {
  __typename?: 'GithubAnalysisDetailEntity';
  attributes?: Maybe<GithubAnalysisDetail>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type GithubAnalysisDetailEntityResponse = {
  __typename?: 'GithubAnalysisDetailEntityResponse';
  data?: Maybe<GithubAnalysisDetailEntity>;
};

export type GithubAnalysisDetailEntityResponseCollection = {
  __typename?: 'GithubAnalysisDetailEntityResponseCollection';
  data: Array<GithubAnalysisDetailEntity>;
  meta: ResponseCollectionMeta;
};

export type GithubAnalysisDetailFiltersInput = {
  analysis_details?: InputMaybe<JsonFilterInput>;
  and?: InputMaybe<Array<InputMaybe<GithubAnalysisDetailFiltersInput>>>;
  batch?: InputMaybe<IntFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<GithubAnalysisDetailFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<GithubAnalysisDetailFiltersInput>>>;
  repo?: InputMaybe<RepoFiltersInput>;
  run_number?: InputMaybe<StringFilterInput>;
  trainee?: InputMaybe<TraineeFiltersInput>;
  trainee_id?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  week?: InputMaybe<StringFilterInput>;
};

export type GithubAnalysisDetailInput = {
  analysis_details?: InputMaybe<Scalars['JSON']['input']>;
  batch?: InputMaybe<Scalars['Int']['input']>;
  repo?: InputMaybe<Scalars['ID']['input']>;
  run_number?: InputMaybe<Scalars['String']['input']>;
  trainee?: InputMaybe<Scalars['ID']['input']>;
  trainee_id?: InputMaybe<Scalars['String']['input']>;
  week?: InputMaybe<Scalars['String']['input']>;
};

export type GithubAnalysisDetailRelationResponseCollection = {
  __typename?: 'GithubAnalysisDetailRelationResponseCollection';
  data: Array<GithubAnalysisDetailEntity>;
};

export type GithubAnalysisSummary = {
  __typename?: 'GithubAnalysisSummary';
  batch: Scalars['Int']['output'];
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  publishedAt?: Maybe<Scalars['DateTime']['output']>;
  run_number: Scalars['String']['output'];
  summary_details: Scalars['JSON']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  week: Scalars['String']['output'];
};

export type GithubAnalysisSummaryEntity = {
  __typename?: 'GithubAnalysisSummaryEntity';
  attributes?: Maybe<GithubAnalysisSummary>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type GithubAnalysisSummaryEntityResponse = {
  __typename?: 'GithubAnalysisSummaryEntityResponse';
  data?: Maybe<GithubAnalysisSummaryEntity>;
};

export type GithubAnalysisSummaryEntityResponseCollection = {
  __typename?: 'GithubAnalysisSummaryEntityResponseCollection';
  data: Array<GithubAnalysisSummaryEntity>;
  meta: ResponseCollectionMeta;
};

export type GithubAnalysisSummaryFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<GithubAnalysisSummaryFiltersInput>>>;
  batch?: InputMaybe<IntFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<GithubAnalysisSummaryFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<GithubAnalysisSummaryFiltersInput>>>;
  publishedAt?: InputMaybe<DateTimeFilterInput>;
  run_number?: InputMaybe<StringFilterInput>;
  summary_details?: InputMaybe<JsonFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  week?: InputMaybe<StringFilterInput>;
};

export type GithubAnalysisSummaryInput = {
  batch?: InputMaybe<Scalars['Int']['input']>;
  publishedAt?: InputMaybe<Scalars['DateTime']['input']>;
  run_number?: InputMaybe<Scalars['String']['input']>;
  summary_details?: InputMaybe<Scalars['JSON']['input']>;
  week?: InputMaybe<Scalars['String']['input']>;
};

export type GithubBranchCommitHistory = {
  __typename?: 'GithubBranchCommitHistory';
  branch: Scalars['String']['output'];
  commit_history: Scalars['JSON']['output'];
  commits_on_branch: Scalars['Int']['output'];
  commits_on_default_to_branch: Scalars['Int']['output'];
  contribution_counts: Scalars['JSON']['output'];
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  default_branch: Scalars['String']['output'];
  extras?: Maybe<Scalars['JSON']['output']>;
  file_level: Scalars['JSON']['output'];
  html_link: Scalars['String']['output'];
  num_contributors: Scalars['Int']['output'];
  repo?: Maybe<RepoEntityResponse>;
  repo_name: Scalars['String']['output'];
  run_number: Scalars['String']['output'];
  trainee?: Maybe<TraineeEntityResponse>;
  trainee_id: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  week: Scalars['String']['output'];
};

export type GithubBranchCommitHistoryEntity = {
  __typename?: 'GithubBranchCommitHistoryEntity';
  attributes?: Maybe<GithubBranchCommitHistory>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type GithubBranchCommitHistoryEntityResponse = {
  __typename?: 'GithubBranchCommitHistoryEntityResponse';
  data?: Maybe<GithubBranchCommitHistoryEntity>;
};

export type GithubBranchCommitHistoryEntityResponseCollection = {
  __typename?: 'GithubBranchCommitHistoryEntityResponseCollection';
  data: Array<GithubBranchCommitHistoryEntity>;
  meta: ResponseCollectionMeta;
};

export type GithubBranchCommitHistoryFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<GithubBranchCommitHistoryFiltersInput>>>;
  branch?: InputMaybe<StringFilterInput>;
  commit_history?: InputMaybe<JsonFilterInput>;
  commits_on_branch?: InputMaybe<IntFilterInput>;
  commits_on_default_to_branch?: InputMaybe<IntFilterInput>;
  contribution_counts?: InputMaybe<JsonFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  default_branch?: InputMaybe<StringFilterInput>;
  extras?: InputMaybe<JsonFilterInput>;
  file_level?: InputMaybe<JsonFilterInput>;
  html_link?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<GithubBranchCommitHistoryFiltersInput>;
  num_contributors?: InputMaybe<IntFilterInput>;
  or?: InputMaybe<Array<InputMaybe<GithubBranchCommitHistoryFiltersInput>>>;
  repo?: InputMaybe<RepoFiltersInput>;
  repo_name?: InputMaybe<StringFilterInput>;
  run_number?: InputMaybe<StringFilterInput>;
  trainee?: InputMaybe<TraineeFiltersInput>;
  trainee_id?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  week?: InputMaybe<StringFilterInput>;
};

export type GithubBranchCommitHistoryInput = {
  branch?: InputMaybe<Scalars['String']['input']>;
  commit_history?: InputMaybe<Scalars['JSON']['input']>;
  commits_on_branch?: InputMaybe<Scalars['Int']['input']>;
  commits_on_default_to_branch?: InputMaybe<Scalars['Int']['input']>;
  contribution_counts?: InputMaybe<Scalars['JSON']['input']>;
  default_branch?: InputMaybe<Scalars['String']['input']>;
  extras?: InputMaybe<Scalars['JSON']['input']>;
  file_level?: InputMaybe<Scalars['JSON']['input']>;
  html_link?: InputMaybe<Scalars['String']['input']>;
  num_contributors?: InputMaybe<Scalars['Int']['input']>;
  repo?: InputMaybe<Scalars['ID']['input']>;
  repo_name?: InputMaybe<Scalars['String']['input']>;
  run_number?: InputMaybe<Scalars['String']['input']>;
  trainee?: InputMaybe<Scalars['ID']['input']>;
  trainee_id?: InputMaybe<Scalars['String']['input']>;
  week?: InputMaybe<Scalars['String']['input']>;
};

export type GithubBranchCommitHistoryRelationResponseCollection = {
  __typename?: 'GithubBranchCommitHistoryRelationResponseCollection';
  data: Array<GithubBranchCommitHistoryEntity>;
};

export type GithubReposMeta = {
  __typename?: 'GithubReposMeta';
  branches: Scalars['Int']['output'];
  commit_stamp: Scalars['JSON']['output'];
  contributors: Scalars['JSON']['output'];
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  description?: Maybe<Scalars['String']['output']>;
  forks: Scalars['Int']['output'];
  html_url: Scalars['String']['output'];
  interested_files: Scalars['JSON']['output'];
  languages: Scalars['JSON']['output'];
  num_dirs: Scalars['Int']['output'];
  num_files: Scalars['Int']['output'];
  publishedAt?: Maybe<Scalars['DateTime']['output']>;
  repo?: Maybe<RepoEntityResponse>;
  repo_name: Scalars['String']['output'];
  run_number: Scalars['String']['output'];
  total_commits: Scalars['Int']['output'];
  trainee?: Maybe<TraineeEntityResponse>;
  trainee_id: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  week: Scalars['String']['output'];
};

export type GithubReposMetaEntity = {
  __typename?: 'GithubReposMetaEntity';
  attributes?: Maybe<GithubReposMeta>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type GithubReposMetaEntityResponse = {
  __typename?: 'GithubReposMetaEntityResponse';
  data?: Maybe<GithubReposMetaEntity>;
};

export type GithubReposMetaEntityResponseCollection = {
  __typename?: 'GithubReposMetaEntityResponseCollection';
  data: Array<GithubReposMetaEntity>;
  meta: ResponseCollectionMeta;
};

export type GithubReposMetaFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<GithubReposMetaFiltersInput>>>;
  branches?: InputMaybe<IntFilterInput>;
  commit_stamp?: InputMaybe<JsonFilterInput>;
  contributors?: InputMaybe<JsonFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  description?: InputMaybe<StringFilterInput>;
  forks?: InputMaybe<IntFilterInput>;
  html_url?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  interested_files?: InputMaybe<JsonFilterInput>;
  languages?: InputMaybe<JsonFilterInput>;
  not?: InputMaybe<GithubReposMetaFiltersInput>;
  num_dirs?: InputMaybe<IntFilterInput>;
  num_files?: InputMaybe<IntFilterInput>;
  or?: InputMaybe<Array<InputMaybe<GithubReposMetaFiltersInput>>>;
  publishedAt?: InputMaybe<DateTimeFilterInput>;
  repo?: InputMaybe<RepoFiltersInput>;
  repo_name?: InputMaybe<StringFilterInput>;
  run_number?: InputMaybe<StringFilterInput>;
  total_commits?: InputMaybe<IntFilterInput>;
  trainee?: InputMaybe<TraineeFiltersInput>;
  trainee_id?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  week?: InputMaybe<StringFilterInput>;
};

export type GithubReposMetaInput = {
  branches?: InputMaybe<Scalars['Int']['input']>;
  commit_stamp?: InputMaybe<Scalars['JSON']['input']>;
  contributors?: InputMaybe<Scalars['JSON']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  forks?: InputMaybe<Scalars['Int']['input']>;
  html_url?: InputMaybe<Scalars['String']['input']>;
  interested_files?: InputMaybe<Scalars['JSON']['input']>;
  languages?: InputMaybe<Scalars['JSON']['input']>;
  num_dirs?: InputMaybe<Scalars['Int']['input']>;
  num_files?: InputMaybe<Scalars['Int']['input']>;
  publishedAt?: InputMaybe<Scalars['DateTime']['input']>;
  repo?: InputMaybe<Scalars['ID']['input']>;
  repo_name?: InputMaybe<Scalars['String']['input']>;
  run_number?: InputMaybe<Scalars['String']['input']>;
  total_commits?: InputMaybe<Scalars['Int']['input']>;
  trainee?: InputMaybe<Scalars['ID']['input']>;
  trainee_id?: InputMaybe<Scalars['String']['input']>;
  week?: InputMaybe<Scalars['String']['input']>;
};

export type GithubReposMetaRelationResponseCollection = {
  __typename?: 'GithubReposMetaRelationResponseCollection';
  data: Array<GithubReposMetaEntity>;
};

export type GithubUserMeta = {
  __typename?: 'GithubUserMeta';
  avatar_url: Scalars['String']['output'];
  bio?: Maybe<Scalars['String']['output']>;
  commits: Scalars['Int']['output'];
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  email?: Maybe<Scalars['String']['output']>;
  followers: Scalars['Int']['output'];
  following: Scalars['Int']['output'];
  html_url: Scalars['String']['output'];
  issues: Scalars['Int']['output'];
  name: Scalars['String']['output'];
  public_repos: Scalars['Int']['output'];
  publishedAt?: Maybe<Scalars['DateTime']['output']>;
  pull_requests: Scalars['Int']['output'];
  repo?: Maybe<RepoEntityResponse>;
  run_number: Scalars['String']['output'];
  trainee?: Maybe<TraineeEntityResponse>;
  trainee_id: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  week: Scalars['String']['output'];
};

export type GithubUserMetaEntity = {
  __typename?: 'GithubUserMetaEntity';
  attributes?: Maybe<GithubUserMeta>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type GithubUserMetaEntityResponse = {
  __typename?: 'GithubUserMetaEntityResponse';
  data?: Maybe<GithubUserMetaEntity>;
};

export type GithubUserMetaEntityResponseCollection = {
  __typename?: 'GithubUserMetaEntityResponseCollection';
  data: Array<GithubUserMetaEntity>;
  meta: ResponseCollectionMeta;
};

export type GithubUserMetaFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<GithubUserMetaFiltersInput>>>;
  avatar_url?: InputMaybe<StringFilterInput>;
  bio?: InputMaybe<StringFilterInput>;
  commits?: InputMaybe<IntFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  email?: InputMaybe<StringFilterInput>;
  followers?: InputMaybe<IntFilterInput>;
  following?: InputMaybe<IntFilterInput>;
  html_url?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  issues?: InputMaybe<IntFilterInput>;
  name?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<GithubUserMetaFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<GithubUserMetaFiltersInput>>>;
  public_repos?: InputMaybe<IntFilterInput>;
  publishedAt?: InputMaybe<DateTimeFilterInput>;
  pull_requests?: InputMaybe<IntFilterInput>;
  repo?: InputMaybe<RepoFiltersInput>;
  run_number?: InputMaybe<StringFilterInput>;
  trainee?: InputMaybe<TraineeFiltersInput>;
  trainee_id?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  week?: InputMaybe<StringFilterInput>;
};

export type GithubUserMetaInput = {
  avatar_url?: InputMaybe<Scalars['String']['input']>;
  bio?: InputMaybe<Scalars['String']['input']>;
  commits?: InputMaybe<Scalars['Int']['input']>;
  email?: InputMaybe<Scalars['String']['input']>;
  followers?: InputMaybe<Scalars['Int']['input']>;
  following?: InputMaybe<Scalars['Int']['input']>;
  html_url?: InputMaybe<Scalars['String']['input']>;
  issues?: InputMaybe<Scalars['Int']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  public_repos?: InputMaybe<Scalars['Int']['input']>;
  publishedAt?: InputMaybe<Scalars['DateTime']['input']>;
  pull_requests?: InputMaybe<Scalars['Int']['input']>;
  repo?: InputMaybe<Scalars['ID']['input']>;
  run_number?: InputMaybe<Scalars['String']['input']>;
  trainee?: InputMaybe<Scalars['ID']['input']>;
  trainee_id?: InputMaybe<Scalars['String']['input']>;
  week?: InputMaybe<Scalars['String']['input']>;
};

export type GithubUserMetaRelationResponseCollection = {
  __typename?: 'GithubUserMetaRelationResponseCollection';
  data: Array<GithubUserMetaEntity>;
};

export type Gmeet = {
  __typename?: 'Gmeet';
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  number_days?: Maybe<Scalars['Int']['output']>;
  publishedAt?: Maybe<Scalars['DateTime']['output']>;
  rank: Scalars['String']['output'];
  trainee?: Maybe<TraineeEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  week: Scalars['String']['output'];
  week_detail: Scalars['JSON']['output'];
};

export type GmeetEntity = {
  __typename?: 'GmeetEntity';
  attributes?: Maybe<Gmeet>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type GmeetEntityResponse = {
  __typename?: 'GmeetEntityResponse';
  data?: Maybe<GmeetEntity>;
};

export type GmeetEntityResponseCollection = {
  __typename?: 'GmeetEntityResponseCollection';
  data: Array<GmeetEntity>;
  meta: ResponseCollectionMeta;
};

export type GmeetFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<GmeetFiltersInput>>>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<GmeetFiltersInput>;
  number_days?: InputMaybe<IntFilterInput>;
  or?: InputMaybe<Array<InputMaybe<GmeetFiltersInput>>>;
  publishedAt?: InputMaybe<DateTimeFilterInput>;
  rank?: InputMaybe<StringFilterInput>;
  trainee?: InputMaybe<TraineeFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  week?: InputMaybe<StringFilterInput>;
  week_detail?: InputMaybe<JsonFilterInput>;
};

export type GmeetInput = {
  number_days?: InputMaybe<Scalars['Int']['input']>;
  publishedAt?: InputMaybe<Scalars['DateTime']['input']>;
  rank?: InputMaybe<Scalars['String']['input']>;
  trainee?: InputMaybe<Scalars['ID']['input']>;
  week?: InputMaybe<Scalars['String']['input']>;
  week_detail?: InputMaybe<Scalars['JSON']['input']>;
};

export type GmeetRelationResponseCollection = {
  __typename?: 'GmeetRelationResponseCollection';
  data: Array<GmeetEntity>;
};

export type Grade = {
  __typename?: 'Grade';
  all_user?: Maybe<AllUserEntityResponse>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  label: Scalars['String']['output'];
  review?: Maybe<ReviewEntityResponse>;
  score: Scalars['Int']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type GradeEntity = {
  __typename?: 'GradeEntity';
  attributes?: Maybe<Grade>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type GradeEntityResponse = {
  __typename?: 'GradeEntityResponse';
  data?: Maybe<GradeEntity>;
};

export type GradeEntityResponseCollection = {
  __typename?: 'GradeEntityResponseCollection';
  data: Array<GradeEntity>;
  meta: ResponseCollectionMeta;
};

export type GradeFiltersInput = {
  all_user?: InputMaybe<AllUserFiltersInput>;
  and?: InputMaybe<Array<InputMaybe<GradeFiltersInput>>>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  label?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<GradeFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<GradeFiltersInput>>>;
  review?: InputMaybe<ReviewFiltersInput>;
  score?: InputMaybe<IntFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type GradeInput = {
  all_user?: InputMaybe<Scalars['ID']['input']>;
  label?: InputMaybe<Scalars['String']['input']>;
  review?: InputMaybe<Scalars['ID']['input']>;
  score?: InputMaybe<Scalars['Int']['input']>;
};

export type GradeRelationResponseCollection = {
  __typename?: 'GradeRelationResponseCollection';
  data: Array<GradeEntity>;
};

export type Group = {
  __typename?: 'Group';
  Name: Scalars['String']['output'];
  all_users?: Maybe<AllUserRelationResponseCollection>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  notifications?: Maybe<NotificationRelationResponseCollection>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type GroupAll_UsersArgs = {
  filters?: InputMaybe<AllUserFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type GroupNotificationsArgs = {
  filters?: InputMaybe<NotificationFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type GroupEntity = {
  __typename?: 'GroupEntity';
  attributes?: Maybe<Group>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type GroupEntityResponse = {
  __typename?: 'GroupEntityResponse';
  data?: Maybe<GroupEntity>;
};

export type GroupEntityResponseCollection = {
  __typename?: 'GroupEntityResponseCollection';
  data: Array<GroupEntity>;
  meta: ResponseCollectionMeta;
};

export type GroupFiltersInput = {
  Name?: InputMaybe<StringFilterInput>;
  all_users?: InputMaybe<AllUserFiltersInput>;
  and?: InputMaybe<Array<InputMaybe<GroupFiltersInput>>>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<GroupFiltersInput>;
  notifications?: InputMaybe<NotificationFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<GroupFiltersInput>>>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type GroupInput = {
  Name?: InputMaybe<Scalars['String']['input']>;
  all_users?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  notifications?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
};

export type GroupRelationResponseCollection = {
  __typename?: 'GroupRelationResponseCollection';
  data: Array<GroupEntity>;
};

export type I18NLocale = {
  __typename?: 'I18NLocale';
  code?: Maybe<Scalars['String']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  name?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type I18NLocaleEntity = {
  __typename?: 'I18NLocaleEntity';
  attributes?: Maybe<I18NLocale>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type I18NLocaleEntityResponse = {
  __typename?: 'I18NLocaleEntityResponse';
  data?: Maybe<I18NLocaleEntity>;
};

export type I18NLocaleEntityResponseCollection = {
  __typename?: 'I18NLocaleEntityResponseCollection';
  data: Array<I18NLocaleEntity>;
  meta: ResponseCollectionMeta;
};

export type I18NLocaleFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<I18NLocaleFiltersInput>>>;
  code?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  name?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<I18NLocaleFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<I18NLocaleFiltersInput>>>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type IdFilterInput = {
  and?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  between?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  contains?: InputMaybe<Scalars['ID']['input']>;
  containsi?: InputMaybe<Scalars['ID']['input']>;
  endsWith?: InputMaybe<Scalars['ID']['input']>;
  eq?: InputMaybe<Scalars['ID']['input']>;
  gt?: InputMaybe<Scalars['ID']['input']>;
  gte?: InputMaybe<Scalars['ID']['input']>;
  in?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  lt?: InputMaybe<Scalars['ID']['input']>;
  lte?: InputMaybe<Scalars['ID']['input']>;
  ne?: InputMaybe<Scalars['ID']['input']>;
  not?: InputMaybe<IdFilterInput>;
  notContains?: InputMaybe<Scalars['ID']['input']>;
  notContainsi?: InputMaybe<Scalars['ID']['input']>;
  notIn?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  notNull?: InputMaybe<Scalars['Boolean']['input']>;
  null?: InputMaybe<Scalars['Boolean']['input']>;
  or?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  startsWith?: InputMaybe<Scalars['ID']['input']>;
};

export type IntFilterInput = {
  and?: InputMaybe<Array<InputMaybe<Scalars['Int']['input']>>>;
  between?: InputMaybe<Array<InputMaybe<Scalars['Int']['input']>>>;
  contains?: InputMaybe<Scalars['Int']['input']>;
  containsi?: InputMaybe<Scalars['Int']['input']>;
  endsWith?: InputMaybe<Scalars['Int']['input']>;
  eq?: InputMaybe<Scalars['Int']['input']>;
  gt?: InputMaybe<Scalars['Int']['input']>;
  gte?: InputMaybe<Scalars['Int']['input']>;
  in?: InputMaybe<Array<InputMaybe<Scalars['Int']['input']>>>;
  lt?: InputMaybe<Scalars['Int']['input']>;
  lte?: InputMaybe<Scalars['Int']['input']>;
  ne?: InputMaybe<Scalars['Int']['input']>;
  not?: InputMaybe<IntFilterInput>;
  notContains?: InputMaybe<Scalars['Int']['input']>;
  notContainsi?: InputMaybe<Scalars['Int']['input']>;
  notIn?: InputMaybe<Array<InputMaybe<Scalars['Int']['input']>>>;
  notNull?: InputMaybe<Scalars['Boolean']['input']>;
  null?: InputMaybe<Scalars['Boolean']['input']>;
  or?: InputMaybe<Array<InputMaybe<Scalars['Int']['input']>>>;
  startsWith?: InputMaybe<Scalars['Int']['input']>;
};

export type JsonFilterInput = {
  and?: InputMaybe<Array<InputMaybe<Scalars['JSON']['input']>>>;
  between?: InputMaybe<Array<InputMaybe<Scalars['JSON']['input']>>>;
  contains?: InputMaybe<Scalars['JSON']['input']>;
  containsi?: InputMaybe<Scalars['JSON']['input']>;
  endsWith?: InputMaybe<Scalars['JSON']['input']>;
  eq?: InputMaybe<Scalars['JSON']['input']>;
  gt?: InputMaybe<Scalars['JSON']['input']>;
  gte?: InputMaybe<Scalars['JSON']['input']>;
  in?: InputMaybe<Array<InputMaybe<Scalars['JSON']['input']>>>;
  lt?: InputMaybe<Scalars['JSON']['input']>;
  lte?: InputMaybe<Scalars['JSON']['input']>;
  ne?: InputMaybe<Scalars['JSON']['input']>;
  not?: InputMaybe<JsonFilterInput>;
  notContains?: InputMaybe<Scalars['JSON']['input']>;
  notContainsi?: InputMaybe<Scalars['JSON']['input']>;
  notIn?: InputMaybe<Array<InputMaybe<Scalars['JSON']['input']>>>;
  notNull?: InputMaybe<Scalars['Boolean']['input']>;
  null?: InputMaybe<Scalars['Boolean']['input']>;
  or?: InputMaybe<Array<InputMaybe<Scalars['JSON']['input']>>>;
  startsWith?: InputMaybe<Scalars['JSON']['input']>;
};

export type Job = {
  __typename?: 'Job';
  Platform?: Maybe<Scalars['String']['output']>;
  Role?: Maybe<Scalars['String']['output']>;
  additionalInfo?: Maybe<Scalars['JSON']['output']>;
  closingDate?: Maybe<Scalars['DateTime']['output']>;
  companyName: Scalars['String']['output'];
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  creator?: Maybe<AllUserEntityResponse>;
  description?: Maybe<Scalars['String']['output']>;
  job_matches?: Maybe<JobMatchRelationResponseCollection>;
  job_trainees?: Maybe<JobTraineeRelationResponseCollection>;
  link?: Maybe<Scalars['String']['output']>;
  openDate?: Maybe<Scalars['DateTime']['output']>;
  slug?: Maybe<Scalars['String']['output']>;
  tinder_job_profiles?: Maybe<TinderJobProfileRelationResponseCollection>;
  title?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type JobJob_MatchesArgs = {
  filters?: InputMaybe<JobMatchFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type JobJob_TraineesArgs = {
  filters?: InputMaybe<JobTraineeFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type JobTinder_Job_ProfilesArgs = {
  filters?: InputMaybe<TinderJobProfileFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type JobAppliecationStatus = {
  __typename?: 'JobAppliecationStatus';
  Description?: Maybe<Scalars['String']['output']>;
  Name?: Maybe<Scalars['String']['output']>;
  additionalInfo?: Maybe<Scalars['JSON']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  job_trainee?: Maybe<JobTraineeEntityResponse>;
  slug?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type JobAppliecationStatusEntity = {
  __typename?: 'JobAppliecationStatusEntity';
  attributes?: Maybe<JobAppliecationStatus>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type JobAppliecationStatusEntityResponse = {
  __typename?: 'JobAppliecationStatusEntityResponse';
  data?: Maybe<JobAppliecationStatusEntity>;
};

export type JobAppliecationStatusEntityResponseCollection = {
  __typename?: 'JobAppliecationStatusEntityResponseCollection';
  data: Array<JobAppliecationStatusEntity>;
  meta: ResponseCollectionMeta;
};

export type JobAppliecationStatusFiltersInput = {
  Description?: InputMaybe<StringFilterInput>;
  Name?: InputMaybe<StringFilterInput>;
  additionalInfo?: InputMaybe<JsonFilterInput>;
  and?: InputMaybe<Array<InputMaybe<JobAppliecationStatusFiltersInput>>>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  job_trainee?: InputMaybe<JobTraineeFiltersInput>;
  not?: InputMaybe<JobAppliecationStatusFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<JobAppliecationStatusFiltersInput>>>;
  slug?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type JobAppliecationStatusInput = {
  Description?: InputMaybe<Scalars['String']['input']>;
  Name?: InputMaybe<Scalars['String']['input']>;
  additionalInfo?: InputMaybe<Scalars['JSON']['input']>;
  job_trainee?: InputMaybe<Scalars['ID']['input']>;
  slug?: InputMaybe<Scalars['String']['input']>;
};

export type JobAppliecationStatusRelationResponseCollection = {
  __typename?: 'JobAppliecationStatusRelationResponseCollection';
  data: Array<JobAppliecationStatusEntity>;
};

export type JobAsset = {
  __typename?: 'JobAsset';
  EditHistory?: Maybe<Scalars['JSON']['output']>;
  additionalInfo?: Maybe<Scalars['JSON']['output']>;
  content?: Maybe<Scalars['JSON']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  job_trainees?: Maybe<JobTraineeRelationResponseCollection>;
  name?: Maybe<Scalars['String']['output']>;
  slug?: Maybe<Scalars['String']['output']>;
  trainee?: Maybe<TraineeEntityResponse>;
  type?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  uploadedFile?: Maybe<UploadFileEntityResponse>;
};


export type JobAssetJob_TraineesArgs = {
  filters?: InputMaybe<JobTraineeFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type JobAssetEntity = {
  __typename?: 'JobAssetEntity';
  attributes?: Maybe<JobAsset>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type JobAssetEntityResponse = {
  __typename?: 'JobAssetEntityResponse';
  data?: Maybe<JobAssetEntity>;
};

export type JobAssetEntityResponseCollection = {
  __typename?: 'JobAssetEntityResponseCollection';
  data: Array<JobAssetEntity>;
  meta: ResponseCollectionMeta;
};

export type JobAssetFiltersInput = {
  EditHistory?: InputMaybe<JsonFilterInput>;
  additionalInfo?: InputMaybe<JsonFilterInput>;
  and?: InputMaybe<Array<InputMaybe<JobAssetFiltersInput>>>;
  content?: InputMaybe<JsonFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  job_trainees?: InputMaybe<JobTraineeFiltersInput>;
  name?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<JobAssetFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<JobAssetFiltersInput>>>;
  slug?: InputMaybe<StringFilterInput>;
  trainee?: InputMaybe<TraineeFiltersInput>;
  type?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type JobAssetInput = {
  EditHistory?: InputMaybe<Scalars['JSON']['input']>;
  additionalInfo?: InputMaybe<Scalars['JSON']['input']>;
  content?: InputMaybe<Scalars['JSON']['input']>;
  job_trainees?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  name?: InputMaybe<Scalars['String']['input']>;
  slug?: InputMaybe<Scalars['String']['input']>;
  trainee?: InputMaybe<Scalars['ID']['input']>;
  type?: InputMaybe<Scalars['String']['input']>;
  uploadedFile?: InputMaybe<Scalars['ID']['input']>;
};

export type JobAssetRelationResponseCollection = {
  __typename?: 'JobAssetRelationResponseCollection';
  data: Array<JobAssetEntity>;
};

export type JobEntity = {
  __typename?: 'JobEntity';
  attributes?: Maybe<Job>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type JobEntityResponse = {
  __typename?: 'JobEntityResponse';
  data?: Maybe<JobEntity>;
};

export type JobEntityResponseCollection = {
  __typename?: 'JobEntityResponseCollection';
  data: Array<JobEntity>;
  meta: ResponseCollectionMeta;
};

export type JobFiltersInput = {
  Platform?: InputMaybe<StringFilterInput>;
  Role?: InputMaybe<StringFilterInput>;
  additionalInfo?: InputMaybe<JsonFilterInput>;
  and?: InputMaybe<Array<InputMaybe<JobFiltersInput>>>;
  closingDate?: InputMaybe<DateTimeFilterInput>;
  companyName?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  creator?: InputMaybe<AllUserFiltersInput>;
  description?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  job_matches?: InputMaybe<JobMatchFiltersInput>;
  job_trainees?: InputMaybe<JobTraineeFiltersInput>;
  link?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<JobFiltersInput>;
  openDate?: InputMaybe<DateTimeFilterInput>;
  or?: InputMaybe<Array<InputMaybe<JobFiltersInput>>>;
  slug?: InputMaybe<StringFilterInput>;
  tinder_job_profiles?: InputMaybe<TinderJobProfileFiltersInput>;
  title?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type JobInput = {
  Platform?: InputMaybe<Scalars['String']['input']>;
  Role?: InputMaybe<Scalars['String']['input']>;
  additionalInfo?: InputMaybe<Scalars['JSON']['input']>;
  closingDate?: InputMaybe<Scalars['DateTime']['input']>;
  companyName?: InputMaybe<Scalars['String']['input']>;
  creator?: InputMaybe<Scalars['ID']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  job_matches?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  job_trainees?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  link?: InputMaybe<Scalars['String']['input']>;
  openDate?: InputMaybe<Scalars['DateTime']['input']>;
  slug?: InputMaybe<Scalars['String']['input']>;
  tinder_job_profiles?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  title?: InputMaybe<Scalars['String']['input']>;
};

export type JobMatch = {
  __typename?: 'JobMatch';
  Applied?: Maybe<Scalars['Boolean']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  creator?: Maybe<AllUserEntityResponse>;
  job?: Maybe<JobEntityResponse>;
  reson?: Maybe<Scalars['JSON']['output']>;
  slug?: Maybe<Scalars['String']['output']>;
  tag?: Maybe<Scalars['String']['output']>;
  trainee?: Maybe<TraineeEntityResponse>;
  type?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type JobMatchEntity = {
  __typename?: 'JobMatchEntity';
  attributes?: Maybe<JobMatch>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type JobMatchEntityResponse = {
  __typename?: 'JobMatchEntityResponse';
  data?: Maybe<JobMatchEntity>;
};

export type JobMatchEntityResponseCollection = {
  __typename?: 'JobMatchEntityResponseCollection';
  data: Array<JobMatchEntity>;
  meta: ResponseCollectionMeta;
};

export type JobMatchFiltersInput = {
  Applied?: InputMaybe<BooleanFilterInput>;
  and?: InputMaybe<Array<InputMaybe<JobMatchFiltersInput>>>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  creator?: InputMaybe<AllUserFiltersInput>;
  id?: InputMaybe<IdFilterInput>;
  job?: InputMaybe<JobFiltersInput>;
  not?: InputMaybe<JobMatchFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<JobMatchFiltersInput>>>;
  reson?: InputMaybe<JsonFilterInput>;
  slug?: InputMaybe<StringFilterInput>;
  tag?: InputMaybe<StringFilterInput>;
  trainee?: InputMaybe<TraineeFiltersInput>;
  type?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type JobMatchInput = {
  Applied?: InputMaybe<Scalars['Boolean']['input']>;
  creator?: InputMaybe<Scalars['ID']['input']>;
  job?: InputMaybe<Scalars['ID']['input']>;
  reson?: InputMaybe<Scalars['JSON']['input']>;
  slug?: InputMaybe<Scalars['String']['input']>;
  tag?: InputMaybe<Scalars['String']['input']>;
  trainee?: InputMaybe<Scalars['ID']['input']>;
  type?: InputMaybe<Scalars['String']['input']>;
};

export type JobMatchRelationResponseCollection = {
  __typename?: 'JobMatchRelationResponseCollection';
  data: Array<JobMatchEntity>;
};

export type JobRelationResponseCollection = {
  __typename?: 'JobRelationResponseCollection';
  data: Array<JobEntity>;
};

export type JobReviewResponse = {
  __typename?: 'JobReviewResponse';
  AdHoc?: Maybe<Scalars['JSON']['output']>;
  all_user?: Maybe<AllUserEntityResponse>;
  by?: Maybe<Scalars['String']['output']>;
  content?: Maybe<Scalars['JSON']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  job_trainees?: Maybe<JobTraineeRelationResponseCollection>;
  mark?: Maybe<Scalars['Int']['output']>;
  rubric_id: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type JobReviewResponseJob_TraineesArgs = {
  filters?: InputMaybe<JobTraineeFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type JobReviewResponseEntity = {
  __typename?: 'JobReviewResponseEntity';
  attributes?: Maybe<JobReviewResponse>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type JobReviewResponseEntityResponse = {
  __typename?: 'JobReviewResponseEntityResponse';
  data?: Maybe<JobReviewResponseEntity>;
};

export type JobReviewResponseEntityResponseCollection = {
  __typename?: 'JobReviewResponseEntityResponseCollection';
  data: Array<JobReviewResponseEntity>;
  meta: ResponseCollectionMeta;
};

export type JobReviewResponseFiltersInput = {
  AdHoc?: InputMaybe<JsonFilterInput>;
  all_user?: InputMaybe<AllUserFiltersInput>;
  and?: InputMaybe<Array<InputMaybe<JobReviewResponseFiltersInput>>>;
  by?: InputMaybe<StringFilterInput>;
  content?: InputMaybe<JsonFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  job_trainees?: InputMaybe<JobTraineeFiltersInput>;
  mark?: InputMaybe<IntFilterInput>;
  not?: InputMaybe<JobReviewResponseFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<JobReviewResponseFiltersInput>>>;
  rubric_id?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type JobReviewResponseInput = {
  AdHoc?: InputMaybe<Scalars['JSON']['input']>;
  all_user?: InputMaybe<Scalars['ID']['input']>;
  by?: InputMaybe<Scalars['String']['input']>;
  content?: InputMaybe<Scalars['JSON']['input']>;
  job_trainees?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  mark?: InputMaybe<Scalars['Int']['input']>;
  rubric_id?: InputMaybe<Scalars['String']['input']>;
};

export type JobReviewResponseRelationResponseCollection = {
  __typename?: 'JobReviewResponseRelationResponseCollection';
  data: Array<JobReviewResponseEntity>;
};

export type JobRubric = {
  __typename?: 'JobRubric';
  AdHoc?: Maybe<Scalars['JSON']['output']>;
  ReviewType?: Maybe<Scalars['String']['output']>;
  content: Scalars['JSON']['output'];
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  creator?: Maybe<AllUserEntityResponse>;
  name: Scalars['String']['output'];
  type?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type JobRubricEntity = {
  __typename?: 'JobRubricEntity';
  attributes?: Maybe<JobRubric>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type JobRubricEntityResponse = {
  __typename?: 'JobRubricEntityResponse';
  data?: Maybe<JobRubricEntity>;
};

export type JobRubricEntityResponseCollection = {
  __typename?: 'JobRubricEntityResponseCollection';
  data: Array<JobRubricEntity>;
  meta: ResponseCollectionMeta;
};

export type JobRubricFiltersInput = {
  AdHoc?: InputMaybe<JsonFilterInput>;
  ReviewType?: InputMaybe<StringFilterInput>;
  and?: InputMaybe<Array<InputMaybe<JobRubricFiltersInput>>>;
  content?: InputMaybe<JsonFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  creator?: InputMaybe<AllUserFiltersInput>;
  id?: InputMaybe<IdFilterInput>;
  name?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<JobRubricFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<JobRubricFiltersInput>>>;
  type?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type JobRubricInput = {
  AdHoc?: InputMaybe<Scalars['JSON']['input']>;
  ReviewType?: InputMaybe<Scalars['String']['input']>;
  content?: InputMaybe<Scalars['JSON']['input']>;
  creator?: InputMaybe<Scalars['ID']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  type?: InputMaybe<Scalars['String']['input']>;
};

export type JobRubricRelationResponseCollection = {
  __typename?: 'JobRubricRelationResponseCollection';
  data: Array<JobRubricEntity>;
};

export type JobTrainee = {
  __typename?: 'JobTrainee';
  Tag?: Maybe<Scalars['String']['output']>;
  additionalInfo?: Maybe<Scalars['JSON']['output']>;
  applicationDate?: Maybe<Scalars['DateTime']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  job?: Maybe<JobEntityResponse>;
  job_appliecation_statuses?: Maybe<JobAppliecationStatusRelationResponseCollection>;
  job_assets?: Maybe<JobAssetRelationResponseCollection>;
  job_review_responses?: Maybe<JobReviewResponseRelationResponseCollection>;
  slug?: Maybe<Scalars['String']['output']>;
  status?: Maybe<Scalars['String']['output']>;
  trainee?: Maybe<TraineeEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type JobTraineeJob_Appliecation_StatusesArgs = {
  filters?: InputMaybe<JobAppliecationStatusFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type JobTraineeJob_AssetsArgs = {
  filters?: InputMaybe<JobAssetFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type JobTraineeJob_Review_ResponsesArgs = {
  filters?: InputMaybe<JobReviewResponseFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type JobTraineeEntity = {
  __typename?: 'JobTraineeEntity';
  attributes?: Maybe<JobTrainee>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type JobTraineeEntityResponse = {
  __typename?: 'JobTraineeEntityResponse';
  data?: Maybe<JobTraineeEntity>;
};

export type JobTraineeEntityResponseCollection = {
  __typename?: 'JobTraineeEntityResponseCollection';
  data: Array<JobTraineeEntity>;
  meta: ResponseCollectionMeta;
};

export type JobTraineeFiltersInput = {
  Tag?: InputMaybe<StringFilterInput>;
  additionalInfo?: InputMaybe<JsonFilterInput>;
  and?: InputMaybe<Array<InputMaybe<JobTraineeFiltersInput>>>;
  applicationDate?: InputMaybe<DateTimeFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  job?: InputMaybe<JobFiltersInput>;
  job_appliecation_statuses?: InputMaybe<JobAppliecationStatusFiltersInput>;
  job_assets?: InputMaybe<JobAssetFiltersInput>;
  job_review_responses?: InputMaybe<JobReviewResponseFiltersInput>;
  not?: InputMaybe<JobTraineeFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<JobTraineeFiltersInput>>>;
  slug?: InputMaybe<StringFilterInput>;
  status?: InputMaybe<StringFilterInput>;
  trainee?: InputMaybe<TraineeFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type JobTraineeInput = {
  Tag?: InputMaybe<Scalars['String']['input']>;
  additionalInfo?: InputMaybe<Scalars['JSON']['input']>;
  applicationDate?: InputMaybe<Scalars['DateTime']['input']>;
  job?: InputMaybe<Scalars['ID']['input']>;
  job_appliecation_statuses?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  job_assets?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  job_review_responses?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  slug?: InputMaybe<Scalars['String']['input']>;
  status?: InputMaybe<Scalars['String']['input']>;
  trainee?: InputMaybe<Scalars['ID']['input']>;
};

export type JobTraineeRelationResponseCollection = {
  __typename?: 'JobTraineeRelationResponseCollection';
  data: Array<JobTraineeEntity>;
};

export type Log = {
  __typename?: 'Log';
  action_type: Enum_Log_Action_Type;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  ip_address?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  url?: Maybe<Scalars['String']['output']>;
  users_permissions_user?: Maybe<UsersPermissionsUserEntityResponse>;
};

export type LogEntity = {
  __typename?: 'LogEntity';
  attributes?: Maybe<Log>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type LogEntityResponse = {
  __typename?: 'LogEntityResponse';
  data?: Maybe<LogEntity>;
};

export type LogEntityResponseCollection = {
  __typename?: 'LogEntityResponseCollection';
  data: Array<LogEntity>;
  meta: ResponseCollectionMeta;
};

export type LogFiltersInput = {
  action_type?: InputMaybe<StringFilterInput>;
  and?: InputMaybe<Array<InputMaybe<LogFiltersInput>>>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  ip_address?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<LogFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<LogFiltersInput>>>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  url?: InputMaybe<StringFilterInput>;
  users_permissions_user?: InputMaybe<UsersPermissionsUserFiltersInput>;
};

export type LogInput = {
  action_type?: InputMaybe<Enum_Log_Action_Type>;
  ip_address?: InputMaybe<Scalars['String']['input']>;
  url?: InputMaybe<Scalars['String']['input']>;
  users_permissions_user?: InputMaybe<Scalars['ID']['input']>;
};

export type LogRelationResponseCollection = {
  __typename?: 'LogRelationResponseCollection';
  data: Array<LogEntity>;
};

export type Message = {
  __typename?: 'Message';
  content: Scalars['JSON']['output'];
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  exchange?: Maybe<ExchangeEntityResponse>;
  notification?: Maybe<NotificationEntityResponse>;
  sender_id?: Maybe<AllUserEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type MessageEntity = {
  __typename?: 'MessageEntity';
  attributes?: Maybe<Message>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type MessageEntityResponse = {
  __typename?: 'MessageEntityResponse';
  data?: Maybe<MessageEntity>;
};

export type MessageEntityResponseCollection = {
  __typename?: 'MessageEntityResponseCollection';
  data: Array<MessageEntity>;
  meta: ResponseCollectionMeta;
};

export type MessageFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<MessageFiltersInput>>>;
  content?: InputMaybe<JsonFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  exchange?: InputMaybe<ExchangeFiltersInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<MessageFiltersInput>;
  notification?: InputMaybe<NotificationFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<MessageFiltersInput>>>;
  sender_id?: InputMaybe<AllUserFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type MessageInput = {
  content?: InputMaybe<Scalars['JSON']['input']>;
  exchange?: InputMaybe<Scalars['ID']['input']>;
  notification?: InputMaybe<Scalars['ID']['input']>;
  sender_id?: InputMaybe<Scalars['ID']['input']>;
};

export type MessageRelationResponseCollection = {
  __typename?: 'MessageRelationResponseCollection';
  data: Array<MessageEntity>;
};

export type Mutation = {
  __typename?: 'Mutation';
  createAllUser?: Maybe<AllUserEntityResponse>;
  createAssignment?: Maybe<AssignmentEntityResponse>;
  createAssignmentCategory?: Maybe<AssignmentCategoryEntityResponse>;
  createAssignmentPeerGrading?: Maybe<AssignmentPeerGradingEntityResponse>;
  createAssignmentResponse?: Maybe<AssignmentResponseEntityResponse>;
  createAssignmentSubmissionSummary?: Maybe<AssignmentSubmissionSummaryEntityResponse>;
  createBatch?: Maybe<BatchEntityResponse>;
  createBatchCompetency?: Maybe<BatchCompetencyEntityResponse>;
  createBestSubmission?: Maybe<BestSubmissionEntityResponse>;
  createBlog?: Maybe<BlogEntityResponse>;
  createChallengeDocument?: Maybe<ChallengeDocumentEntityResponse>;
  createChallengeSection?: Maybe<ChallengeSectionEntityResponse>;
  createChatInformation?: Maybe<ChatInformationEntityResponse>;
  createDataDictionary?: Maybe<DataDictionaryEntityResponse>;
  createExchange?: Maybe<ExchangeEntityResponse>;
  createForm?: Maybe<FormEntityResponse>;
  createGithubAnalysisDetail?: Maybe<GithubAnalysisDetailEntityResponse>;
  createGithubAnalysisSummary?: Maybe<GithubAnalysisSummaryEntityResponse>;
  createGithubBranchCommitHistory?: Maybe<GithubBranchCommitHistoryEntityResponse>;
  createGithubReposMeta?: Maybe<GithubReposMetaEntityResponse>;
  createGithubUserMeta?: Maybe<GithubUserMetaEntityResponse>;
  createGmeet?: Maybe<GmeetEntityResponse>;
  createGrade?: Maybe<GradeEntityResponse>;
  createGroup?: Maybe<GroupEntityResponse>;
  createJob?: Maybe<JobEntityResponse>;
  createJobAppliecationStatus?: Maybe<JobAppliecationStatusEntityResponse>;
  createJobAsset?: Maybe<JobAssetEntityResponse>;
  createJobMatch?: Maybe<JobMatchEntityResponse>;
  createJobReviewResponse?: Maybe<JobReviewResponseEntityResponse>;
  createJobRubric?: Maybe<JobRubricEntityResponse>;
  createJobTrainee?: Maybe<JobTraineeEntityResponse>;
  createLog?: Maybe<LogEntityResponse>;
  createMessage?: Maybe<MessageEntityResponse>;
  createNotification?: Maybe<NotificationEntityResponse>;
  createNotificationStatus?: Maybe<NotificationStatusEntityResponse>;
  createPortfolio?: Maybe<PortfolioEntityResponse>;
  createPortfolioGroup?: Maybe<PortfolioGroupEntityResponse>;
  createPreference?: Maybe<PreferenceEntityResponse>;
  createProfileInformation?: Maybe<ProfileInformationEntityResponse>;
  createPublicLog?: Maybe<PublicLogEntityResponse>;
  createReference?: Maybe<ReferenceEntityResponse>;
  createRepo?: Maybe<RepoEntityResponse>;
  createReview?: Maybe<ReviewEntityResponse>;
  createReviewCategory?: Maybe<ReviewCategoryEntityResponse>;
  createReviewResponse?: Maybe<ReviewResponseEntityResponse>;
  createReviewer?: Maybe<ReviewerEntityResponse>;
  createRubric?: Maybe<RubricEntityResponse>;
  createSmgCriterion?: Maybe<SmgCriterionEntityResponse>;
  createSmgCriterionMetric?: Maybe<SmgCriterionMetricEntityResponse>;
  createSmgCriterionResult?: Maybe<SmgCriterionResultEntityResponse>;
  createSmgDummyRubric?: Maybe<SmgDummyRubricEntityResponse>;
  createSmgMetricPrompt?: Maybe<SmgMetricPromptEntityResponse>;
  createSmgPromptTemplate?: Maybe<SmgPromptTemplateEntityResponse>;
  createSmgRubric?: Maybe<SmgRubricEntityResponse>;
  createTinderAssetGeneration?: Maybe<TinderAssetGenerationEntityResponse>;
  createTinderJobProfile?: Maybe<TinderJobProfileEntityResponse>;
  createTinderUserJobMatch?: Maybe<TinderUserJobMatchEntityResponse>;
  createTinderUserProfile?: Maybe<TinderUserProfileEntityResponse>;
  createTinderUserReaction?: Maybe<TinderUserReactionEntityResponse>;
  createTrainee?: Maybe<TraineeEntityResponse>;
  createUploadFile?: Maybe<UploadFileEntityResponse>;
  /** Create a new role */
  createUsersPermissionsRole?: Maybe<UsersPermissionsCreateRolePayload>;
  /** Create a new user */
  createUsersPermissionsUser: UsersPermissionsUserEntityResponse;
  createWeekCompetency?: Maybe<WeekCompetencyEntityResponse>;
  deleteAllUser?: Maybe<AllUserEntityResponse>;
  deleteAssignment?: Maybe<AssignmentEntityResponse>;
  deleteAssignmentCategory?: Maybe<AssignmentCategoryEntityResponse>;
  deleteAssignmentPeerGrading?: Maybe<AssignmentPeerGradingEntityResponse>;
  deleteAssignmentResponse?: Maybe<AssignmentResponseEntityResponse>;
  deleteAssignmentSubmissionSummary?: Maybe<AssignmentSubmissionSummaryEntityResponse>;
  deleteBatch?: Maybe<BatchEntityResponse>;
  deleteBatchCompetency?: Maybe<BatchCompetencyEntityResponse>;
  deleteBestSubmission?: Maybe<BestSubmissionEntityResponse>;
  deleteBlog?: Maybe<BlogEntityResponse>;
  deleteChallengeDocument?: Maybe<ChallengeDocumentEntityResponse>;
  deleteChallengeSection?: Maybe<ChallengeSectionEntityResponse>;
  deleteChatInformation?: Maybe<ChatInformationEntityResponse>;
  deleteDataDictionary?: Maybe<DataDictionaryEntityResponse>;
  deleteExchange?: Maybe<ExchangeEntityResponse>;
  deleteForm?: Maybe<FormEntityResponse>;
  deleteGithubAnalysisDetail?: Maybe<GithubAnalysisDetailEntityResponse>;
  deleteGithubAnalysisSummary?: Maybe<GithubAnalysisSummaryEntityResponse>;
  deleteGithubBranchCommitHistory?: Maybe<GithubBranchCommitHistoryEntityResponse>;
  deleteGithubReposMeta?: Maybe<GithubReposMetaEntityResponse>;
  deleteGithubUserMeta?: Maybe<GithubUserMetaEntityResponse>;
  deleteGmeet?: Maybe<GmeetEntityResponse>;
  deleteGrade?: Maybe<GradeEntityResponse>;
  deleteGroup?: Maybe<GroupEntityResponse>;
  deleteJob?: Maybe<JobEntityResponse>;
  deleteJobAppliecationStatus?: Maybe<JobAppliecationStatusEntityResponse>;
  deleteJobAsset?: Maybe<JobAssetEntityResponse>;
  deleteJobMatch?: Maybe<JobMatchEntityResponse>;
  deleteJobReviewResponse?: Maybe<JobReviewResponseEntityResponse>;
  deleteJobRubric?: Maybe<JobRubricEntityResponse>;
  deleteJobTrainee?: Maybe<JobTraineeEntityResponse>;
  deleteLog?: Maybe<LogEntityResponse>;
  deleteMessage?: Maybe<MessageEntityResponse>;
  deleteNotification?: Maybe<NotificationEntityResponse>;
  deleteNotificationStatus?: Maybe<NotificationStatusEntityResponse>;
  deletePortfolio?: Maybe<PortfolioEntityResponse>;
  deletePortfolioGroup?: Maybe<PortfolioGroupEntityResponse>;
  deletePreference?: Maybe<PreferenceEntityResponse>;
  deleteProfileInformation?: Maybe<ProfileInformationEntityResponse>;
  deletePublicLog?: Maybe<PublicLogEntityResponse>;
  deleteReference?: Maybe<ReferenceEntityResponse>;
  deleteRepo?: Maybe<RepoEntityResponse>;
  deleteReview?: Maybe<ReviewEntityResponse>;
  deleteReviewCategory?: Maybe<ReviewCategoryEntityResponse>;
  deleteReviewResponse?: Maybe<ReviewResponseEntityResponse>;
  deleteReviewer?: Maybe<ReviewerEntityResponse>;
  deleteRubric?: Maybe<RubricEntityResponse>;
  deleteSmgCriterion?: Maybe<SmgCriterionEntityResponse>;
  deleteSmgCriterionMetric?: Maybe<SmgCriterionMetricEntityResponse>;
  deleteSmgCriterionResult?: Maybe<SmgCriterionResultEntityResponse>;
  deleteSmgDummyRubric?: Maybe<SmgDummyRubricEntityResponse>;
  deleteSmgMetricPrompt?: Maybe<SmgMetricPromptEntityResponse>;
  deleteSmgPromptTemplate?: Maybe<SmgPromptTemplateEntityResponse>;
  deleteSmgRubric?: Maybe<SmgRubricEntityResponse>;
  deleteTinderAssetGeneration?: Maybe<TinderAssetGenerationEntityResponse>;
  deleteTinderJobProfile?: Maybe<TinderJobProfileEntityResponse>;
  deleteTinderUserJobMatch?: Maybe<TinderUserJobMatchEntityResponse>;
  deleteTinderUserProfile?: Maybe<TinderUserProfileEntityResponse>;
  deleteTinderUserReaction?: Maybe<TinderUserReactionEntityResponse>;
  deleteTrainee?: Maybe<TraineeEntityResponse>;
  deleteUploadFile?: Maybe<UploadFileEntityResponse>;
  /** Delete an existing role */
  deleteUsersPermissionsRole?: Maybe<UsersPermissionsDeleteRolePayload>;
  /** Update an existing user */
  deleteUsersPermissionsUser: UsersPermissionsUserEntityResponse;
  deleteWeekCompetency?: Maybe<WeekCompetencyEntityResponse>;
  /** Confirm an email users email address */
  emailConfirmation?: Maybe<UsersPermissionsLoginPayload>;
  /** Request a reset password token */
  forgotPassword?: Maybe<UsersPermissionsPasswordPayload>;
  login: UsersPermissionsLoginPayload;
  multipleUpload: Array<Maybe<UploadFileEntityResponse>>;
  /** Register a user */
  register: UsersPermissionsLoginPayload;
  removeFile?: Maybe<UploadFileEntityResponse>;
  /** Reset user password. Confirm with a code (resetToken from forgotPassword) */
  resetPassword?: Maybe<UsersPermissionsLoginPayload>;
  updateAllUser?: Maybe<AllUserEntityResponse>;
  updateAssignment?: Maybe<AssignmentEntityResponse>;
  updateAssignmentCategory?: Maybe<AssignmentCategoryEntityResponse>;
  updateAssignmentPeerGrading?: Maybe<AssignmentPeerGradingEntityResponse>;
  updateAssignmentResponse?: Maybe<AssignmentResponseEntityResponse>;
  updateAssignmentSubmissionSummary?: Maybe<AssignmentSubmissionSummaryEntityResponse>;
  updateBatch?: Maybe<BatchEntityResponse>;
  updateBatchCompetency?: Maybe<BatchCompetencyEntityResponse>;
  updateBestSubmission?: Maybe<BestSubmissionEntityResponse>;
  updateBlog?: Maybe<BlogEntityResponse>;
  updateChallengeDocument?: Maybe<ChallengeDocumentEntityResponse>;
  updateChallengeSection?: Maybe<ChallengeSectionEntityResponse>;
  updateChatInformation?: Maybe<ChatInformationEntityResponse>;
  updateDataDictionary?: Maybe<DataDictionaryEntityResponse>;
  updateExchange?: Maybe<ExchangeEntityResponse>;
  updateFileInfo: UploadFileEntityResponse;
  updateForm?: Maybe<FormEntityResponse>;
  updateGithubAnalysisDetail?: Maybe<GithubAnalysisDetailEntityResponse>;
  updateGithubAnalysisSummary?: Maybe<GithubAnalysisSummaryEntityResponse>;
  updateGithubBranchCommitHistory?: Maybe<GithubBranchCommitHistoryEntityResponse>;
  updateGithubReposMeta?: Maybe<GithubReposMetaEntityResponse>;
  updateGithubUserMeta?: Maybe<GithubUserMetaEntityResponse>;
  updateGmeet?: Maybe<GmeetEntityResponse>;
  updateGrade?: Maybe<GradeEntityResponse>;
  updateGroup?: Maybe<GroupEntityResponse>;
  updateJob?: Maybe<JobEntityResponse>;
  updateJobAppliecationStatus?: Maybe<JobAppliecationStatusEntityResponse>;
  updateJobAsset?: Maybe<JobAssetEntityResponse>;
  updateJobMatch?: Maybe<JobMatchEntityResponse>;
  updateJobReviewResponse?: Maybe<JobReviewResponseEntityResponse>;
  updateJobRubric?: Maybe<JobRubricEntityResponse>;
  updateJobTrainee?: Maybe<JobTraineeEntityResponse>;
  updateLog?: Maybe<LogEntityResponse>;
  updateMessage?: Maybe<MessageEntityResponse>;
  updateNotification?: Maybe<NotificationEntityResponse>;
  updateNotificationStatus?: Maybe<NotificationStatusEntityResponse>;
  updatePortfolio?: Maybe<PortfolioEntityResponse>;
  updatePortfolioGroup?: Maybe<PortfolioGroupEntityResponse>;
  updatePreference?: Maybe<PreferenceEntityResponse>;
  updateProfileInformation?: Maybe<ProfileInformationEntityResponse>;
  updatePublicLog?: Maybe<PublicLogEntityResponse>;
  updateReference?: Maybe<ReferenceEntityResponse>;
  updateRepo?: Maybe<RepoEntityResponse>;
  updateReview?: Maybe<ReviewEntityResponse>;
  updateReviewCategory?: Maybe<ReviewCategoryEntityResponse>;
  updateReviewResponse?: Maybe<ReviewResponseEntityResponse>;
  updateReviewer?: Maybe<ReviewerEntityResponse>;
  updateRubric?: Maybe<RubricEntityResponse>;
  updateSmgCriterion?: Maybe<SmgCriterionEntityResponse>;
  updateSmgCriterionMetric?: Maybe<SmgCriterionMetricEntityResponse>;
  updateSmgCriterionResult?: Maybe<SmgCriterionResultEntityResponse>;
  updateSmgDummyRubric?: Maybe<SmgDummyRubricEntityResponse>;
  updateSmgMetricPrompt?: Maybe<SmgMetricPromptEntityResponse>;
  updateSmgPromptTemplate?: Maybe<SmgPromptTemplateEntityResponse>;
  updateSmgRubric?: Maybe<SmgRubricEntityResponse>;
  updateTinderAssetGeneration?: Maybe<TinderAssetGenerationEntityResponse>;
  updateTinderJobProfile?: Maybe<TinderJobProfileEntityResponse>;
  updateTinderUserJobMatch?: Maybe<TinderUserJobMatchEntityResponse>;
  updateTinderUserProfile?: Maybe<TinderUserProfileEntityResponse>;
  updateTinderUserReaction?: Maybe<TinderUserReactionEntityResponse>;
  updateTrainee?: Maybe<TraineeEntityResponse>;
  updateUploadFile?: Maybe<UploadFileEntityResponse>;
  /** Update an existing role */
  updateUsersPermissionsRole?: Maybe<UsersPermissionsUpdateRolePayload>;
  /** Update an existing user */
  updateUsersPermissionsUser: UsersPermissionsUserEntityResponse;
  updateWeekCompetency?: Maybe<WeekCompetencyEntityResponse>;
  upload: UploadFileEntityResponse;
};


export type MutationCreateAllUserArgs = {
  data: AllUserInput;
};


export type MutationCreateAssignmentArgs = {
  data: AssignmentInput;
};


export type MutationCreateAssignmentCategoryArgs = {
  data: AssignmentCategoryInput;
};


export type MutationCreateAssignmentPeerGradingArgs = {
  data: AssignmentPeerGradingInput;
};


export type MutationCreateAssignmentResponseArgs = {
  data: AssignmentResponseInput;
};


export type MutationCreateAssignmentSubmissionSummaryArgs = {
  data: AssignmentSubmissionSummaryInput;
};


export type MutationCreateBatchArgs = {
  data: BatchInput;
};


export type MutationCreateBatchCompetencyArgs = {
  data: BatchCompetencyInput;
};


export type MutationCreateBestSubmissionArgs = {
  data: BestSubmissionInput;
};


export type MutationCreateBlogArgs = {
  data: BlogInput;
};


export type MutationCreateChallengeDocumentArgs = {
  data: ChallengeDocumentInput;
};


export type MutationCreateChallengeSectionArgs = {
  data: ChallengeSectionInput;
};


export type MutationCreateChatInformationArgs = {
  data: ChatInformationInput;
};


export type MutationCreateDataDictionaryArgs = {
  data: DataDictionaryInput;
};


export type MutationCreateExchangeArgs = {
  data: ExchangeInput;
};


export type MutationCreateFormArgs = {
  data: FormInput;
};


export type MutationCreateGithubAnalysisDetailArgs = {
  data: GithubAnalysisDetailInput;
};


export type MutationCreateGithubAnalysisSummaryArgs = {
  data: GithubAnalysisSummaryInput;
};


export type MutationCreateGithubBranchCommitHistoryArgs = {
  data: GithubBranchCommitHistoryInput;
};


export type MutationCreateGithubReposMetaArgs = {
  data: GithubReposMetaInput;
};


export type MutationCreateGithubUserMetaArgs = {
  data: GithubUserMetaInput;
};


export type MutationCreateGmeetArgs = {
  data: GmeetInput;
};


export type MutationCreateGradeArgs = {
  data: GradeInput;
};


export type MutationCreateGroupArgs = {
  data: GroupInput;
};


export type MutationCreateJobArgs = {
  data: JobInput;
};


export type MutationCreateJobAppliecationStatusArgs = {
  data: JobAppliecationStatusInput;
};


export type MutationCreateJobAssetArgs = {
  data: JobAssetInput;
};


export type MutationCreateJobMatchArgs = {
  data: JobMatchInput;
};


export type MutationCreateJobReviewResponseArgs = {
  data: JobReviewResponseInput;
};


export type MutationCreateJobRubricArgs = {
  data: JobRubricInput;
};


export type MutationCreateJobTraineeArgs = {
  data: JobTraineeInput;
};


export type MutationCreateLogArgs = {
  data: LogInput;
};


export type MutationCreateMessageArgs = {
  data: MessageInput;
};


export type MutationCreateNotificationArgs = {
  data: NotificationInput;
};


export type MutationCreateNotificationStatusArgs = {
  data: NotificationStatusInput;
};


export type MutationCreatePortfolioArgs = {
  data: PortfolioInput;
};


export type MutationCreatePortfolioGroupArgs = {
  data: PortfolioGroupInput;
};


export type MutationCreatePreferenceArgs = {
  data: PreferenceInput;
};


export type MutationCreateProfileInformationArgs = {
  data: ProfileInformationInput;
};


export type MutationCreatePublicLogArgs = {
  data: PublicLogInput;
};


export type MutationCreateReferenceArgs = {
  data: ReferenceInput;
};


export type MutationCreateRepoArgs = {
  data: RepoInput;
};


export type MutationCreateReviewArgs = {
  data: ReviewInput;
};


export type MutationCreateReviewCategoryArgs = {
  data: ReviewCategoryInput;
};


export type MutationCreateReviewResponseArgs = {
  data: ReviewResponseInput;
};


export type MutationCreateReviewerArgs = {
  data: ReviewerInput;
};


export type MutationCreateRubricArgs = {
  data: RubricInput;
};


export type MutationCreateSmgCriterionArgs = {
  data: SmgCriterionInput;
};


export type MutationCreateSmgCriterionMetricArgs = {
  data: SmgCriterionMetricInput;
};


export type MutationCreateSmgCriterionResultArgs = {
  data: SmgCriterionResultInput;
};


export type MutationCreateSmgDummyRubricArgs = {
  data: SmgDummyRubricInput;
};


export type MutationCreateSmgMetricPromptArgs = {
  data: SmgMetricPromptInput;
};


export type MutationCreateSmgPromptTemplateArgs = {
  data: SmgPromptTemplateInput;
};


export type MutationCreateSmgRubricArgs = {
  data: SmgRubricInput;
};


export type MutationCreateTinderAssetGenerationArgs = {
  data: TinderAssetGenerationInput;
};


export type MutationCreateTinderJobProfileArgs = {
  data: TinderJobProfileInput;
};


export type MutationCreateTinderUserJobMatchArgs = {
  data: TinderUserJobMatchInput;
};


export type MutationCreateTinderUserProfileArgs = {
  data: TinderUserProfileInput;
};


export type MutationCreateTinderUserReactionArgs = {
  data: TinderUserReactionInput;
};


export type MutationCreateTraineeArgs = {
  data: TraineeInput;
};


export type MutationCreateUploadFileArgs = {
  data: UploadFileInput;
};


export type MutationCreateUsersPermissionsRoleArgs = {
  data: UsersPermissionsRoleInput;
};


export type MutationCreateUsersPermissionsUserArgs = {
  data: UsersPermissionsUserInput;
};


export type MutationCreateWeekCompetencyArgs = {
  data: WeekCompetencyInput;
};


export type MutationDeleteAllUserArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteAssignmentArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteAssignmentCategoryArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteAssignmentPeerGradingArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteAssignmentResponseArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteAssignmentSubmissionSummaryArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteBatchArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteBatchCompetencyArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteBestSubmissionArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteBlogArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteChallengeDocumentArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteChallengeSectionArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteChatInformationArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteDataDictionaryArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteExchangeArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteFormArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteGithubAnalysisDetailArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteGithubAnalysisSummaryArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteGithubBranchCommitHistoryArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteGithubReposMetaArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteGithubUserMetaArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteGmeetArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteGradeArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteGroupArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteJobArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteJobAppliecationStatusArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteJobAssetArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteJobMatchArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteJobReviewResponseArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteJobRubricArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteJobTraineeArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteLogArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteMessageArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteNotificationArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteNotificationStatusArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeletePortfolioArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeletePortfolioGroupArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeletePreferenceArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteProfileInformationArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeletePublicLogArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteReferenceArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteRepoArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteReviewArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteReviewCategoryArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteReviewResponseArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteReviewerArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteRubricArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteSmgCriterionArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteSmgCriterionMetricArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteSmgCriterionResultArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteSmgDummyRubricArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteSmgMetricPromptArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteSmgPromptTemplateArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteSmgRubricArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteTinderAssetGenerationArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteTinderJobProfileArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteTinderUserJobMatchArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteTinderUserProfileArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteTinderUserReactionArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteTraineeArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteUploadFileArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteUsersPermissionsRoleArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteUsersPermissionsUserArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteWeekCompetencyArgs = {
  id: Scalars['ID']['input'];
};


export type MutationEmailConfirmationArgs = {
  confirmation: Scalars['String']['input'];
};


export type MutationForgotPasswordArgs = {
  email: Scalars['String']['input'];
};


export type MutationLoginArgs = {
  input: UsersPermissionsLoginInput;
};


export type MutationMultipleUploadArgs = {
  field?: InputMaybe<Scalars['String']['input']>;
  files: Array<InputMaybe<Scalars['Upload']['input']>>;
  ref?: InputMaybe<Scalars['String']['input']>;
  refId?: InputMaybe<Scalars['ID']['input']>;
};


export type MutationRegisterArgs = {
  input: UsersPermissionsRegisterInput;
};


export type MutationRemoveFileArgs = {
  id: Scalars['ID']['input'];
};


export type MutationResetPasswordArgs = {
  code: Scalars['String']['input'];
  password: Scalars['String']['input'];
  passwordConfirmation: Scalars['String']['input'];
};


export type MutationUpdateAllUserArgs = {
  data: AllUserInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateAssignmentArgs = {
  data: AssignmentInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateAssignmentCategoryArgs = {
  data: AssignmentCategoryInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateAssignmentPeerGradingArgs = {
  data: AssignmentPeerGradingInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateAssignmentResponseArgs = {
  data: AssignmentResponseInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateAssignmentSubmissionSummaryArgs = {
  data: AssignmentSubmissionSummaryInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateBatchArgs = {
  data: BatchInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateBatchCompetencyArgs = {
  data: BatchCompetencyInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateBestSubmissionArgs = {
  data: BestSubmissionInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateBlogArgs = {
  data: BlogInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateChallengeDocumentArgs = {
  data: ChallengeDocumentInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateChallengeSectionArgs = {
  data: ChallengeSectionInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateChatInformationArgs = {
  data: ChatInformationInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateDataDictionaryArgs = {
  data: DataDictionaryInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateExchangeArgs = {
  data: ExchangeInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateFileInfoArgs = {
  id: Scalars['ID']['input'];
  info?: InputMaybe<FileInfoInput>;
};


export type MutationUpdateFormArgs = {
  data: FormInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateGithubAnalysisDetailArgs = {
  data: GithubAnalysisDetailInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateGithubAnalysisSummaryArgs = {
  data: GithubAnalysisSummaryInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateGithubBranchCommitHistoryArgs = {
  data: GithubBranchCommitHistoryInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateGithubReposMetaArgs = {
  data: GithubReposMetaInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateGithubUserMetaArgs = {
  data: GithubUserMetaInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateGmeetArgs = {
  data: GmeetInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateGradeArgs = {
  data: GradeInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateGroupArgs = {
  data: GroupInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateJobArgs = {
  data: JobInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateJobAppliecationStatusArgs = {
  data: JobAppliecationStatusInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateJobAssetArgs = {
  data: JobAssetInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateJobMatchArgs = {
  data: JobMatchInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateJobReviewResponseArgs = {
  data: JobReviewResponseInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateJobRubricArgs = {
  data: JobRubricInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateJobTraineeArgs = {
  data: JobTraineeInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateLogArgs = {
  data: LogInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateMessageArgs = {
  data: MessageInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateNotificationArgs = {
  data: NotificationInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateNotificationStatusArgs = {
  data: NotificationStatusInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdatePortfolioArgs = {
  data: PortfolioInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdatePortfolioGroupArgs = {
  data: PortfolioGroupInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdatePreferenceArgs = {
  data: PreferenceInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateProfileInformationArgs = {
  data: ProfileInformationInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdatePublicLogArgs = {
  data: PublicLogInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateReferenceArgs = {
  data: ReferenceInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateRepoArgs = {
  data: RepoInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateReviewArgs = {
  data: ReviewInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateReviewCategoryArgs = {
  data: ReviewCategoryInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateReviewResponseArgs = {
  data: ReviewResponseInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateReviewerArgs = {
  data: ReviewerInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateRubricArgs = {
  data: RubricInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateSmgCriterionArgs = {
  data: SmgCriterionInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateSmgCriterionMetricArgs = {
  data: SmgCriterionMetricInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateSmgCriterionResultArgs = {
  data: SmgCriterionResultInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateSmgDummyRubricArgs = {
  data: SmgDummyRubricInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateSmgMetricPromptArgs = {
  data: SmgMetricPromptInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateSmgPromptTemplateArgs = {
  data: SmgPromptTemplateInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateSmgRubricArgs = {
  data: SmgRubricInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateTinderAssetGenerationArgs = {
  data: TinderAssetGenerationInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateTinderJobProfileArgs = {
  data: TinderJobProfileInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateTinderUserJobMatchArgs = {
  data: TinderUserJobMatchInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateTinderUserProfileArgs = {
  data: TinderUserProfileInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateTinderUserReactionArgs = {
  data: TinderUserReactionInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateTraineeArgs = {
  data: TraineeInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateUploadFileArgs = {
  data: UploadFileInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateUsersPermissionsRoleArgs = {
  data: UsersPermissionsRoleInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateUsersPermissionsUserArgs = {
  data: UsersPermissionsUserInput;
  id: Scalars['ID']['input'];
};


export type MutationUpdateWeekCompetencyArgs = {
  data: WeekCompetencyInput;
  id: Scalars['ID']['input'];
};


export type MutationUploadArgs = {
  field?: InputMaybe<Scalars['String']['input']>;
  file: Scalars['Upload']['input'];
  info?: InputMaybe<FileInfoInput>;
  ref?: InputMaybe<Scalars['String']['input']>;
  refId?: InputMaybe<Scalars['ID']['input']>;
};

export type Notification = {
  __typename?: 'Notification';
  Detail?: Maybe<Scalars['JSON']['output']>;
  batch?: Maybe<Scalars['Int']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  group?: Maybe<GroupEntityResponse>;
  message?: Maybe<MessageEntityResponse>;
  notification_statuses?: Maybe<NotificationStatusRelationResponseCollection>;
  receiver?: Maybe<AllUserEntityResponse>;
  sender?: Maybe<AllUserEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type NotificationNotification_StatusesArgs = {
  filters?: InputMaybe<NotificationStatusFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type NotificationEntity = {
  __typename?: 'NotificationEntity';
  attributes?: Maybe<Notification>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type NotificationEntityResponse = {
  __typename?: 'NotificationEntityResponse';
  data?: Maybe<NotificationEntity>;
};

export type NotificationEntityResponseCollection = {
  __typename?: 'NotificationEntityResponseCollection';
  data: Array<NotificationEntity>;
  meta: ResponseCollectionMeta;
};

export type NotificationFiltersInput = {
  Detail?: InputMaybe<JsonFilterInput>;
  and?: InputMaybe<Array<InputMaybe<NotificationFiltersInput>>>;
  batch?: InputMaybe<IntFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  group?: InputMaybe<GroupFiltersInput>;
  id?: InputMaybe<IdFilterInput>;
  message?: InputMaybe<MessageFiltersInput>;
  not?: InputMaybe<NotificationFiltersInput>;
  notification_statuses?: InputMaybe<NotificationStatusFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<NotificationFiltersInput>>>;
  receiver?: InputMaybe<AllUserFiltersInput>;
  sender?: InputMaybe<AllUserFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type NotificationInput = {
  Detail?: InputMaybe<Scalars['JSON']['input']>;
  batch?: InputMaybe<Scalars['Int']['input']>;
  group?: InputMaybe<Scalars['ID']['input']>;
  message?: InputMaybe<Scalars['ID']['input']>;
  notification_statuses?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  receiver?: InputMaybe<Scalars['ID']['input']>;
  sender?: InputMaybe<Scalars['ID']['input']>;
};

export type NotificationRelationResponseCollection = {
  __typename?: 'NotificationRelationResponseCollection';
  data: Array<NotificationEntity>;
};

export type NotificationStatus = {
  __typename?: 'NotificationStatus';
  IsRead?: Maybe<Scalars['Boolean']['output']>;
  all_user?: Maybe<AllUserEntityResponse>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  notification?: Maybe<NotificationEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type NotificationStatusEntity = {
  __typename?: 'NotificationStatusEntity';
  attributes?: Maybe<NotificationStatus>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type NotificationStatusEntityResponse = {
  __typename?: 'NotificationStatusEntityResponse';
  data?: Maybe<NotificationStatusEntity>;
};

export type NotificationStatusEntityResponseCollection = {
  __typename?: 'NotificationStatusEntityResponseCollection';
  data: Array<NotificationStatusEntity>;
  meta: ResponseCollectionMeta;
};

export type NotificationStatusFiltersInput = {
  IsRead?: InputMaybe<BooleanFilterInput>;
  all_user?: InputMaybe<AllUserFiltersInput>;
  and?: InputMaybe<Array<InputMaybe<NotificationStatusFiltersInput>>>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<NotificationStatusFiltersInput>;
  notification?: InputMaybe<NotificationFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<NotificationStatusFiltersInput>>>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type NotificationStatusInput = {
  IsRead?: InputMaybe<Scalars['Boolean']['input']>;
  all_user?: InputMaybe<Scalars['ID']['input']>;
  notification?: InputMaybe<Scalars['ID']['input']>;
};

export type NotificationStatusRelationResponseCollection = {
  __typename?: 'NotificationStatusRelationResponseCollection';
  data: Array<NotificationStatusEntity>;
};

export type Pagination = {
  __typename?: 'Pagination';
  page: Scalars['Int']['output'];
  pageCount: Scalars['Int']['output'];
  pageSize: Scalars['Int']['output'];
  total: Scalars['Int']['output'];
};

export type PaginationArg = {
  limit?: InputMaybe<Scalars['Int']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  pageSize?: InputMaybe<Scalars['Int']['input']>;
  start?: InputMaybe<Scalars['Int']['input']>;
};

export type Portfolio = {
  __typename?: 'Portfolio';
  batch?: Maybe<BatchEntityResponse>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  description: Scalars['String']['output'];
  email?: Maybe<Scalars['String']['output']>;
  image?: Maybe<UploadFileEntityResponse>;
  location?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  other_info?: Maybe<Scalars['JSON']['output']>;
  performance_tag?: Maybe<Scalars['String']['output']>;
  portfolio_groups?: Maybe<PortfolioGroupRelationResponseCollection>;
  portfolio_link: Scalars['String']['output'];
  profileStatus?: Maybe<Scalars['String']['output']>;
  role: Scalars['String']['output'];
  skills: Scalars['JSON']['output'];
  status: Enum_Portfolio_Status;
  story?: Maybe<Scalars['String']['output']>;
  trainee?: Maybe<TraineeEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type PortfolioPortfolio_GroupsArgs = {
  filters?: InputMaybe<PortfolioGroupFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type PortfolioEntity = {
  __typename?: 'PortfolioEntity';
  attributes?: Maybe<Portfolio>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type PortfolioEntityResponse = {
  __typename?: 'PortfolioEntityResponse';
  data?: Maybe<PortfolioEntity>;
};

export type PortfolioEntityResponseCollection = {
  __typename?: 'PortfolioEntityResponseCollection';
  data: Array<PortfolioEntity>;
  meta: ResponseCollectionMeta;
};

export type PortfolioFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<PortfolioFiltersInput>>>;
  batch?: InputMaybe<BatchFiltersInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  description?: InputMaybe<StringFilterInput>;
  email?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  location?: InputMaybe<StringFilterInput>;
  name?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<PortfolioFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<PortfolioFiltersInput>>>;
  other_info?: InputMaybe<JsonFilterInput>;
  performance_tag?: InputMaybe<StringFilterInput>;
  portfolio_groups?: InputMaybe<PortfolioGroupFiltersInput>;
  portfolio_link?: InputMaybe<StringFilterInput>;
  profileStatus?: InputMaybe<StringFilterInput>;
  role?: InputMaybe<StringFilterInput>;
  skills?: InputMaybe<JsonFilterInput>;
  status?: InputMaybe<StringFilterInput>;
  story?: InputMaybe<StringFilterInput>;
  trainee?: InputMaybe<TraineeFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type PortfolioGroup = {
  __typename?: 'PortfolioGroup';
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  name: Scalars['String']['output'];
  other_info?: Maybe<Scalars['JSON']['output']>;
  portfolios?: Maybe<PortfolioRelationResponseCollection>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type PortfolioGroupPortfoliosArgs = {
  filters?: InputMaybe<PortfolioFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type PortfolioGroupEntity = {
  __typename?: 'PortfolioGroupEntity';
  attributes?: Maybe<PortfolioGroup>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type PortfolioGroupEntityResponse = {
  __typename?: 'PortfolioGroupEntityResponse';
  data?: Maybe<PortfolioGroupEntity>;
};

export type PortfolioGroupEntityResponseCollection = {
  __typename?: 'PortfolioGroupEntityResponseCollection';
  data: Array<PortfolioGroupEntity>;
  meta: ResponseCollectionMeta;
};

export type PortfolioGroupFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<PortfolioGroupFiltersInput>>>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  name?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<PortfolioGroupFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<PortfolioGroupFiltersInput>>>;
  other_info?: InputMaybe<JsonFilterInput>;
  portfolios?: InputMaybe<PortfolioFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type PortfolioGroupInput = {
  name?: InputMaybe<Scalars['String']['input']>;
  other_info?: InputMaybe<Scalars['JSON']['input']>;
  portfolios?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
};

export type PortfolioGroupRelationResponseCollection = {
  __typename?: 'PortfolioGroupRelationResponseCollection';
  data: Array<PortfolioGroupEntity>;
};

export type PortfolioInput = {
  batch?: InputMaybe<Scalars['ID']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  email?: InputMaybe<Scalars['String']['input']>;
  image?: InputMaybe<Scalars['ID']['input']>;
  location?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  other_info?: InputMaybe<Scalars['JSON']['input']>;
  performance_tag?: InputMaybe<Scalars['String']['input']>;
  portfolio_groups?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  portfolio_link?: InputMaybe<Scalars['String']['input']>;
  profileStatus?: InputMaybe<Scalars['String']['input']>;
  role?: InputMaybe<Scalars['String']['input']>;
  skills?: InputMaybe<Scalars['JSON']['input']>;
  status?: InputMaybe<Enum_Portfolio_Status>;
  story?: InputMaybe<Scalars['String']['input']>;
  trainee?: InputMaybe<Scalars['ID']['input']>;
};

export type PortfolioRelationResponseCollection = {
  __typename?: 'PortfolioRelationResponseCollection';
  data: Array<PortfolioEntity>;
};

export type Preference = {
  __typename?: 'Preference';
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  defaultSettings?: Maybe<Scalars['JSON']['output']>;
  email: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  users_permissions_user?: Maybe<UsersPermissionsUserEntityResponse>;
};

export type PreferenceEntity = {
  __typename?: 'PreferenceEntity';
  attributes?: Maybe<Preference>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type PreferenceEntityResponse = {
  __typename?: 'PreferenceEntityResponse';
  data?: Maybe<PreferenceEntity>;
};

export type PreferenceEntityResponseCollection = {
  __typename?: 'PreferenceEntityResponseCollection';
  data: Array<PreferenceEntity>;
  meta: ResponseCollectionMeta;
};

export type PreferenceFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<PreferenceFiltersInput>>>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  defaultSettings?: InputMaybe<JsonFilterInput>;
  email?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<PreferenceFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<PreferenceFiltersInput>>>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  users_permissions_user?: InputMaybe<UsersPermissionsUserFiltersInput>;
};

export type PreferenceInput = {
  defaultSettings?: InputMaybe<Scalars['JSON']['input']>;
  email?: InputMaybe<Scalars['String']['input']>;
  users_permissions_user?: InputMaybe<Scalars['ID']['input']>;
};

export type ProfileInformation = {
  __typename?: 'ProfileInformation';
  all_user?: Maybe<AllUserEntityResponse>;
  bio?: Maybe<Scalars['String']['output']>;
  city_of_residence?: Maybe<Scalars['String']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  date_of_birth?: Maybe<Scalars['Date']['output']>;
  email: Scalars['String']['output'];
  first_name?: Maybe<Scalars['String']['output']>;
  gender?: Maybe<Scalars['String']['output']>;
  nationality?: Maybe<Scalars['String']['output']>;
  other_info?: Maybe<Scalars['JSON']['output']>;
  surname?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type ProfileInformationEntity = {
  __typename?: 'ProfileInformationEntity';
  attributes?: Maybe<ProfileInformation>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type ProfileInformationEntityResponse = {
  __typename?: 'ProfileInformationEntityResponse';
  data?: Maybe<ProfileInformationEntity>;
};

export type ProfileInformationEntityResponseCollection = {
  __typename?: 'ProfileInformationEntityResponseCollection';
  data: Array<ProfileInformationEntity>;
  meta: ResponseCollectionMeta;
};

export type ProfileInformationFiltersInput = {
  all_user?: InputMaybe<AllUserFiltersInput>;
  and?: InputMaybe<Array<InputMaybe<ProfileInformationFiltersInput>>>;
  bio?: InputMaybe<StringFilterInput>;
  city_of_residence?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  date_of_birth?: InputMaybe<DateFilterInput>;
  email?: InputMaybe<StringFilterInput>;
  first_name?: InputMaybe<StringFilterInput>;
  gender?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  nationality?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<ProfileInformationFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<ProfileInformationFiltersInput>>>;
  other_info?: InputMaybe<JsonFilterInput>;
  surname?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type ProfileInformationInput = {
  all_user?: InputMaybe<Scalars['ID']['input']>;
  bio?: InputMaybe<Scalars['String']['input']>;
  city_of_residence?: InputMaybe<Scalars['String']['input']>;
  date_of_birth?: InputMaybe<Scalars['Date']['input']>;
  email?: InputMaybe<Scalars['String']['input']>;
  first_name?: InputMaybe<Scalars['String']['input']>;
  gender?: InputMaybe<Scalars['String']['input']>;
  nationality?: InputMaybe<Scalars['String']['input']>;
  other_info?: InputMaybe<Scalars['JSON']['input']>;
  surname?: InputMaybe<Scalars['String']['input']>;
};

export type PublicLog = {
  __typename?: 'PublicLog';
  action_type: Scalars['String']['output'];
  componentURL?: Maybe<Scalars['String']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  ip_address?: Maybe<Scalars['String']['output']>;
  other_info?: Maybe<Scalars['JSON']['output']>;
  pageURL: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type PublicLogEntity = {
  __typename?: 'PublicLogEntity';
  attributes?: Maybe<PublicLog>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type PublicLogEntityResponse = {
  __typename?: 'PublicLogEntityResponse';
  data?: Maybe<PublicLogEntity>;
};

export type PublicLogEntityResponseCollection = {
  __typename?: 'PublicLogEntityResponseCollection';
  data: Array<PublicLogEntity>;
  meta: ResponseCollectionMeta;
};

export type PublicLogFiltersInput = {
  action_type?: InputMaybe<StringFilterInput>;
  and?: InputMaybe<Array<InputMaybe<PublicLogFiltersInput>>>;
  componentURL?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  ip_address?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<PublicLogFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<PublicLogFiltersInput>>>;
  other_info?: InputMaybe<JsonFilterInput>;
  pageURL?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type PublicLogInput = {
  action_type?: InputMaybe<Scalars['String']['input']>;
  componentURL?: InputMaybe<Scalars['String']['input']>;
  ip_address?: InputMaybe<Scalars['String']['input']>;
  other_info?: InputMaybe<Scalars['JSON']['input']>;
  pageURL?: InputMaybe<Scalars['String']['input']>;
};

export enum PublicationState {
  Live = 'LIVE',
  Preview = 'PREVIEW'
}

export type Query = {
  __typename?: 'Query';
  allUser?: Maybe<AllUserEntityResponse>;
  allUsers?: Maybe<AllUserEntityResponseCollection>;
  assignment?: Maybe<AssignmentEntityResponse>;
  assignmentCategories?: Maybe<AssignmentCategoryEntityResponseCollection>;
  assignmentCategory?: Maybe<AssignmentCategoryEntityResponse>;
  assignmentPeerGrading?: Maybe<AssignmentPeerGradingEntityResponse>;
  assignmentPeerGradings?: Maybe<AssignmentPeerGradingEntityResponseCollection>;
  assignmentResponse?: Maybe<AssignmentResponseEntityResponse>;
  assignmentResponses?: Maybe<AssignmentResponseEntityResponseCollection>;
  assignmentSubmissionSummaries?: Maybe<AssignmentSubmissionSummaryEntityResponseCollection>;
  assignmentSubmissionSummary?: Maybe<AssignmentSubmissionSummaryEntityResponse>;
  assignments?: Maybe<AssignmentEntityResponseCollection>;
  batch?: Maybe<BatchEntityResponse>;
  batchCompetencies?: Maybe<BatchCompetencyEntityResponseCollection>;
  batchCompetency?: Maybe<BatchCompetencyEntityResponse>;
  batches?: Maybe<BatchEntityResponseCollection>;
  bestSubmission?: Maybe<BestSubmissionEntityResponse>;
  bestSubmissions?: Maybe<BestSubmissionEntityResponseCollection>;
  blog?: Maybe<BlogEntityResponse>;
  blogs?: Maybe<BlogEntityResponseCollection>;
  challengeDocument?: Maybe<ChallengeDocumentEntityResponse>;
  challengeDocuments?: Maybe<ChallengeDocumentEntityResponseCollection>;
  challengeSection?: Maybe<ChallengeSectionEntityResponse>;
  challengeSections?: Maybe<ChallengeSectionEntityResponseCollection>;
  chatInformation?: Maybe<ChatInformationEntityResponse>;
  chatInformations?: Maybe<ChatInformationEntityResponseCollection>;
  dataDictionaries?: Maybe<DataDictionaryEntityResponseCollection>;
  dataDictionary?: Maybe<DataDictionaryEntityResponse>;
  exchange?: Maybe<ExchangeEntityResponse>;
  exchanges?: Maybe<ExchangeEntityResponseCollection>;
  form?: Maybe<FormEntityResponse>;
  forms?: Maybe<FormEntityResponseCollection>;
  githubAnalysisDetail?: Maybe<GithubAnalysisDetailEntityResponse>;
  githubAnalysisDetails?: Maybe<GithubAnalysisDetailEntityResponseCollection>;
  githubAnalysisSummaries?: Maybe<GithubAnalysisSummaryEntityResponseCollection>;
  githubAnalysisSummary?: Maybe<GithubAnalysisSummaryEntityResponse>;
  githubBranchCommitHistories?: Maybe<GithubBranchCommitHistoryEntityResponseCollection>;
  githubBranchCommitHistory?: Maybe<GithubBranchCommitHistoryEntityResponse>;
  githubReposMeta?: Maybe<GithubReposMetaEntityResponse>;
  githubReposMetas?: Maybe<GithubReposMetaEntityResponseCollection>;
  githubUserMeta?: Maybe<GithubUserMetaEntityResponse>;
  githubUserMetas?: Maybe<GithubUserMetaEntityResponseCollection>;
  gmeet?: Maybe<GmeetEntityResponse>;
  gmeets?: Maybe<GmeetEntityResponseCollection>;
  grade?: Maybe<GradeEntityResponse>;
  grades?: Maybe<GradeEntityResponseCollection>;
  group?: Maybe<GroupEntityResponse>;
  groups?: Maybe<GroupEntityResponseCollection>;
  i18NLocale?: Maybe<I18NLocaleEntityResponse>;
  i18NLocales?: Maybe<I18NLocaleEntityResponseCollection>;
  job?: Maybe<JobEntityResponse>;
  jobAppliecationStatus?: Maybe<JobAppliecationStatusEntityResponse>;
  jobAppliecationStatuses?: Maybe<JobAppliecationStatusEntityResponseCollection>;
  jobAsset?: Maybe<JobAssetEntityResponse>;
  jobAssets?: Maybe<JobAssetEntityResponseCollection>;
  jobMatch?: Maybe<JobMatchEntityResponse>;
  jobMatches?: Maybe<JobMatchEntityResponseCollection>;
  jobReviewResponse?: Maybe<JobReviewResponseEntityResponse>;
  jobReviewResponses?: Maybe<JobReviewResponseEntityResponseCollection>;
  jobRubric?: Maybe<JobRubricEntityResponse>;
  jobRubrics?: Maybe<JobRubricEntityResponseCollection>;
  jobTrainee?: Maybe<JobTraineeEntityResponse>;
  jobTrainees?: Maybe<JobTraineeEntityResponseCollection>;
  jobs?: Maybe<JobEntityResponseCollection>;
  log?: Maybe<LogEntityResponse>;
  logs?: Maybe<LogEntityResponseCollection>;
  me?: Maybe<UsersPermissionsMe>;
  message?: Maybe<MessageEntityResponse>;
  messages?: Maybe<MessageEntityResponseCollection>;
  notification?: Maybe<NotificationEntityResponse>;
  notificationStatus?: Maybe<NotificationStatusEntityResponse>;
  notificationStatuses?: Maybe<NotificationStatusEntityResponseCollection>;
  notifications?: Maybe<NotificationEntityResponseCollection>;
  portfolio?: Maybe<PortfolioEntityResponse>;
  portfolioGroup?: Maybe<PortfolioGroupEntityResponse>;
  portfolioGroups?: Maybe<PortfolioGroupEntityResponseCollection>;
  portfolios?: Maybe<PortfolioEntityResponseCollection>;
  preference?: Maybe<PreferenceEntityResponse>;
  preferences?: Maybe<PreferenceEntityResponseCollection>;
  profileInformation?: Maybe<ProfileInformationEntityResponse>;
  profileInformations?: Maybe<ProfileInformationEntityResponseCollection>;
  publicLog?: Maybe<PublicLogEntityResponse>;
  publicLogs?: Maybe<PublicLogEntityResponseCollection>;
  reference?: Maybe<ReferenceEntityResponse>;
  references?: Maybe<ReferenceEntityResponseCollection>;
  repo?: Maybe<RepoEntityResponse>;
  repos?: Maybe<RepoEntityResponseCollection>;
  review?: Maybe<ReviewEntityResponse>;
  reviewCategories?: Maybe<ReviewCategoryEntityResponseCollection>;
  reviewCategory?: Maybe<ReviewCategoryEntityResponse>;
  reviewResponse?: Maybe<ReviewResponseEntityResponse>;
  reviewResponses?: Maybe<ReviewResponseEntityResponseCollection>;
  reviewer?: Maybe<ReviewerEntityResponse>;
  reviewers?: Maybe<ReviewerEntityResponseCollection>;
  reviews?: Maybe<ReviewEntityResponseCollection>;
  rubric?: Maybe<RubricEntityResponse>;
  rubrics?: Maybe<RubricEntityResponseCollection>;
  smgCriteria?: Maybe<SmgCriterionEntityResponseCollection>;
  smgCriterion?: Maybe<SmgCriterionEntityResponse>;
  smgCriterionMetric?: Maybe<SmgCriterionMetricEntityResponse>;
  smgCriterionMetrics?: Maybe<SmgCriterionMetricEntityResponseCollection>;
  smgCriterionResult?: Maybe<SmgCriterionResultEntityResponse>;
  smgCriterionResults?: Maybe<SmgCriterionResultEntityResponseCollection>;
  smgDummyRubric?: Maybe<SmgDummyRubricEntityResponse>;
  smgDummyRubrics?: Maybe<SmgDummyRubricEntityResponseCollection>;
  smgMetricPrompt?: Maybe<SmgMetricPromptEntityResponse>;
  smgMetricPrompts?: Maybe<SmgMetricPromptEntityResponseCollection>;
  smgPromptTemplate?: Maybe<SmgPromptTemplateEntityResponse>;
  smgPromptTemplates?: Maybe<SmgPromptTemplateEntityResponseCollection>;
  smgRubric?: Maybe<SmgRubricEntityResponse>;
  smgRubrics?: Maybe<SmgRubricEntityResponseCollection>;
  tinderAssetGeneration?: Maybe<TinderAssetGenerationEntityResponse>;
  tinderAssetGenerations?: Maybe<TinderAssetGenerationEntityResponseCollection>;
  tinderJobProfile?: Maybe<TinderJobProfileEntityResponse>;
  tinderJobProfiles?: Maybe<TinderJobProfileEntityResponseCollection>;
  tinderUserJobMatch?: Maybe<TinderUserJobMatchEntityResponse>;
  tinderUserJobMatches?: Maybe<TinderUserJobMatchEntityResponseCollection>;
  tinderUserProfile?: Maybe<TinderUserProfileEntityResponse>;
  tinderUserProfiles?: Maybe<TinderUserProfileEntityResponseCollection>;
  tinderUserReaction?: Maybe<TinderUserReactionEntityResponse>;
  tinderUserReactions?: Maybe<TinderUserReactionEntityResponseCollection>;
  trainee?: Maybe<TraineeEntityResponse>;
  trainees?: Maybe<TraineeEntityResponseCollection>;
  uploadFile?: Maybe<UploadFileEntityResponse>;
  uploadFiles?: Maybe<UploadFileEntityResponseCollection>;
  usersPermissionsRole?: Maybe<UsersPermissionsRoleEntityResponse>;
  usersPermissionsRoles?: Maybe<UsersPermissionsRoleEntityResponseCollection>;
  usersPermissionsUser?: Maybe<UsersPermissionsUserEntityResponse>;
  usersPermissionsUsers?: Maybe<UsersPermissionsUserEntityResponseCollection>;
  weekCompetencies?: Maybe<WeekCompetencyEntityResponseCollection>;
  weekCompetency?: Maybe<WeekCompetencyEntityResponse>;
};


export type QueryAllUserArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryAllUsersArgs = {
  filters?: InputMaybe<AllUserFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryAssignmentArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryAssignmentCategoriesArgs = {
  filters?: InputMaybe<AssignmentCategoryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryAssignmentCategoryArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryAssignmentPeerGradingArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryAssignmentPeerGradingsArgs = {
  filters?: InputMaybe<AssignmentPeerGradingFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryAssignmentResponseArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryAssignmentResponsesArgs = {
  filters?: InputMaybe<AssignmentResponseFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryAssignmentSubmissionSummariesArgs = {
  filters?: InputMaybe<AssignmentSubmissionSummaryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryAssignmentSubmissionSummaryArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryAssignmentsArgs = {
  filters?: InputMaybe<AssignmentFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryBatchArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryBatchCompetenciesArgs = {
  filters?: InputMaybe<BatchCompetencyFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryBatchCompetencyArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryBatchesArgs = {
  filters?: InputMaybe<BatchFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryBestSubmissionArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryBestSubmissionsArgs = {
  filters?: InputMaybe<BestSubmissionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryBlogArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryBlogsArgs = {
  filters?: InputMaybe<BlogFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryChallengeDocumentArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryChallengeDocumentsArgs = {
  filters?: InputMaybe<ChallengeDocumentFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryChallengeSectionArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryChallengeSectionsArgs = {
  filters?: InputMaybe<ChallengeSectionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryChatInformationArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryChatInformationsArgs = {
  filters?: InputMaybe<ChatInformationFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryDataDictionariesArgs = {
  filters?: InputMaybe<DataDictionaryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryDataDictionaryArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryExchangeArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryExchangesArgs = {
  filters?: InputMaybe<ExchangeFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryFormArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryFormsArgs = {
  filters?: InputMaybe<FormFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryGithubAnalysisDetailArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryGithubAnalysisDetailsArgs = {
  filters?: InputMaybe<GithubAnalysisDetailFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryGithubAnalysisSummariesArgs = {
  filters?: InputMaybe<GithubAnalysisSummaryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryGithubAnalysisSummaryArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryGithubBranchCommitHistoriesArgs = {
  filters?: InputMaybe<GithubBranchCommitHistoryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryGithubBranchCommitHistoryArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryGithubReposMetaArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryGithubReposMetasArgs = {
  filters?: InputMaybe<GithubReposMetaFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryGithubUserMetaArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryGithubUserMetasArgs = {
  filters?: InputMaybe<GithubUserMetaFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryGmeetArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryGmeetsArgs = {
  filters?: InputMaybe<GmeetFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryGradeArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryGradesArgs = {
  filters?: InputMaybe<GradeFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryGroupArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryGroupsArgs = {
  filters?: InputMaybe<GroupFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryI18NLocaleArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryI18NLocalesArgs = {
  filters?: InputMaybe<I18NLocaleFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryJobArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryJobAppliecationStatusArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryJobAppliecationStatusesArgs = {
  filters?: InputMaybe<JobAppliecationStatusFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryJobAssetArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryJobAssetsArgs = {
  filters?: InputMaybe<JobAssetFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryJobMatchArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryJobMatchesArgs = {
  filters?: InputMaybe<JobMatchFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryJobReviewResponseArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryJobReviewResponsesArgs = {
  filters?: InputMaybe<JobReviewResponseFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryJobRubricArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryJobRubricsArgs = {
  filters?: InputMaybe<JobRubricFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryJobTraineeArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryJobTraineesArgs = {
  filters?: InputMaybe<JobTraineeFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryJobsArgs = {
  filters?: InputMaybe<JobFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryLogArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryLogsArgs = {
  filters?: InputMaybe<LogFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryMessageArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryMessagesArgs = {
  filters?: InputMaybe<MessageFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryNotificationArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryNotificationStatusArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryNotificationStatusesArgs = {
  filters?: InputMaybe<NotificationStatusFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryNotificationsArgs = {
  filters?: InputMaybe<NotificationFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryPortfolioArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryPortfolioGroupArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryPortfolioGroupsArgs = {
  filters?: InputMaybe<PortfolioGroupFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryPortfoliosArgs = {
  filters?: InputMaybe<PortfolioFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryPreferenceArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryPreferencesArgs = {
  filters?: InputMaybe<PreferenceFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryProfileInformationArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryProfileInformationsArgs = {
  filters?: InputMaybe<ProfileInformationFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryPublicLogArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryPublicLogsArgs = {
  filters?: InputMaybe<PublicLogFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryReferenceArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryReferencesArgs = {
  filters?: InputMaybe<ReferenceFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryRepoArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryReposArgs = {
  filters?: InputMaybe<RepoFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryReviewArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryReviewCategoriesArgs = {
  filters?: InputMaybe<ReviewCategoryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryReviewCategoryArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryReviewResponseArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryReviewResponsesArgs = {
  filters?: InputMaybe<ReviewResponseFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryReviewerArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryReviewersArgs = {
  filters?: InputMaybe<ReviewerFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryReviewsArgs = {
  filters?: InputMaybe<ReviewFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryRubricArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryRubricsArgs = {
  filters?: InputMaybe<RubricFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QuerySmgCriteriaArgs = {
  filters?: InputMaybe<SmgCriterionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QuerySmgCriterionArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QuerySmgCriterionMetricArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QuerySmgCriterionMetricsArgs = {
  filters?: InputMaybe<SmgCriterionMetricFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QuerySmgCriterionResultArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QuerySmgCriterionResultsArgs = {
  filters?: InputMaybe<SmgCriterionResultFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QuerySmgDummyRubricArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QuerySmgDummyRubricsArgs = {
  filters?: InputMaybe<SmgDummyRubricFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QuerySmgMetricPromptArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QuerySmgMetricPromptsArgs = {
  filters?: InputMaybe<SmgMetricPromptFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QuerySmgPromptTemplateArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QuerySmgPromptTemplatesArgs = {
  filters?: InputMaybe<SmgPromptTemplateFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QuerySmgRubricArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QuerySmgRubricsArgs = {
  filters?: InputMaybe<SmgRubricFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryTinderAssetGenerationArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryTinderAssetGenerationsArgs = {
  filters?: InputMaybe<TinderAssetGenerationFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryTinderJobProfileArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryTinderJobProfilesArgs = {
  filters?: InputMaybe<TinderJobProfileFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryTinderUserJobMatchArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryTinderUserJobMatchesArgs = {
  filters?: InputMaybe<TinderUserJobMatchFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryTinderUserProfileArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryTinderUserProfilesArgs = {
  filters?: InputMaybe<TinderUserProfileFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryTinderUserReactionArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryTinderUserReactionsArgs = {
  filters?: InputMaybe<TinderUserReactionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryTraineeArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryTraineesArgs = {
  filters?: InputMaybe<TraineeFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryUploadFileArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryUploadFilesArgs = {
  filters?: InputMaybe<UploadFileFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryUsersPermissionsRoleArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryUsersPermissionsRolesArgs = {
  filters?: InputMaybe<UsersPermissionsRoleFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryUsersPermissionsUserArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};


export type QueryUsersPermissionsUsersArgs = {
  filters?: InputMaybe<UsersPermissionsUserFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryWeekCompetenciesArgs = {
  filters?: InputMaybe<WeekCompetencyFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QueryWeekCompetencyArgs = {
  id?: InputMaybe<Scalars['ID']['input']>;
};

export type Reference = {
  __typename?: 'Reference';
  Title?: Maybe<Scalars['String']['output']>;
  challenge_sections?: Maybe<ChallengeSectionRelationResponseCollection>;
  created?: Maybe<AllUserEntityResponse>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  likes?: Maybe<AllUserRelationResponseCollection>;
  link: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type ReferenceChallenge_SectionsArgs = {
  filters?: InputMaybe<ChallengeSectionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type ReferenceLikesArgs = {
  filters?: InputMaybe<AllUserFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type ReferenceEntity = {
  __typename?: 'ReferenceEntity';
  attributes?: Maybe<Reference>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type ReferenceEntityResponse = {
  __typename?: 'ReferenceEntityResponse';
  data?: Maybe<ReferenceEntity>;
};

export type ReferenceEntityResponseCollection = {
  __typename?: 'ReferenceEntityResponseCollection';
  data: Array<ReferenceEntity>;
  meta: ResponseCollectionMeta;
};

export type ReferenceFiltersInput = {
  Title?: InputMaybe<StringFilterInput>;
  and?: InputMaybe<Array<InputMaybe<ReferenceFiltersInput>>>;
  challenge_sections?: InputMaybe<ChallengeSectionFiltersInput>;
  created?: InputMaybe<AllUserFiltersInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  likes?: InputMaybe<AllUserFiltersInput>;
  link?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<ReferenceFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<ReferenceFiltersInput>>>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type ReferenceInput = {
  Title?: InputMaybe<Scalars['String']['input']>;
  challenge_sections?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  created?: InputMaybe<Scalars['ID']['input']>;
  likes?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  link?: InputMaybe<Scalars['String']['input']>;
};

export type ReferenceRelationResponseCollection = {
  __typename?: 'ReferenceRelationResponseCollection';
  data: Array<ReferenceEntity>;
};

export type Repo = {
  __typename?: 'Repo';
  assignments?: Maybe<AssignmentRelationResponseCollection>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  github_analysis_details?: Maybe<GithubAnalysisDetailRelationResponseCollection>;
  github_branch_commit_history?: Maybe<GithubBranchCommitHistoryEntityResponse>;
  github_repos_metas?: Maybe<GithubReposMetaRelationResponseCollection>;
  github_user_meta?: Maybe<GithubUserMetaEntityResponse>;
  html_url: Scalars['String']['output'];
  run_number: Scalars['String']['output'];
  trainees?: Maybe<TraineeRelationResponseCollection>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  week: Scalars['String']['output'];
};


export type RepoAssignmentsArgs = {
  filters?: InputMaybe<AssignmentFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type RepoGithub_Analysis_DetailsArgs = {
  filters?: InputMaybe<GithubAnalysisDetailFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type RepoGithub_Repos_MetasArgs = {
  filters?: InputMaybe<GithubReposMetaFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type RepoTraineesArgs = {
  filters?: InputMaybe<TraineeFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type RepoEntity = {
  __typename?: 'RepoEntity';
  attributes?: Maybe<Repo>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type RepoEntityResponse = {
  __typename?: 'RepoEntityResponse';
  data?: Maybe<RepoEntity>;
};

export type RepoEntityResponseCollection = {
  __typename?: 'RepoEntityResponseCollection';
  data: Array<RepoEntity>;
  meta: ResponseCollectionMeta;
};

export type RepoFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<RepoFiltersInput>>>;
  assignments?: InputMaybe<AssignmentFiltersInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  github_analysis_details?: InputMaybe<GithubAnalysisDetailFiltersInput>;
  github_branch_commit_history?: InputMaybe<GithubBranchCommitHistoryFiltersInput>;
  github_repos_metas?: InputMaybe<GithubReposMetaFiltersInput>;
  github_user_meta?: InputMaybe<GithubUserMetaFiltersInput>;
  html_url?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<RepoFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<RepoFiltersInput>>>;
  run_number?: InputMaybe<StringFilterInput>;
  trainees?: InputMaybe<TraineeFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  week?: InputMaybe<StringFilterInput>;
};

export type RepoInput = {
  assignments?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  github_analysis_details?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  github_branch_commit_history?: InputMaybe<Scalars['ID']['input']>;
  github_repos_metas?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  github_user_meta?: InputMaybe<Scalars['ID']['input']>;
  html_url?: InputMaybe<Scalars['String']['input']>;
  run_number?: InputMaybe<Scalars['String']['input']>;
  trainees?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  week?: InputMaybe<Scalars['String']['input']>;
};

export type RepoRelationResponseCollection = {
  __typename?: 'RepoRelationResponseCollection';
  data: Array<RepoEntity>;
};

export type ResponseCollectionMeta = {
  __typename?: 'ResponseCollectionMeta';
  pagination: Pagination;
};

export type Review = {
  __typename?: 'Review';
  all_user?: Maybe<AllUserEntityResponse>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  grade?: Maybe<GradeEntityResponse>;
  prefilled_response?: Maybe<Scalars['JSON']['output']>;
  publishedAt?: Maybe<Scalars['DateTime']['output']>;
  review_category?: Maybe<ReviewCategoryEntityResponse>;
  review_responses?: Maybe<ReviewResponseRelationResponseCollection>;
  reviewers?: Maybe<ReviewerRelationResponseCollection>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type ReviewReview_ResponsesArgs = {
  filters?: InputMaybe<ReviewResponseFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type ReviewReviewersArgs = {
  filters?: InputMaybe<ReviewerFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type ReviewCategory = {
  __typename?: 'ReviewCategory';
  batch: Scalars['String']['output'];
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  form?: Maybe<FormEntityResponse>;
  mark?: Maybe<Scalars['Int']['output']>;
  name: Scalars['String']['output'];
  review_type: Enum_Reviewcategory_Review_Type;
  reviewers?: Maybe<ReviewerRelationResponseCollection>;
  reviews?: Maybe<ReviewRelationResponseCollection>;
  status: Enum_Reviewcategory_Status;
  unit: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type ReviewCategoryReviewersArgs = {
  filters?: InputMaybe<ReviewerFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type ReviewCategoryReviewsArgs = {
  filters?: InputMaybe<ReviewFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type ReviewCategoryEntity = {
  __typename?: 'ReviewCategoryEntity';
  attributes?: Maybe<ReviewCategory>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type ReviewCategoryEntityResponse = {
  __typename?: 'ReviewCategoryEntityResponse';
  data?: Maybe<ReviewCategoryEntity>;
};

export type ReviewCategoryEntityResponseCollection = {
  __typename?: 'ReviewCategoryEntityResponseCollection';
  data: Array<ReviewCategoryEntity>;
  meta: ResponseCollectionMeta;
};

export type ReviewCategoryFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<ReviewCategoryFiltersInput>>>;
  batch?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  form?: InputMaybe<FormFiltersInput>;
  id?: InputMaybe<IdFilterInput>;
  mark?: InputMaybe<IntFilterInput>;
  name?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<ReviewCategoryFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<ReviewCategoryFiltersInput>>>;
  review_type?: InputMaybe<StringFilterInput>;
  reviewers?: InputMaybe<ReviewerFiltersInput>;
  reviews?: InputMaybe<ReviewFiltersInput>;
  status?: InputMaybe<StringFilterInput>;
  unit?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type ReviewCategoryInput = {
  batch?: InputMaybe<Scalars['String']['input']>;
  form?: InputMaybe<Scalars['ID']['input']>;
  mark?: InputMaybe<Scalars['Int']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  review_type?: InputMaybe<Enum_Reviewcategory_Review_Type>;
  reviewers?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  reviews?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  status?: InputMaybe<Enum_Reviewcategory_Status>;
  unit?: InputMaybe<Scalars['String']['input']>;
};

export type ReviewCategoryRelationResponseCollection = {
  __typename?: 'ReviewCategoryRelationResponseCollection';
  data: Array<ReviewCategoryEntity>;
};

export type ReviewEntity = {
  __typename?: 'ReviewEntity';
  attributes?: Maybe<Review>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type ReviewEntityResponse = {
  __typename?: 'ReviewEntityResponse';
  data?: Maybe<ReviewEntity>;
};

export type ReviewEntityResponseCollection = {
  __typename?: 'ReviewEntityResponseCollection';
  data: Array<ReviewEntity>;
  meta: ResponseCollectionMeta;
};

export type ReviewFiltersInput = {
  all_user?: InputMaybe<AllUserFiltersInput>;
  and?: InputMaybe<Array<InputMaybe<ReviewFiltersInput>>>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  grade?: InputMaybe<GradeFiltersInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<ReviewFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<ReviewFiltersInput>>>;
  prefilled_response?: InputMaybe<JsonFilterInput>;
  publishedAt?: InputMaybe<DateTimeFilterInput>;
  review_category?: InputMaybe<ReviewCategoryFiltersInput>;
  review_responses?: InputMaybe<ReviewResponseFiltersInput>;
  reviewers?: InputMaybe<ReviewerFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type ReviewInput = {
  all_user?: InputMaybe<Scalars['ID']['input']>;
  grade?: InputMaybe<Scalars['ID']['input']>;
  prefilled_response?: InputMaybe<Scalars['JSON']['input']>;
  publishedAt?: InputMaybe<Scalars['DateTime']['input']>;
  review_category?: InputMaybe<Scalars['ID']['input']>;
  review_responses?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  reviewers?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
};

export type ReviewRelationResponseCollection = {
  __typename?: 'ReviewRelationResponseCollection';
  data: Array<ReviewEntity>;
};

export type ReviewResponse = {
  __typename?: 'ReviewResponse';
  content?: Maybe<Scalars['JSON']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  review?: Maybe<ReviewEntityResponse>;
  reviewer?: Maybe<ReviewerEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type ReviewResponseEntity = {
  __typename?: 'ReviewResponseEntity';
  attributes?: Maybe<ReviewResponse>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type ReviewResponseEntityResponse = {
  __typename?: 'ReviewResponseEntityResponse';
  data?: Maybe<ReviewResponseEntity>;
};

export type ReviewResponseEntityResponseCollection = {
  __typename?: 'ReviewResponseEntityResponseCollection';
  data: Array<ReviewResponseEntity>;
  meta: ResponseCollectionMeta;
};

export type ReviewResponseFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<ReviewResponseFiltersInput>>>;
  content?: InputMaybe<JsonFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<ReviewResponseFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<ReviewResponseFiltersInput>>>;
  review?: InputMaybe<ReviewFiltersInput>;
  reviewer?: InputMaybe<ReviewerFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type ReviewResponseInput = {
  content?: InputMaybe<Scalars['JSON']['input']>;
  review?: InputMaybe<Scalars['ID']['input']>;
  reviewer?: InputMaybe<Scalars['ID']['input']>;
};

export type ReviewResponseRelationResponseCollection = {
  __typename?: 'ReviewResponseRelationResponseCollection';
  data: Array<ReviewResponseEntity>;
};

export type Reviewer = {
  __typename?: 'Reviewer';
  Email: Scalars['String']['output'];
  all_user?: Maybe<AllUserEntityResponse>;
  assignment_categories?: Maybe<AssignmentCategoryRelationResponseCollection>;
  assignment_responses?: Maybe<AssignmentResponseRelationResponseCollection>;
  batches?: Maybe<BatchRelationResponseCollection>;
  best_submissions?: Maybe<BestSubmissionRelationResponseCollection>;
  challenge_documents?: Maybe<ChallengeDocumentRelationResponseCollection>;
  challenge_sections?: Maybe<ChallengeSectionRelationResponseCollection>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  review_categories?: Maybe<ReviewCategoryRelationResponseCollection>;
  review_responses?: Maybe<ReviewResponseRelationResponseCollection>;
  reviews?: Maybe<ReviewRelationResponseCollection>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type ReviewerAssignment_CategoriesArgs = {
  filters?: InputMaybe<AssignmentCategoryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type ReviewerAssignment_ResponsesArgs = {
  filters?: InputMaybe<AssignmentResponseFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type ReviewerBatchesArgs = {
  filters?: InputMaybe<BatchFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type ReviewerBest_SubmissionsArgs = {
  filters?: InputMaybe<BestSubmissionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type ReviewerChallenge_DocumentsArgs = {
  filters?: InputMaybe<ChallengeDocumentFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type ReviewerChallenge_SectionsArgs = {
  filters?: InputMaybe<ChallengeSectionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type ReviewerReview_CategoriesArgs = {
  filters?: InputMaybe<ReviewCategoryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type ReviewerReview_ResponsesArgs = {
  filters?: InputMaybe<ReviewResponseFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type ReviewerReviewsArgs = {
  filters?: InputMaybe<ReviewFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type ReviewerEntity = {
  __typename?: 'ReviewerEntity';
  attributes?: Maybe<Reviewer>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type ReviewerEntityResponse = {
  __typename?: 'ReviewerEntityResponse';
  data?: Maybe<ReviewerEntity>;
};

export type ReviewerEntityResponseCollection = {
  __typename?: 'ReviewerEntityResponseCollection';
  data: Array<ReviewerEntity>;
  meta: ResponseCollectionMeta;
};

export type ReviewerFiltersInput = {
  Email?: InputMaybe<StringFilterInput>;
  all_user?: InputMaybe<AllUserFiltersInput>;
  and?: InputMaybe<Array<InputMaybe<ReviewerFiltersInput>>>;
  assignment_categories?: InputMaybe<AssignmentCategoryFiltersInput>;
  assignment_responses?: InputMaybe<AssignmentResponseFiltersInput>;
  batches?: InputMaybe<BatchFiltersInput>;
  best_submissions?: InputMaybe<BestSubmissionFiltersInput>;
  challenge_documents?: InputMaybe<ChallengeDocumentFiltersInput>;
  challenge_sections?: InputMaybe<ChallengeSectionFiltersInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<ReviewerFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<ReviewerFiltersInput>>>;
  review_categories?: InputMaybe<ReviewCategoryFiltersInput>;
  review_responses?: InputMaybe<ReviewResponseFiltersInput>;
  reviews?: InputMaybe<ReviewFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type ReviewerInput = {
  Email?: InputMaybe<Scalars['String']['input']>;
  all_user?: InputMaybe<Scalars['ID']['input']>;
  assignment_categories?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  assignment_responses?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  batches?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  best_submissions?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  challenge_documents?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  challenge_sections?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  review_categories?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  review_responses?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  reviews?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
};

export type ReviewerRelationResponseCollection = {
  __typename?: 'ReviewerRelationResponseCollection';
  data: Array<ReviewerEntity>;
};

export type Rubric = {
  __typename?: 'Rubric';
  AdHoc?: Maybe<Scalars['JSON']['output']>;
  assignment_categories?: Maybe<AssignmentCategoryRelationResponseCollection>;
  content: Scalars['JSON']['output'];
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  name: Scalars['String']['output'];
  type?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type RubricAssignment_CategoriesArgs = {
  filters?: InputMaybe<AssignmentCategoryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type RubricEntity = {
  __typename?: 'RubricEntity';
  attributes?: Maybe<Rubric>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type RubricEntityResponse = {
  __typename?: 'RubricEntityResponse';
  data?: Maybe<RubricEntity>;
};

export type RubricEntityResponseCollection = {
  __typename?: 'RubricEntityResponseCollection';
  data: Array<RubricEntity>;
  meta: ResponseCollectionMeta;
};

export type RubricFiltersInput = {
  AdHoc?: InputMaybe<JsonFilterInput>;
  and?: InputMaybe<Array<InputMaybe<RubricFiltersInput>>>;
  assignment_categories?: InputMaybe<AssignmentCategoryFiltersInput>;
  content?: InputMaybe<JsonFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  name?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<RubricFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<RubricFiltersInput>>>;
  type?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type RubricInput = {
  AdHoc?: InputMaybe<Scalars['JSON']['input']>;
  assignment_categories?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  content?: InputMaybe<Scalars['JSON']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  type?: InputMaybe<Scalars['String']['input']>;
};

export type RubricRelationResponseCollection = {
  __typename?: 'RubricRelationResponseCollection';
  data: Array<RubricEntity>;
};

export type SmgCriterion = {
  __typename?: 'SmgCriterion';
  CriterionPromptTemplate?: Maybe<Scalars['String']['output']>;
  EditHistory?: Maybe<Scalars['JSON']['output']>;
  all_user?: Maybe<AllUserEntityResponse>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  layout?: Maybe<Scalars['JSON']['output']>;
  smg_criterion_metrics?: Maybe<SmgCriterionMetricRelationResponseCollection>;
  smg_prompt_templates?: Maybe<SmgPromptTemplateRelationResponseCollection>;
  tag?: Maybe<Scalars['String']['output']>;
  target?: Maybe<Scalars['String']['output']>;
  title?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type SmgCriterionSmg_Criterion_MetricsArgs = {
  filters?: InputMaybe<SmgCriterionMetricFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type SmgCriterionSmg_Prompt_TemplatesArgs = {
  filters?: InputMaybe<SmgPromptTemplateFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type SmgCriterionEntity = {
  __typename?: 'SmgCriterionEntity';
  attributes?: Maybe<SmgCriterion>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type SmgCriterionEntityResponse = {
  __typename?: 'SmgCriterionEntityResponse';
  data?: Maybe<SmgCriterionEntity>;
};

export type SmgCriterionEntityResponseCollection = {
  __typename?: 'SmgCriterionEntityResponseCollection';
  data: Array<SmgCriterionEntity>;
  meta: ResponseCollectionMeta;
};

export type SmgCriterionFiltersInput = {
  CriterionPromptTemplate?: InputMaybe<StringFilterInput>;
  EditHistory?: InputMaybe<JsonFilterInput>;
  all_user?: InputMaybe<AllUserFiltersInput>;
  and?: InputMaybe<Array<InputMaybe<SmgCriterionFiltersInput>>>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  layout?: InputMaybe<JsonFilterInput>;
  not?: InputMaybe<SmgCriterionFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<SmgCriterionFiltersInput>>>;
  smg_criterion_metrics?: InputMaybe<SmgCriterionMetricFiltersInput>;
  smg_prompt_templates?: InputMaybe<SmgPromptTemplateFiltersInput>;
  tag?: InputMaybe<StringFilterInput>;
  target?: InputMaybe<StringFilterInput>;
  title?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type SmgCriterionInput = {
  CriterionPromptTemplate?: InputMaybe<Scalars['String']['input']>;
  EditHistory?: InputMaybe<Scalars['JSON']['input']>;
  all_user?: InputMaybe<Scalars['ID']['input']>;
  layout?: InputMaybe<Scalars['JSON']['input']>;
  smg_criterion_metrics?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  smg_prompt_templates?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  tag?: InputMaybe<Scalars['String']['input']>;
  target?: InputMaybe<Scalars['String']['input']>;
  title?: InputMaybe<Scalars['String']['input']>;
};

export type SmgCriterionMetric = {
  __typename?: 'SmgCriterionMetric';
  EditHistory?: Maybe<Scalars['JSON']['output']>;
  content?: Maybe<Scalars['String']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  creator?: Maybe<AllUserEntityResponse>;
  layout?: Maybe<Scalars['JSON']['output']>;
  smg_criterion?: Maybe<SmgCriterionEntityResponse>;
  smg_criterion_results?: Maybe<SmgCriterionResultRelationResponseCollection>;
  smg_metric_prompts?: Maybe<SmgMetricPromptRelationResponseCollection>;
  smg_rubrics?: Maybe<SmgRubricRelationResponseCollection>;
  tag?: Maybe<Scalars['String']['output']>;
  target?: Maybe<Scalars['String']['output']>;
  title?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type SmgCriterionMetricSmg_Criterion_ResultsArgs = {
  filters?: InputMaybe<SmgCriterionResultFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type SmgCriterionMetricSmg_Metric_PromptsArgs = {
  filters?: InputMaybe<SmgMetricPromptFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type SmgCriterionMetricSmg_RubricsArgs = {
  filters?: InputMaybe<SmgRubricFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type SmgCriterionMetricEntity = {
  __typename?: 'SmgCriterionMetricEntity';
  attributes?: Maybe<SmgCriterionMetric>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type SmgCriterionMetricEntityResponse = {
  __typename?: 'SmgCriterionMetricEntityResponse';
  data?: Maybe<SmgCriterionMetricEntity>;
};

export type SmgCriterionMetricEntityResponseCollection = {
  __typename?: 'SmgCriterionMetricEntityResponseCollection';
  data: Array<SmgCriterionMetricEntity>;
  meta: ResponseCollectionMeta;
};

export type SmgCriterionMetricFiltersInput = {
  EditHistory?: InputMaybe<JsonFilterInput>;
  and?: InputMaybe<Array<InputMaybe<SmgCriterionMetricFiltersInput>>>;
  content?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  creator?: InputMaybe<AllUserFiltersInput>;
  id?: InputMaybe<IdFilterInput>;
  layout?: InputMaybe<JsonFilterInput>;
  not?: InputMaybe<SmgCriterionMetricFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<SmgCriterionMetricFiltersInput>>>;
  smg_criterion?: InputMaybe<SmgCriterionFiltersInput>;
  smg_criterion_results?: InputMaybe<SmgCriterionResultFiltersInput>;
  smg_metric_prompts?: InputMaybe<SmgMetricPromptFiltersInput>;
  smg_rubrics?: InputMaybe<SmgRubricFiltersInput>;
  tag?: InputMaybe<StringFilterInput>;
  target?: InputMaybe<StringFilterInput>;
  title?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type SmgCriterionMetricInput = {
  EditHistory?: InputMaybe<Scalars['JSON']['input']>;
  content?: InputMaybe<Scalars['String']['input']>;
  creator?: InputMaybe<Scalars['ID']['input']>;
  layout?: InputMaybe<Scalars['JSON']['input']>;
  smg_criterion?: InputMaybe<Scalars['ID']['input']>;
  smg_criterion_results?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  smg_metric_prompts?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  smg_rubrics?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  tag?: InputMaybe<Scalars['String']['input']>;
  target?: InputMaybe<Scalars['String']['input']>;
  title?: InputMaybe<Scalars['String']['input']>;
};

export type SmgCriterionMetricRelationResponseCollection = {
  __typename?: 'SmgCriterionMetricRelationResponseCollection';
  data: Array<SmgCriterionMetricEntity>;
};

export type SmgCriterionRelationResponseCollection = {
  __typename?: 'SmgCriterionRelationResponseCollection';
  data: Array<SmgCriterionEntity>;
};

export type SmgCriterionResult = {
  __typename?: 'SmgCriterionResult';
  assignment?: Maybe<AssignmentEntityResponse>;
  content?: Maybe<Scalars['JSON']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  smg_criterion_metric?: Maybe<SmgCriterionMetricEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type SmgCriterionResultEntity = {
  __typename?: 'SmgCriterionResultEntity';
  attributes?: Maybe<SmgCriterionResult>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type SmgCriterionResultEntityResponse = {
  __typename?: 'SmgCriterionResultEntityResponse';
  data?: Maybe<SmgCriterionResultEntity>;
};

export type SmgCriterionResultEntityResponseCollection = {
  __typename?: 'SmgCriterionResultEntityResponseCollection';
  data: Array<SmgCriterionResultEntity>;
  meta: ResponseCollectionMeta;
};

export type SmgCriterionResultFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<SmgCriterionResultFiltersInput>>>;
  assignment?: InputMaybe<AssignmentFiltersInput>;
  content?: InputMaybe<JsonFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<SmgCriterionResultFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<SmgCriterionResultFiltersInput>>>;
  smg_criterion_metric?: InputMaybe<SmgCriterionMetricFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type SmgCriterionResultInput = {
  assignment?: InputMaybe<Scalars['ID']['input']>;
  content?: InputMaybe<Scalars['JSON']['input']>;
  smg_criterion_metric?: InputMaybe<Scalars['ID']['input']>;
};

export type SmgCriterionResultRelationResponseCollection = {
  __typename?: 'SmgCriterionResultRelationResponseCollection';
  data: Array<SmgCriterionResultEntity>;
};

export type SmgDummyRubric = {
  __typename?: 'SmgDummyRubric';
  AdHoc?: Maybe<Scalars['JSON']['output']>;
  content?: Maybe<Scalars['JSON']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  name?: Maybe<Scalars['String']['output']>;
  smg_rubrics?: Maybe<SmgRubricRelationResponseCollection>;
  type?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type SmgDummyRubricSmg_RubricsArgs = {
  filters?: InputMaybe<SmgRubricFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type SmgDummyRubricEntity = {
  __typename?: 'SmgDummyRubricEntity';
  attributes?: Maybe<SmgDummyRubric>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type SmgDummyRubricEntityResponse = {
  __typename?: 'SmgDummyRubricEntityResponse';
  data?: Maybe<SmgDummyRubricEntity>;
};

export type SmgDummyRubricEntityResponseCollection = {
  __typename?: 'SmgDummyRubricEntityResponseCollection';
  data: Array<SmgDummyRubricEntity>;
  meta: ResponseCollectionMeta;
};

export type SmgDummyRubricFiltersInput = {
  AdHoc?: InputMaybe<JsonFilterInput>;
  and?: InputMaybe<Array<InputMaybe<SmgDummyRubricFiltersInput>>>;
  content?: InputMaybe<JsonFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  name?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<SmgDummyRubricFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<SmgDummyRubricFiltersInput>>>;
  smg_rubrics?: InputMaybe<SmgRubricFiltersInput>;
  type?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type SmgDummyRubricInput = {
  AdHoc?: InputMaybe<Scalars['JSON']['input']>;
  content?: InputMaybe<Scalars['JSON']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  smg_rubrics?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  type?: InputMaybe<Scalars['String']['input']>;
};

export type SmgMetricPrompt = {
  __typename?: 'SmgMetricPrompt';
  all_user?: Maybe<AllUserEntityResponse>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  editable?: Maybe<Scalars['String']['output']>;
  promptContent?: Maybe<Scalars['String']['output']>;
  smg_criterion_metrics?: Maybe<SmgCriterionMetricRelationResponseCollection>;
  smg_prompt_template?: Maybe<SmgPromptTemplateEntityResponse>;
  title?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type SmgMetricPromptSmg_Criterion_MetricsArgs = {
  filters?: InputMaybe<SmgCriterionMetricFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type SmgMetricPromptEntity = {
  __typename?: 'SmgMetricPromptEntity';
  attributes?: Maybe<SmgMetricPrompt>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type SmgMetricPromptEntityResponse = {
  __typename?: 'SmgMetricPromptEntityResponse';
  data?: Maybe<SmgMetricPromptEntity>;
};

export type SmgMetricPromptEntityResponseCollection = {
  __typename?: 'SmgMetricPromptEntityResponseCollection';
  data: Array<SmgMetricPromptEntity>;
  meta: ResponseCollectionMeta;
};

export type SmgMetricPromptFiltersInput = {
  all_user?: InputMaybe<AllUserFiltersInput>;
  and?: InputMaybe<Array<InputMaybe<SmgMetricPromptFiltersInput>>>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  editable?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<SmgMetricPromptFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<SmgMetricPromptFiltersInput>>>;
  promptContent?: InputMaybe<StringFilterInput>;
  smg_criterion_metrics?: InputMaybe<SmgCriterionMetricFiltersInput>;
  smg_prompt_template?: InputMaybe<SmgPromptTemplateFiltersInput>;
  title?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type SmgMetricPromptInput = {
  all_user?: InputMaybe<Scalars['ID']['input']>;
  editable?: InputMaybe<Scalars['String']['input']>;
  promptContent?: InputMaybe<Scalars['String']['input']>;
  smg_criterion_metrics?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  smg_prompt_template?: InputMaybe<Scalars['ID']['input']>;
  title?: InputMaybe<Scalars['String']['input']>;
};

export type SmgMetricPromptRelationResponseCollection = {
  __typename?: 'SmgMetricPromptRelationResponseCollection';
  data: Array<SmgMetricPromptEntity>;
};

export type SmgPromptTemplate = {
  __typename?: 'SmgPromptTemplate';
  EditHistory?: Maybe<Scalars['JSON']['output']>;
  Tag?: Maybe<Scalars['String']['output']>;
  all_user?: Maybe<AllUserEntityResponse>;
  content?: Maybe<Scalars['JSON']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  smg_criteria?: Maybe<SmgCriterionRelationResponseCollection>;
  smg_metric_prompts?: Maybe<SmgMetricPromptRelationResponseCollection>;
  target?: Maybe<Scalars['String']['output']>;
  title?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type SmgPromptTemplateSmg_CriteriaArgs = {
  filters?: InputMaybe<SmgCriterionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type SmgPromptTemplateSmg_Metric_PromptsArgs = {
  filters?: InputMaybe<SmgMetricPromptFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type SmgPromptTemplateEntity = {
  __typename?: 'SmgPromptTemplateEntity';
  attributes?: Maybe<SmgPromptTemplate>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type SmgPromptTemplateEntityResponse = {
  __typename?: 'SmgPromptTemplateEntityResponse';
  data?: Maybe<SmgPromptTemplateEntity>;
};

export type SmgPromptTemplateEntityResponseCollection = {
  __typename?: 'SmgPromptTemplateEntityResponseCollection';
  data: Array<SmgPromptTemplateEntity>;
  meta: ResponseCollectionMeta;
};

export type SmgPromptTemplateFiltersInput = {
  EditHistory?: InputMaybe<JsonFilterInput>;
  Tag?: InputMaybe<StringFilterInput>;
  all_user?: InputMaybe<AllUserFiltersInput>;
  and?: InputMaybe<Array<InputMaybe<SmgPromptTemplateFiltersInput>>>;
  content?: InputMaybe<JsonFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<SmgPromptTemplateFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<SmgPromptTemplateFiltersInput>>>;
  smg_criteria?: InputMaybe<SmgCriterionFiltersInput>;
  smg_metric_prompts?: InputMaybe<SmgMetricPromptFiltersInput>;
  target?: InputMaybe<StringFilterInput>;
  title?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type SmgPromptTemplateInput = {
  EditHistory?: InputMaybe<Scalars['JSON']['input']>;
  Tag?: InputMaybe<Scalars['String']['input']>;
  all_user?: InputMaybe<Scalars['ID']['input']>;
  content?: InputMaybe<Scalars['JSON']['input']>;
  smg_criteria?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  smg_metric_prompts?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  target?: InputMaybe<Scalars['String']['input']>;
  title?: InputMaybe<Scalars['String']['input']>;
};

export type SmgPromptTemplateRelationResponseCollection = {
  __typename?: 'SmgPromptTemplateRelationResponseCollection';
  data: Array<SmgPromptTemplateEntity>;
};

export type SmgRubric = {
  __typename?: 'SmgRubric';
  assignment_categories?: Maybe<AssignmentCategoryRelationResponseCollection>;
  content?: Maybe<Scalars['String']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  creator?: Maybe<AllUserEntityResponse>;
  layout?: Maybe<Scalars['JSON']['output']>;
  smg_criterion_metrics?: Maybe<SmgCriterionMetricRelationResponseCollection>;
  smg_dummy_rubric?: Maybe<SmgDummyRubricEntityResponse>;
  tag?: Maybe<Scalars['String']['output']>;
  target?: Maybe<Scalars['String']['output']>;
  title: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type SmgRubricAssignment_CategoriesArgs = {
  filters?: InputMaybe<AssignmentCategoryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type SmgRubricSmg_Criterion_MetricsArgs = {
  filters?: InputMaybe<SmgCriterionMetricFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type SmgRubricEntity = {
  __typename?: 'SmgRubricEntity';
  attributes?: Maybe<SmgRubric>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type SmgRubricEntityResponse = {
  __typename?: 'SmgRubricEntityResponse';
  data?: Maybe<SmgRubricEntity>;
};

export type SmgRubricEntityResponseCollection = {
  __typename?: 'SmgRubricEntityResponseCollection';
  data: Array<SmgRubricEntity>;
  meta: ResponseCollectionMeta;
};

export type SmgRubricFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<SmgRubricFiltersInput>>>;
  assignment_categories?: InputMaybe<AssignmentCategoryFiltersInput>;
  content?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  creator?: InputMaybe<AllUserFiltersInput>;
  id?: InputMaybe<IdFilterInput>;
  layout?: InputMaybe<JsonFilterInput>;
  not?: InputMaybe<SmgRubricFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<SmgRubricFiltersInput>>>;
  smg_criterion_metrics?: InputMaybe<SmgCriterionMetricFiltersInput>;
  smg_dummy_rubric?: InputMaybe<SmgDummyRubricFiltersInput>;
  tag?: InputMaybe<StringFilterInput>;
  target?: InputMaybe<StringFilterInput>;
  title?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type SmgRubricInput = {
  assignment_categories?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  content?: InputMaybe<Scalars['String']['input']>;
  creator?: InputMaybe<Scalars['ID']['input']>;
  layout?: InputMaybe<Scalars['JSON']['input']>;
  smg_criterion_metrics?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  smg_dummy_rubric?: InputMaybe<Scalars['ID']['input']>;
  tag?: InputMaybe<Scalars['String']['input']>;
  target?: InputMaybe<Scalars['String']['input']>;
  title?: InputMaybe<Scalars['String']['input']>;
};

export type SmgRubricRelationResponseCollection = {
  __typename?: 'SmgRubricRelationResponseCollection';
  data: Array<SmgRubricEntity>;
};

export type StringFilterInput = {
  and?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
  between?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
  contains?: InputMaybe<Scalars['String']['input']>;
  containsi?: InputMaybe<Scalars['String']['input']>;
  endsWith?: InputMaybe<Scalars['String']['input']>;
  eq?: InputMaybe<Scalars['String']['input']>;
  gt?: InputMaybe<Scalars['String']['input']>;
  gte?: InputMaybe<Scalars['String']['input']>;
  in?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
  lt?: InputMaybe<Scalars['String']['input']>;
  lte?: InputMaybe<Scalars['String']['input']>;
  ne?: InputMaybe<Scalars['String']['input']>;
  not?: InputMaybe<StringFilterInput>;
  notContains?: InputMaybe<Scalars['String']['input']>;
  notContainsi?: InputMaybe<Scalars['String']['input']>;
  notIn?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
  notNull?: InputMaybe<Scalars['Boolean']['input']>;
  null?: InputMaybe<Scalars['Boolean']['input']>;
  or?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
  startsWith?: InputMaybe<Scalars['String']['input']>;
};

export type TinderAssetGeneration = {
  __typename?: 'TinderAssetGeneration';
  applyLink?: Maybe<Scalars['String']['output']>;
  attributes?: Maybe<Scalars['JSON']['output']>;
  clstatus?: Maybe<Scalars['String']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  cvstatus?: Maybe<Scalars['String']['output']>;
  folderLink?: Maybe<Scalars['String']['output']>;
  metadata?: Maybe<Scalars['JSON']['output']>;
  publishedAt?: Maybe<Scalars['DateTime']['output']>;
  slug?: Maybe<Scalars['String']['output']>;
  tags?: Maybe<Scalars['String']['output']>;
  tinder_user_reaction?: Maybe<TinderUserReactionEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type TinderAssetGenerationEntity = {
  __typename?: 'TinderAssetGenerationEntity';
  attributes?: Maybe<TinderAssetGeneration>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type TinderAssetGenerationEntityResponse = {
  __typename?: 'TinderAssetGenerationEntityResponse';
  data?: Maybe<TinderAssetGenerationEntity>;
};

export type TinderAssetGenerationEntityResponseCollection = {
  __typename?: 'TinderAssetGenerationEntityResponseCollection';
  data: Array<TinderAssetGenerationEntity>;
  meta: ResponseCollectionMeta;
};

export type TinderAssetGenerationFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<TinderAssetGenerationFiltersInput>>>;
  applyLink?: InputMaybe<StringFilterInput>;
  applyLinkUID?: InputMaybe<StringFilterInput>;
  attributes?: InputMaybe<JsonFilterInput>;
  clstatus?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  cvstatus?: InputMaybe<StringFilterInput>;
  folderLink?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  metadata?: InputMaybe<JsonFilterInput>;
  not?: InputMaybe<TinderAssetGenerationFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<TinderAssetGenerationFiltersInput>>>;
  publishedAt?: InputMaybe<DateTimeFilterInput>;
  slug?: InputMaybe<StringFilterInput>;
  tags?: InputMaybe<StringFilterInput>;
  tinder_user_reaction?: InputMaybe<TinderUserReactionFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type TinderAssetGenerationInput = {
  applyLink?: InputMaybe<Scalars['String']['input']>;
  applyLinkUID?: InputMaybe<Scalars['String']['input']>;
  attributes?: InputMaybe<Scalars['JSON']['input']>;
  clstatus?: InputMaybe<Scalars['String']['input']>;
  cvstatus?: InputMaybe<Scalars['String']['input']>;
  folderLink?: InputMaybe<Scalars['String']['input']>;
  metadata?: InputMaybe<Scalars['JSON']['input']>;
  publishedAt?: InputMaybe<Scalars['DateTime']['input']>;
  slug?: InputMaybe<Scalars['String']['input']>;
  tags?: InputMaybe<Scalars['String']['input']>;
  tinder_user_reaction?: InputMaybe<Scalars['ID']['input']>;
};

export type TinderJobProfile = {
  __typename?: 'TinderJobProfile';
  applyLink?: Maybe<Scalars['String']['output']>;
  attributes?: Maybe<Scalars['JSON']['output']>;
  category?: Maybe<Scalars['String']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  endDate?: Maybe<Scalars['DateTime']['output']>;
  job?: Maybe<JobEntityResponse>;
  label?: Maybe<Scalars['String']['output']>;
  level?: Maybe<Scalars['String']['output']>;
  location?: Maybe<Scalars['String']['output']>;
  metadata?: Maybe<Scalars['JSON']['output']>;
  summary?: Maybe<Scalars['String']['output']>;
  tags?: Maybe<Scalars['String']['output']>;
  tinder_user_reactions?: Maybe<TinderUserReactionRelationResponseCollection>;
  title?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type TinderJobProfileTinder_User_ReactionsArgs = {
  filters?: InputMaybe<TinderUserReactionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type TinderJobProfileEntity = {
  __typename?: 'TinderJobProfileEntity';
  attributes?: Maybe<TinderJobProfile>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type TinderJobProfileEntityResponse = {
  __typename?: 'TinderJobProfileEntityResponse';
  data?: Maybe<TinderJobProfileEntity>;
};

export type TinderJobProfileEntityResponseCollection = {
  __typename?: 'TinderJobProfileEntityResponseCollection';
  data: Array<TinderJobProfileEntity>;
  meta: ResponseCollectionMeta;
};

export type TinderJobProfileFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<TinderJobProfileFiltersInput>>>;
  applyLink?: InputMaybe<StringFilterInput>;
  attributes?: InputMaybe<JsonFilterInput>;
  category?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  endDate?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  job?: InputMaybe<JobFiltersInput>;
  label?: InputMaybe<StringFilterInput>;
  level?: InputMaybe<StringFilterInput>;
  location?: InputMaybe<StringFilterInput>;
  metadata?: InputMaybe<JsonFilterInput>;
  not?: InputMaybe<TinderJobProfileFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<TinderJobProfileFiltersInput>>>;
  summary?: InputMaybe<StringFilterInput>;
  tags?: InputMaybe<StringFilterInput>;
  tinder_user_reactions?: InputMaybe<TinderUserReactionFiltersInput>;
  title?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type TinderJobProfileInput = {
  applyLink?: InputMaybe<Scalars['String']['input']>;
  attributes?: InputMaybe<Scalars['JSON']['input']>;
  category?: InputMaybe<Scalars['String']['input']>;
  endDate?: InputMaybe<Scalars['DateTime']['input']>;
  job?: InputMaybe<Scalars['ID']['input']>;
  label?: InputMaybe<Scalars['String']['input']>;
  level?: InputMaybe<Scalars['String']['input']>;
  location?: InputMaybe<Scalars['String']['input']>;
  metadata?: InputMaybe<Scalars['JSON']['input']>;
  summary?: InputMaybe<Scalars['String']['input']>;
  tags?: InputMaybe<Scalars['String']['input']>;
  tinder_user_reactions?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  title?: InputMaybe<Scalars['String']['input']>;
};

export type TinderJobProfileRelationResponseCollection = {
  __typename?: 'TinderJobProfileRelationResponseCollection';
  data: Array<TinderJobProfileEntity>;
};

export type TinderUserJobMatch = {
  __typename?: 'TinderUserJobMatch';
  category?: Maybe<Scalars['String']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  match_attributes?: Maybe<Scalars['JSON']['output']>;
  match_summary?: Maybe<Scalars['String']['output']>;
  metadata?: Maybe<Scalars['JSON']['output']>;
  publishedAt?: Maybe<Scalars['DateTime']['output']>;
  score?: Maybe<Scalars['Int']['output']>;
  slug?: Maybe<Scalars['String']['output']>;
  tags?: Maybe<Scalars['String']['output']>;
  tinder_user_profiles?: Maybe<TinderUserProfileRelationResponseCollection>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type TinderUserJobMatchTinder_User_ProfilesArgs = {
  filters?: InputMaybe<TinderUserProfileFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type TinderUserJobMatchEntity = {
  __typename?: 'TinderUserJobMatchEntity';
  attributes?: Maybe<TinderUserJobMatch>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type TinderUserJobMatchEntityResponse = {
  __typename?: 'TinderUserJobMatchEntityResponse';
  data?: Maybe<TinderUserJobMatchEntity>;
};

export type TinderUserJobMatchEntityResponseCollection = {
  __typename?: 'TinderUserJobMatchEntityResponseCollection';
  data: Array<TinderUserJobMatchEntity>;
  meta: ResponseCollectionMeta;
};

export type TinderUserJobMatchFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<TinderUserJobMatchFiltersInput>>>;
  category?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  match_attributes?: InputMaybe<JsonFilterInput>;
  match_summary?: InputMaybe<StringFilterInput>;
  metadata?: InputMaybe<JsonFilterInput>;
  not?: InputMaybe<TinderUserJobMatchFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<TinderUserJobMatchFiltersInput>>>;
  publishedAt?: InputMaybe<DateTimeFilterInput>;
  score?: InputMaybe<IntFilterInput>;
  slug?: InputMaybe<StringFilterInput>;
  tags?: InputMaybe<StringFilterInput>;
  tinder_user_profiles?: InputMaybe<TinderUserProfileFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type TinderUserJobMatchInput = {
  category?: InputMaybe<Scalars['String']['input']>;
  match_attributes?: InputMaybe<Scalars['JSON']['input']>;
  match_summary?: InputMaybe<Scalars['String']['input']>;
  metadata?: InputMaybe<Scalars['JSON']['input']>;
  publishedAt?: InputMaybe<Scalars['DateTime']['input']>;
  score?: InputMaybe<Scalars['Int']['input']>;
  slug?: InputMaybe<Scalars['String']['input']>;
  tags?: InputMaybe<Scalars['String']['input']>;
  tinder_user_profiles?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
};

export type TinderUserJobMatchRelationResponseCollection = {
  __typename?: 'TinderUserJobMatchRelationResponseCollection';
  data: Array<TinderUserJobMatchEntity>;
};

export type TinderUserProfile = {
  __typename?: 'TinderUserProfile';
  all_users?: Maybe<AllUserRelationResponseCollection>;
  attributes?: Maybe<Scalars['JSON']['output']>;
  category?: Maybe<Scalars['String']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  credibility?: Maybe<Enum_Tinderuserprofile_Credibility>;
  metadata?: Maybe<Scalars['JSON']['output']>;
  profile_type?: Maybe<Enum_Tinderuserprofile_Profile_Type>;
  slug?: Maybe<Scalars['String']['output']>;
  summary?: Maybe<Scalars['String']['output']>;
  tags?: Maybe<Scalars['String']['output']>;
  tinder_user_job_matches?: Maybe<TinderUserJobMatchRelationResponseCollection>;
  title?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type TinderUserProfileAll_UsersArgs = {
  filters?: InputMaybe<AllUserFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type TinderUserProfileTinder_User_Job_MatchesArgs = {
  filters?: InputMaybe<TinderUserJobMatchFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type TinderUserProfileEntity = {
  __typename?: 'TinderUserProfileEntity';
  attributes?: Maybe<TinderUserProfile>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type TinderUserProfileEntityResponse = {
  __typename?: 'TinderUserProfileEntityResponse';
  data?: Maybe<TinderUserProfileEntity>;
};

export type TinderUserProfileEntityResponseCollection = {
  __typename?: 'TinderUserProfileEntityResponseCollection';
  data: Array<TinderUserProfileEntity>;
  meta: ResponseCollectionMeta;
};

export type TinderUserProfileFiltersInput = {
  all_users?: InputMaybe<AllUserFiltersInput>;
  and?: InputMaybe<Array<InputMaybe<TinderUserProfileFiltersInput>>>;
  attributes?: InputMaybe<JsonFilterInput>;
  category?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  credibility?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  metadata?: InputMaybe<JsonFilterInput>;
  not?: InputMaybe<TinderUserProfileFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<TinderUserProfileFiltersInput>>>;
  profile_type?: InputMaybe<StringFilterInput>;
  slug?: InputMaybe<StringFilterInput>;
  summary?: InputMaybe<StringFilterInput>;
  tags?: InputMaybe<StringFilterInput>;
  tinder_user_job_matches?: InputMaybe<TinderUserJobMatchFiltersInput>;
  title?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type TinderUserProfileInput = {
  all_users?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  attributes?: InputMaybe<Scalars['JSON']['input']>;
  category?: InputMaybe<Scalars['String']['input']>;
  credibility?: InputMaybe<Enum_Tinderuserprofile_Credibility>;
  metadata?: InputMaybe<Scalars['JSON']['input']>;
  profile_type?: InputMaybe<Enum_Tinderuserprofile_Profile_Type>;
  slug?: InputMaybe<Scalars['String']['input']>;
  summary?: InputMaybe<Scalars['String']['input']>;
  tags?: InputMaybe<Scalars['String']['input']>;
  tinder_user_job_matches?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  title?: InputMaybe<Scalars['String']['input']>;
};

export type TinderUserProfileRelationResponseCollection = {
  __typename?: 'TinderUserProfileRelationResponseCollection';
  data: Array<TinderUserProfileEntity>;
};

export type TinderUserReaction = {
  __typename?: 'TinderUserReaction';
  all_user?: Maybe<AllUserEntityResponse>;
  category?: Maybe<Scalars['String']['output']>;
  comment?: Maybe<Scalars['String']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  metadata?: Maybe<Scalars['JSON']['output']>;
  overall_reaction?: Maybe<Enum_Tinderuserreaction_Overall_Reaction>;
  reaction_attributes?: Maybe<Scalars['JSON']['output']>;
  score?: Maybe<Scalars['Int']['output']>;
  slug?: Maybe<Scalars['String']['output']>;
  tinder_asset_generation?: Maybe<TinderAssetGenerationEntityResponse>;
  tinder_job_profile?: Maybe<TinderJobProfileEntityResponse>;
  tinder_user_profile?: Maybe<TinderUserProfileEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type TinderUserReactionEntity = {
  __typename?: 'TinderUserReactionEntity';
  attributes?: Maybe<TinderUserReaction>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type TinderUserReactionEntityResponse = {
  __typename?: 'TinderUserReactionEntityResponse';
  data?: Maybe<TinderUserReactionEntity>;
};

export type TinderUserReactionEntityResponseCollection = {
  __typename?: 'TinderUserReactionEntityResponseCollection';
  data: Array<TinderUserReactionEntity>;
  meta: ResponseCollectionMeta;
};

export type TinderUserReactionFiltersInput = {
  all_user?: InputMaybe<AllUserFiltersInput>;
  and?: InputMaybe<Array<InputMaybe<TinderUserReactionFiltersInput>>>;
  category?: InputMaybe<StringFilterInput>;
  comment?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  metadata?: InputMaybe<JsonFilterInput>;
  not?: InputMaybe<TinderUserReactionFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<TinderUserReactionFiltersInput>>>;
  overall_reaction?: InputMaybe<StringFilterInput>;
  reaction_attributes?: InputMaybe<JsonFilterInput>;
  score?: InputMaybe<IntFilterInput>;
  slug?: InputMaybe<StringFilterInput>;
  tinder_asset_generation?: InputMaybe<TinderAssetGenerationFiltersInput>;
  tinder_job_profile?: InputMaybe<TinderJobProfileFiltersInput>;
  tinder_user_profile?: InputMaybe<TinderUserProfileFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type TinderUserReactionInput = {
  all_user?: InputMaybe<Scalars['ID']['input']>;
  category?: InputMaybe<Scalars['String']['input']>;
  comment?: InputMaybe<Scalars['String']['input']>;
  metadata?: InputMaybe<Scalars['JSON']['input']>;
  overall_reaction?: InputMaybe<Enum_Tinderuserreaction_Overall_Reaction>;
  reaction_attributes?: InputMaybe<Scalars['JSON']['input']>;
  score?: InputMaybe<Scalars['Int']['input']>;
  slug?: InputMaybe<Scalars['String']['input']>;
  tinder_asset_generation?: InputMaybe<Scalars['ID']['input']>;
  tinder_job_profile?: InputMaybe<Scalars['ID']['input']>;
  tinder_user_profile?: InputMaybe<Scalars['ID']['input']>;
};

export type TinderUserReactionRelationResponseCollection = {
  __typename?: 'TinderUserReactionRelationResponseCollection';
  data: Array<TinderUserReactionEntity>;
};

export type Trainee = {
  __typename?: 'Trainee';
  Status?: Maybe<Enum_Trainee_Status>;
  all_user?: Maybe<AllUserEntityResponse>;
  assignment_peer_gradings?: Maybe<AssignmentPeerGradingRelationResponseCollection>;
  assignment_submission_summaries?: Maybe<AssignmentSubmissionSummaryRelationResponseCollection>;
  assignments?: Maybe<AssignmentRelationResponseCollection>;
  batch?: Maybe<BatchEntityResponse>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  email: Scalars['String']['output'];
  github_analysis_details?: Maybe<GithubAnalysisDetailRelationResponseCollection>;
  github_branch_commit_histories?: Maybe<GithubBranchCommitHistoryRelationResponseCollection>;
  github_repos_metas?: Maybe<GithubReposMetaRelationResponseCollection>;
  github_user_metas?: Maybe<GithubUserMetaRelationResponseCollection>;
  gmeets?: Maybe<GmeetRelationResponseCollection>;
  job_assets?: Maybe<JobAssetRelationResponseCollection>;
  job_matches?: Maybe<JobMatchRelationResponseCollection>;
  job_trainees?: Maybe<JobTraineeRelationResponseCollection>;
  portfolio?: Maybe<PortfolioEntityResponse>;
  publishedAt?: Maybe<Scalars['DateTime']['output']>;
  repos?: Maybe<RepoRelationResponseCollection>;
  trainee_id: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  week_competencies?: Maybe<WeekCompetencyRelationResponseCollection>;
};


export type TraineeAssignment_Peer_GradingsArgs = {
  filters?: InputMaybe<AssignmentPeerGradingFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type TraineeAssignment_Submission_SummariesArgs = {
  filters?: InputMaybe<AssignmentSubmissionSummaryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type TraineeAssignmentsArgs = {
  filters?: InputMaybe<AssignmentFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type TraineeGithub_Analysis_DetailsArgs = {
  filters?: InputMaybe<GithubAnalysisDetailFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type TraineeGithub_Branch_Commit_HistoriesArgs = {
  filters?: InputMaybe<GithubBranchCommitHistoryFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type TraineeGithub_Repos_MetasArgs = {
  filters?: InputMaybe<GithubReposMetaFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type TraineeGithub_User_MetasArgs = {
  filters?: InputMaybe<GithubUserMetaFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type TraineeGmeetsArgs = {
  filters?: InputMaybe<GmeetFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type TraineeJob_AssetsArgs = {
  filters?: InputMaybe<JobAssetFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type TraineeJob_MatchesArgs = {
  filters?: InputMaybe<JobMatchFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type TraineeJob_TraineesArgs = {
  filters?: InputMaybe<JobTraineeFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type TraineeReposArgs = {
  filters?: InputMaybe<RepoFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type TraineeWeek_CompetenciesArgs = {
  filters?: InputMaybe<WeekCompetencyFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  publicationState?: InputMaybe<PublicationState>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type TraineeEntity = {
  __typename?: 'TraineeEntity';
  attributes?: Maybe<Trainee>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type TraineeEntityResponse = {
  __typename?: 'TraineeEntityResponse';
  data?: Maybe<TraineeEntity>;
};

export type TraineeEntityResponseCollection = {
  __typename?: 'TraineeEntityResponseCollection';
  data: Array<TraineeEntity>;
  meta: ResponseCollectionMeta;
};

export type TraineeFiltersInput = {
  Status?: InputMaybe<StringFilterInput>;
  all_user?: InputMaybe<AllUserFiltersInput>;
  and?: InputMaybe<Array<InputMaybe<TraineeFiltersInput>>>;
  assignment_peer_gradings?: InputMaybe<AssignmentPeerGradingFiltersInput>;
  assignment_submission_summaries?: InputMaybe<AssignmentSubmissionSummaryFiltersInput>;
  assignments?: InputMaybe<AssignmentFiltersInput>;
  batch?: InputMaybe<BatchFiltersInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  email?: InputMaybe<StringFilterInput>;
  github_analysis_details?: InputMaybe<GithubAnalysisDetailFiltersInput>;
  github_branch_commit_histories?: InputMaybe<GithubBranchCommitHistoryFiltersInput>;
  github_repos_metas?: InputMaybe<GithubReposMetaFiltersInput>;
  github_user_metas?: InputMaybe<GithubUserMetaFiltersInput>;
  gmeets?: InputMaybe<GmeetFiltersInput>;
  id?: InputMaybe<IdFilterInput>;
  job_assets?: InputMaybe<JobAssetFiltersInput>;
  job_matches?: InputMaybe<JobMatchFiltersInput>;
  job_trainees?: InputMaybe<JobTraineeFiltersInput>;
  not?: InputMaybe<TraineeFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<TraineeFiltersInput>>>;
  portfolio?: InputMaybe<PortfolioFiltersInput>;
  publishedAt?: InputMaybe<DateTimeFilterInput>;
  repos?: InputMaybe<RepoFiltersInput>;
  trainee_id?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  week_competencies?: InputMaybe<WeekCompetencyFiltersInput>;
};

export type TraineeInput = {
  Status?: InputMaybe<Enum_Trainee_Status>;
  all_user?: InputMaybe<Scalars['ID']['input']>;
  assignment_peer_gradings?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  assignment_submission_summaries?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  assignments?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  batch?: InputMaybe<Scalars['ID']['input']>;
  email?: InputMaybe<Scalars['String']['input']>;
  github_analysis_details?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  github_branch_commit_histories?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  github_repos_metas?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  github_user_metas?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  gmeets?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  job_assets?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  job_matches?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  job_trainees?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  portfolio?: InputMaybe<Scalars['ID']['input']>;
  publishedAt?: InputMaybe<Scalars['DateTime']['input']>;
  repos?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  trainee_id?: InputMaybe<Scalars['String']['input']>;
  week_competencies?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
};

export type TraineeRelationResponseCollection = {
  __typename?: 'TraineeRelationResponseCollection';
  data: Array<TraineeEntity>;
};

export type UploadFile = {
  __typename?: 'UploadFile';
  alternativeText?: Maybe<Scalars['String']['output']>;
  caption?: Maybe<Scalars['String']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  ext?: Maybe<Scalars['String']['output']>;
  formats?: Maybe<Scalars['JSON']['output']>;
  hash: Scalars['String']['output'];
  height?: Maybe<Scalars['Int']['output']>;
  mime: Scalars['String']['output'];
  name: Scalars['String']['output'];
  previewUrl?: Maybe<Scalars['String']['output']>;
  provider: Scalars['String']['output'];
  provider_metadata?: Maybe<Scalars['JSON']['output']>;
  related?: Maybe<Array<Maybe<GenericMorph>>>;
  size: Scalars['Float']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  url: Scalars['String']['output'];
  width?: Maybe<Scalars['Int']['output']>;
};

export type UploadFileEntity = {
  __typename?: 'UploadFileEntity';
  attributes?: Maybe<UploadFile>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type UploadFileEntityResponse = {
  __typename?: 'UploadFileEntityResponse';
  data?: Maybe<UploadFileEntity>;
};

export type UploadFileEntityResponseCollection = {
  __typename?: 'UploadFileEntityResponseCollection';
  data: Array<UploadFileEntity>;
  meta: ResponseCollectionMeta;
};

export type UploadFileFiltersInput = {
  alternativeText?: InputMaybe<StringFilterInput>;
  and?: InputMaybe<Array<InputMaybe<UploadFileFiltersInput>>>;
  caption?: InputMaybe<StringFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  ext?: InputMaybe<StringFilterInput>;
  formats?: InputMaybe<JsonFilterInput>;
  hash?: InputMaybe<StringFilterInput>;
  height?: InputMaybe<IntFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  mime?: InputMaybe<StringFilterInput>;
  name?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<UploadFileFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<UploadFileFiltersInput>>>;
  previewUrl?: InputMaybe<StringFilterInput>;
  provider?: InputMaybe<StringFilterInput>;
  provider_metadata?: InputMaybe<JsonFilterInput>;
  size?: InputMaybe<FloatFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  url?: InputMaybe<StringFilterInput>;
  width?: InputMaybe<IntFilterInput>;
};

export type UploadFileInput = {
  alternativeText?: InputMaybe<Scalars['String']['input']>;
  caption?: InputMaybe<Scalars['String']['input']>;
  ext?: InputMaybe<Scalars['String']['input']>;
  formats?: InputMaybe<Scalars['JSON']['input']>;
  hash?: InputMaybe<Scalars['String']['input']>;
  height?: InputMaybe<Scalars['Int']['input']>;
  mime?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  previewUrl?: InputMaybe<Scalars['String']['input']>;
  provider?: InputMaybe<Scalars['String']['input']>;
  provider_metadata?: InputMaybe<Scalars['JSON']['input']>;
  size?: InputMaybe<Scalars['Float']['input']>;
  url?: InputMaybe<Scalars['String']['input']>;
  width?: InputMaybe<Scalars['Int']['input']>;
};

export type UsersPermissionsCreateRolePayload = {
  __typename?: 'UsersPermissionsCreateRolePayload';
  ok: Scalars['Boolean']['output'];
};

export type UsersPermissionsDeleteRolePayload = {
  __typename?: 'UsersPermissionsDeleteRolePayload';
  ok: Scalars['Boolean']['output'];
};

export type UsersPermissionsLoginInput = {
  identifier: Scalars['String']['input'];
  password: Scalars['String']['input'];
  provider?: Scalars['String']['input'];
};

export type UsersPermissionsLoginPayload = {
  __typename?: 'UsersPermissionsLoginPayload';
  jwt?: Maybe<Scalars['String']['output']>;
  user: UsersPermissionsMe;
};

export type UsersPermissionsMe = {
  __typename?: 'UsersPermissionsMe';
  blocked?: Maybe<Scalars['Boolean']['output']>;
  confirmed?: Maybe<Scalars['Boolean']['output']>;
  email?: Maybe<Scalars['String']['output']>;
  id: Scalars['ID']['output'];
  role?: Maybe<UsersPermissionsMeRole>;
  username: Scalars['String']['output'];
};

export type UsersPermissionsMeRole = {
  __typename?: 'UsersPermissionsMeRole';
  description?: Maybe<Scalars['String']['output']>;
  id: Scalars['ID']['output'];
  name: Scalars['String']['output'];
  type?: Maybe<Scalars['String']['output']>;
};

export type UsersPermissionsPasswordPayload = {
  __typename?: 'UsersPermissionsPasswordPayload';
  ok: Scalars['Boolean']['output'];
};

export type UsersPermissionsPermission = {
  __typename?: 'UsersPermissionsPermission';
  action: Scalars['String']['output'];
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  role?: Maybe<UsersPermissionsRoleEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type UsersPermissionsPermissionEntity = {
  __typename?: 'UsersPermissionsPermissionEntity';
  attributes?: Maybe<UsersPermissionsPermission>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type UsersPermissionsPermissionFiltersInput = {
  action?: InputMaybe<StringFilterInput>;
  and?: InputMaybe<Array<InputMaybe<UsersPermissionsPermissionFiltersInput>>>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<UsersPermissionsPermissionFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<UsersPermissionsPermissionFiltersInput>>>;
  role?: InputMaybe<UsersPermissionsRoleFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
};

export type UsersPermissionsPermissionRelationResponseCollection = {
  __typename?: 'UsersPermissionsPermissionRelationResponseCollection';
  data: Array<UsersPermissionsPermissionEntity>;
};

export type UsersPermissionsRegisterInput = {
  email: Scalars['String']['input'];
  password: Scalars['String']['input'];
  username: Scalars['String']['input'];
};

export type UsersPermissionsRole = {
  __typename?: 'UsersPermissionsRole';
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  description?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  permissions?: Maybe<UsersPermissionsPermissionRelationResponseCollection>;
  type?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  users?: Maybe<UsersPermissionsUserRelationResponseCollection>;
};


export type UsersPermissionsRolePermissionsArgs = {
  filters?: InputMaybe<UsersPermissionsPermissionFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type UsersPermissionsRoleUsersArgs = {
  filters?: InputMaybe<UsersPermissionsUserFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type UsersPermissionsRoleEntity = {
  __typename?: 'UsersPermissionsRoleEntity';
  attributes?: Maybe<UsersPermissionsRole>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type UsersPermissionsRoleEntityResponse = {
  __typename?: 'UsersPermissionsRoleEntityResponse';
  data?: Maybe<UsersPermissionsRoleEntity>;
};

export type UsersPermissionsRoleEntityResponseCollection = {
  __typename?: 'UsersPermissionsRoleEntityResponseCollection';
  data: Array<UsersPermissionsRoleEntity>;
  meta: ResponseCollectionMeta;
};

export type UsersPermissionsRoleFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<UsersPermissionsRoleFiltersInput>>>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  description?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  name?: InputMaybe<StringFilterInput>;
  not?: InputMaybe<UsersPermissionsRoleFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<UsersPermissionsRoleFiltersInput>>>;
  permissions?: InputMaybe<UsersPermissionsPermissionFiltersInput>;
  type?: InputMaybe<StringFilterInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  users?: InputMaybe<UsersPermissionsUserFiltersInput>;
};

export type UsersPermissionsRoleInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  permissions?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  type?: InputMaybe<Scalars['String']['input']>;
  users?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
};

export type UsersPermissionsUpdateRolePayload = {
  __typename?: 'UsersPermissionsUpdateRolePayload';
  ok: Scalars['Boolean']['output'];
};

export type UsersPermissionsUser = {
  __typename?: 'UsersPermissionsUser';
  all_users?: Maybe<AllUserRelationResponseCollection>;
  blocked?: Maybe<Scalars['Boolean']['output']>;
  confirmed?: Maybe<Scalars['Boolean']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  email: Scalars['String']['output'];
  logs?: Maybe<LogRelationResponseCollection>;
  preference?: Maybe<PreferenceEntityResponse>;
  provider?: Maybe<Scalars['String']['output']>;
  role?: Maybe<UsersPermissionsRoleEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  username: Scalars['String']['output'];
};


export type UsersPermissionsUserAll_UsersArgs = {
  filters?: InputMaybe<AllUserFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type UsersPermissionsUserLogsArgs = {
  filters?: InputMaybe<LogFiltersInput>;
  pagination?: InputMaybe<PaginationArg>;
  sort?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};

export type UsersPermissionsUserEntity = {
  __typename?: 'UsersPermissionsUserEntity';
  attributes?: Maybe<UsersPermissionsUser>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type UsersPermissionsUserEntityResponse = {
  __typename?: 'UsersPermissionsUserEntityResponse';
  data?: Maybe<UsersPermissionsUserEntity>;
};

export type UsersPermissionsUserEntityResponseCollection = {
  __typename?: 'UsersPermissionsUserEntityResponseCollection';
  data: Array<UsersPermissionsUserEntity>;
  meta: ResponseCollectionMeta;
};

export type UsersPermissionsUserFiltersInput = {
  all_users?: InputMaybe<AllUserFiltersInput>;
  and?: InputMaybe<Array<InputMaybe<UsersPermissionsUserFiltersInput>>>;
  blocked?: InputMaybe<BooleanFilterInput>;
  confirmationToken?: InputMaybe<StringFilterInput>;
  confirmed?: InputMaybe<BooleanFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  email?: InputMaybe<StringFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  logs?: InputMaybe<LogFiltersInput>;
  not?: InputMaybe<UsersPermissionsUserFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<UsersPermissionsUserFiltersInput>>>;
  password?: InputMaybe<StringFilterInput>;
  preference?: InputMaybe<PreferenceFiltersInput>;
  provider?: InputMaybe<StringFilterInput>;
  resetPasswordToken?: InputMaybe<StringFilterInput>;
  role?: InputMaybe<UsersPermissionsRoleFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  username?: InputMaybe<StringFilterInput>;
};

export type UsersPermissionsUserInput = {
  all_users?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  blocked?: InputMaybe<Scalars['Boolean']['input']>;
  confirmationToken?: InputMaybe<Scalars['String']['input']>;
  confirmed?: InputMaybe<Scalars['Boolean']['input']>;
  email?: InputMaybe<Scalars['String']['input']>;
  logs?: InputMaybe<Array<InputMaybe<Scalars['ID']['input']>>>;
  password?: InputMaybe<Scalars['String']['input']>;
  preference?: InputMaybe<Scalars['ID']['input']>;
  provider?: InputMaybe<Scalars['String']['input']>;
  resetPasswordToken?: InputMaybe<Scalars['String']['input']>;
  role?: InputMaybe<Scalars['ID']['input']>;
  username?: InputMaybe<Scalars['String']['input']>;
};

export type UsersPermissionsUserRelationResponseCollection = {
  __typename?: 'UsersPermissionsUserRelationResponseCollection';
  data: Array<UsersPermissionsUserEntity>;
};

export type WeekCompetency = {
  __typename?: 'WeekCompetency';
  competency?: Maybe<Scalars['JSON']['output']>;
  createdAt?: Maybe<Scalars['DateTime']['output']>;
  finalScore?: Maybe<Scalars['Int']['output']>;
  prevWeekScore?: Maybe<Scalars['Int']['output']>;
  publishedAt?: Maybe<Scalars['DateTime']['output']>;
  rank?: Maybe<Scalars['String']['output']>;
  trainee?: Maybe<TraineeEntityResponse>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  week?: Maybe<Scalars['String']['output']>;
};

export type WeekCompetencyEntity = {
  __typename?: 'WeekCompetencyEntity';
  attributes?: Maybe<WeekCompetency>;
  id?: Maybe<Scalars['ID']['output']>;
};

export type WeekCompetencyEntityResponse = {
  __typename?: 'WeekCompetencyEntityResponse';
  data?: Maybe<WeekCompetencyEntity>;
};

export type WeekCompetencyEntityResponseCollection = {
  __typename?: 'WeekCompetencyEntityResponseCollection';
  data: Array<WeekCompetencyEntity>;
  meta: ResponseCollectionMeta;
};

export type WeekCompetencyFiltersInput = {
  and?: InputMaybe<Array<InputMaybe<WeekCompetencyFiltersInput>>>;
  competency?: InputMaybe<JsonFilterInput>;
  createdAt?: InputMaybe<DateTimeFilterInput>;
  finalScore?: InputMaybe<IntFilterInput>;
  id?: InputMaybe<IdFilterInput>;
  not?: InputMaybe<WeekCompetencyFiltersInput>;
  or?: InputMaybe<Array<InputMaybe<WeekCompetencyFiltersInput>>>;
  prevWeekScore?: InputMaybe<IntFilterInput>;
  publishedAt?: InputMaybe<DateTimeFilterInput>;
  rank?: InputMaybe<StringFilterInput>;
  trainee?: InputMaybe<TraineeFiltersInput>;
  updatedAt?: InputMaybe<DateTimeFilterInput>;
  week?: InputMaybe<StringFilterInput>;
};

export type WeekCompetencyInput = {
  competency?: InputMaybe<Scalars['JSON']['input']>;
  finalScore?: InputMaybe<Scalars['Int']['input']>;
  prevWeekScore?: InputMaybe<Scalars['Int']['input']>;
  publishedAt?: InputMaybe<Scalars['DateTime']['input']>;
  rank?: InputMaybe<Scalars['String']['input']>;
  trainee?: InputMaybe<Scalars['ID']['input']>;
  week?: InputMaybe<Scalars['String']['input']>;
};

export type WeekCompetencyRelationResponseCollection = {
  __typename?: 'WeekCompetencyRelationResponseCollection';
  data: Array<WeekCompetencyEntity>;
};


