import { gql } from "@apollo/client";

//Create a new job application status
export const CREATE_JOBS = gql`
mutation createNewStatus(
    $name: String
    $description: String
    $traineeJobID: ID
    $slug: String
    ) {
    createJobAppliecationStatus(
        data: {
        slug: $slug
        job_trainee: $traineeJobID
        Name: $name
        Description: $description
        }
    ) {
        data {
        id
        }
    }
}
`

//Update a job tag
export const JOB_TRAINEE_TAG=gql`
mutation UpdateJobTag($traineeJobID:ID!,$Tag:String){
  updateJobTrainee(id:$traineeJobID,data:{Tag:$Tag}){
    data{
      id
    }
  }
}
`

//Update a job status
export const JOB_TRAINEE_STATUS=gql`
mutation UpdateJobStatus($traineeJobID:ID!,$status:String){
  updateJobTrainee(id:$traineeJobID,data:{status:$status}){
    data{
      id
    }
  }
}`

//Create an exchange
export const CREATE_EXCHANGE = gql`
  mutation createExchange($topic:String!,$batch:Int!){
    createExchange(data:{topic:$topic,batch:$batch}){
      data{
        id
        attributes{
          topic
        }
      }
    }
  }
`
//Create a message
export const CREATE_MESSAGE = gql`
  mutation createMessage($content:JSON!,$exchangeID:ID!,$sender:ID!){
    createMessage(data:{content:$content,exchange:$exchangeID,sender_id:$sender}){
      data{
        id
      }
    }
  }
`

//Update a job asset
export const EDIT_JOB_ASSET = gql`
mutation updateJobAssetRelation($id:ID!,$jobTrainees:[ID]){
  updateJobAsset(id:$id,data:{job_trainees:$jobTrainees}){
    data{
      id
    }
  }
}`

//Create a notification
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
        origin: $origin
      }
    ) {
      data {
        id
      }
    }
  }
`

//Create a job asset
export const CREATE_JOB_ASSET=gql`
mutation createAsset(
  $name: String
  $type: String
  $traineeID: ID
  $jobTrainees: [ID]
  $slug:String
  $additionalInfo:JSON
  $content:JSON
) {
  createJobAsset(
    data: {
      name: $name
      type: $type
      trainee: $traineeID
      job_trainees: $jobTrainees
      slug:$slug
      additionalInfo:$additionalInfo
      content:$content
    }
  ){
    data{
      id
    }
  }
}

`


