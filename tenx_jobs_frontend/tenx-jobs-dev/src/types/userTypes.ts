import { ReviewerEntityResponseCollection, TinderUserProfileEntityResponseCollection, TraineeEntityResponseCollection } from "./generated";

export type TUser = {
    token: string;
    username: string;
    email: string;
    role: string;
    userId: string;
    strapiId: string;
    batch: string;
    allUserId: string;
    groups: string;
    Tid: string;
    Rid: string;
    batchID: string;
    user_profile_id: string;
  }

  export type TReviewer ={
    reviewers: ReviewerEntityResponseCollection
  }

  export type TTrainee = {
    trainees: TraineeEntityResponseCollection
  }

  export type TUserProfile = {
    tinderUserProfiles: TinderUserProfileEntityResponseCollection
  }