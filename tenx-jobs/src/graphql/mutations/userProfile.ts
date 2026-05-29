import { gql } from "@apollo/client";

export const UPDATE_USER_PROFILE = gql`
mutation createUserProfile(
  $id: ID!
  $attributes: JSON
){
  updateTinderUserProfile(
    id: $id
    data : {  
    attributes: $attributes
  }) {
    data {
      id
    }
  }
}
`