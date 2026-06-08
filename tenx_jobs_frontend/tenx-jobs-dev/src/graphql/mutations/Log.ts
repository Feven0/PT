import { gql } from "@apollo/client";

export const log = gql`
  mutation createLog($userId: ID!, $action: ENUM_LOG_ACTION_TYPE!, $ip: String) {
    createLog(data: { users_permissions_user: $userId, action_type: $action, ip_address: $ip}) {
      data {
        id
      }
    }
  }
`;