import { gql } from "@apollo/client";

export const CREATE_NOTIFICATION = gql`
mutation createNotification(
  $sender: ID!
  $receiver: ID
  $detail: JSON
  $group: ID
  $batch:Int!
  $message:ID
  $origin: String
) {
  createNotification(
    data: {
      sender: $sender
      receiver: $receiver
      Detail: $detail
      group: $group
      batch:$batch
      message:$message
      origin:$origin
    }
  ) {
    data {
      id
    }
  }
}
`

export const CREATE_NOTIFICATION_STATUS = gql`
mutation CreateNotificationStatus($allUserID:ID,$NotificationID:ID){
  createNotificationStatus(
      data:{
      all_user:$allUserID,
      notification:$NotificationID,
      IsRead:true
      }){
    data{
      id
    }
  }
}`
