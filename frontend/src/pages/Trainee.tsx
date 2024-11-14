import { Select } from 'antd';
import data from '../assets/mock-data/user_profiles.json';
import { Link } from 'react-router-dom';
import '../styles/Trainee.css'; 
const { Option } = Select;

const Trainee = () => {
  return (
    <div className="container">
      <h2>Select a Trainee</h2>
      <Select placeholder="Select a name" style={{ width: '300px' }}>
        {data.map(user => (
          <Option key={user.user_profile_id} value={user.name}>
            <Link to={`/jobs/${user.user_profile_id}`}>
                {user.name}
            </Link>
          </Option>
        ))}
      </Select>
    </div>
  );
}

export default Trainee;