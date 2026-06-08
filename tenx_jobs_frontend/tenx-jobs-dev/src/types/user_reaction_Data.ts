export type TReactionAttribute = {
  section: string;
  user_reaction: string | null;
};

export type TReactionAttributes = {
  comment: string;
  applyLink: string;
  job_title?: string;
  job_level?: string;
  attributes: TReactionAttribute[];
  match_score: number;
  job_location?: string;
  additional_data: Record<string, any>;
};

export type TReaction = {
  all_user_id: string;
  tinder_job_profile_id: string;
  tinder_user_profile_id: string;
  tinder_asset_generation_id?: string | null;
  tinder_asset_generation?: string | null;
  category: string;
  slug: string;
  metadata: Record<string, any>;
  match_status: string;
  user_reaction: string;
  reaction_attributes: TReactionAttributes;
  comment: string;
  createdAt: string;
  tinder_user_reaction_id: string;
};

export type TReactionsResponse = {
  all_user_id: number;
  reactions: TReaction[];
  status: number;
  message: string;
};
