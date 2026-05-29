import { gql } from "@apollo/client";

export const GET_USER_PROFILE = gql`
query getTinderUserProfile($user_id: ID) {
  tinderUserProfiles(
    filters:{
      all_users: {id: {eq: $user_id}}
    }
  ) {
    data {
      id
      attributes {
        all_users {
          data {
            id
            attributes {
              name
              email
            }
          }
        }
        category
        slug
        tags
        title
        credibility
        summary
        profile_type
        attributes
      }
    }
  }
} 
`