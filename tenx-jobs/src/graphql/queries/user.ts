import { gql } from "@apollo/client";

export const REVIEWER = gql`
query getReviewerId($email:String!){
  reviewers(filters:{Email:{eq:$email}}){
    data{
      id
      attributes{
        batches(sort:"Batch:desc"){
          data{
            id
            attributes{
              Batch
              Class_link
              Communication_link
              createdAt
            }
          }
        }
        all_user{
          data{
            id
            attributes{
              groups{
                data{
                  id
                  attributes{
                    Name
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}`

export const STAFF_PERSONAL_SETTINGS = gql`
query getDefaultSetting($email:String!){
  preferences(filters:{email:{eq:$email}}){
    data{
      attributes{
        email
        defaultSettings
      }
    }
  }
}`

export const GET_TRAINEE_DETAILS = gql`
query GetTraineeUserID($email: String!) {
  trainees(filters: { email: { eq: $email } }) {
    data {
      id
      attributes {
        trainee_id
        email
        all_user {
          data {
            id
            attributes{
              groups{
                data
                {
                  id
                  attributes{
                    Name
                  }
                }
              }
            }
          }
        }
        batch {
          data {
            id
            attributes {
              Batch
              Class_link
              Communication_link
            }
          }
        }
      }
    }
  }
}`

export const GET_REVIEWER_ID= gql`
query getReviewerId($email: String!) {
reviewers(filters: { Email: { eq: $email } }) {
  data {
    id
  }
  }
}`