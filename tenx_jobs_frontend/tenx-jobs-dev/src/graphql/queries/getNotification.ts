import { gql } from "@apollo/client";

export const NOTIFICATION = gql`
query traineeNotification($allUser: ID!, $groupID: [ID], $origin: String) {
    notifications(
      sort:"createdAt:desc"
      pagination:{start:0,limit:200}
      filters: {
        sender:{id:{ne:$allUser}},
        or: [
          { receiver: { id: { eq: $allUser } } }
          { group: { id: { in: $groupID } } }
        ],
        origin: {eq: $origin}
      }
    ) {
      meta{
        pagination{
          total
        }
      }
      data {
        id
        attributes {
          Detail
          createdAt
          sender{
            data{
              id
              attributes{
                email
                name
              }
            }
          }
          notification_statuses(filters:{all_user:{id:{eq:$allUser}}}){
            data{
              id
              attributes{
                IsRead
                createdAt
              }
            }
          }
          receiver {
            data {
              attributes {
                email
              }
            }
          }
        }
      }
    }
  }
  `

 export const GET_TEAM_NOTIFICATION = gql`
  query traineeNotification($allUser: ID!, $groupID: [ID],$batch:Int, $origin: String) {
      notifications(
        sort:"createdAt:desc"
        pagination:{start:0,limit:500}
        filters: {
          batch:{eq:$batch}
          sender:{id:{ne:$allUser}},
          or: [
            { receiver: { id: { eq: $allUser } } }
            { group: { id: { in: $groupID } } }
          ],
          origin: {eq: $origin}
        }
      ) {
        meta{
          pagination{
            total
          }
        }
        data {
          id
          attributes {
            Detail
            createdAt
            sender{
              data{
                id
                attributes{
                  email
                  name
                }
              }
            }
            notification_statuses(filters:{all_user:{id:{eq:$allUser}}}){
              data{
                id
                attributes{
                  IsRead
                  createdAt
                }
              }
            }
            receiver {
              data {
                attributes {
                  email
                }
              }
            }
          }
        }
      }
    }
    
    `