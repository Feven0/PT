import { gql } from "@apollo/client";

//Get all the exchanges for a topic
export const EXCHANGE = gql`
  query GetExchange($topic:String!){
    exchanges(pagination:{start:0,limit:200} filters:{topic:{eq:$topic}}){
      data{
        id
        attributes{
          topic
          messages(sort:"createdAt", pagination:{start:0,limit:200}){
            data{
              attributes{	
                content
                createdAt
                sender_id{
                  data{
                    id
                    attributes{
                      name
                      image_link
                    }
                  }
                }
                
              }
            }
          }
        }
      }
    }
  }
`

//Get all the jobs for a trainee
export const GET_JOB_DETAIL = gql`
  query traineeJob($traineeJobID: ID!, $Tid: ID!) {
    jobTrainees(
      filters: { trainee: { id: { eq: $Tid } }, id: { eq: $traineeJobID } }
    ) {
      data {
        attributes {
          trainee {
            data {
              id
              attributes {
                all_user {
                  data {
                    id
                    attributes {
                      name
                    }
                  }
                }
              }
            }
          }
          job {
            data {
              id
              attributes {
                title
                companyName
                link
                Platform
                description
                slug
                job_trainees(pagination: { start: 0, limit: 200 }) {
                  data {
                    id
                    attributes {
                      trainee {
                        data {
                          attributes {
                            all_user {
                              data {
                                attributes {
                                  name
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
          job_review_responses(
            sort: "createdAt:desc"
            pagination: { start: 0, limit: 100 }
          ) {
            data {
              id
              attributes {
                AdHoc
                rubric_id
                mark
                content
                by
                createdAt
                all_user {
                  data {
                    id
                    attributes {
                      name
                    }
                  }
                }
              }
            }
          }
          Tag
          status
          slug
          job_assets(pagination: { start: 0, limit: 100 }) {
            data {
              id
              attributes {
                name
                type
                content
                updatedAt
              }
            }
          }
          job_appliecation_statuses(pagination: { start: 0, limit: 100 }) {
            data {
              id
              attributes {
                Name
                slug
                Description
                createdAt
              }
            }
          }
        }
      }
    }
  }
`;

//Get rubrics list for a job
export const JOB_RUBRICS_LIST = gql`
  query getJobRubrics {
    jobRubrics(pagination: { start: 0, limit: 100 }, sort: "createdAt:desc") {
      data {
        id
        attributes {
          name
          createdAt
          content
          AdHoc
          createdAt
          type
          ReviewType
        }
      }
    }
  }
`;

//Get all job ids
export const JOB_TRAINEE_IDS = gql`
  query GetTraineeJobs($traineeID: ID!) {
    jobTrainees(filters: { trainee: { id: { eq: $traineeID } } }) {
      data {
        id
      }
    }
  }
`;

export const JOB_APPLICATION_MATERIALS = gql`
  query GetApplicationMaterials($traineeID: ID!) {
    jobAssets(
      pagination: { start: 0, limit: 500 }
      filters: { trainee: { id: { eq: $traineeID } } }
    ) {
      data {
        id
        attributes {
          name
          content
          type
          updatedAt
          job_trainees {
            data {
              id
            }
          }
        }
      }
    }
  }
`;