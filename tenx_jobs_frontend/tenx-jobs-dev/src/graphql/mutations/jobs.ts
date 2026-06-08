import { gql } from "@apollo/client";

export const CREATE_USER_REACTION = gql`
mutation createTinderUserReaction(
  $all_user: ID
  $job_profile: ID
  $reaction: ENUM_TINDERUSERREACTION_OVERALL_REACTION
  $slug: String
  $comment: String
  $metadata: JSON
  $category: String
  $score: Int
  $tinderUserProfile: ID
  $reactionAttr: JSON
  $tinderAssetGen: ID
) {
  createTinderUserReaction (data:{
    all_user: $all_user
    tinder_job_profile: $job_profile
    overall_reaction: $reaction
    slug : $slug
    metadata: $metadata
    category: $category
    comment: $comment
    score: $score
    tinder_user_profile : $tinderUserProfile
    reaction_attributes: $reactionAttr
    tinder_asset_generation: $tinderAssetGen
  }) {
    data {
      id
    }
  }
}
`