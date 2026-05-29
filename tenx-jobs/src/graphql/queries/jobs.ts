import { gql } from '@apollo/client';

export const GET_ALL_JOBS = gql`
query getJobProfile {
  tinderJobProfiles {
    data {
      id
      attributes {
        title
        level
        summary
        endDate
        tags
        attributes
        job {
          data {
            id
            attributes {
              companyName
              title
              link
              description
            }
          }
        }
      }
    }
  }
}
`