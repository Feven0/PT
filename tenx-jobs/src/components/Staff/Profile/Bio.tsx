import { Col } from "antd";
import DescriptionToggle from "../../commonComponents/DescriptionToggler";

import { noProfile } from "../../../assets";
import { T_TraineeBasics } from "../../../types/profileResponse";

type TBio = {
  bio: T_TraineeBasics;
}

const MAX_DESCRIPTION_LENGTH = 420;

export default function Bio({ bio}: TBio) {

  return (
    <>
    {(bio.attributes.length > 0 && bio.attributes[0].personal_statement) ?
    <>
      <Col span={24} className="mobile-user-profile user-bio-container">
          <DescriptionToggle bio={bio.attributes[0].personal_statement} maxDescriptionLength={MAX_DESCRIPTION_LENGTH} />
      </Col>
      </>
      :
      <Col span={24}>
          <div className="d-flex-center no-profile-data" style={{flexDirection:"column", marginBottom:"1rem"}}>
            <h3>No Personal information</h3>
            <img src={noProfile} width={200} alt="no-profile" />
            <p>Personal information is not provided for this trainee!</p>
          </div>
    </Col>
    }
    </>
  );
}
