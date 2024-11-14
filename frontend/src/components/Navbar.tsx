import { CgProfile } from 'react-icons/cg';
import { Link } from 'react-router-dom';
import { Dropdown, Menu, Button, Typography } from 'antd';
import '../styles/Navbar/navbar.css'
const { Text } = Typography;

const Navbar = () => {
    const menu = (
        <Menu>
            <Menu.Item key="4">
                <Link to="/">Logout</Link>
            </Menu.Item>
        </Menu>
    );

    return (
        <div className="navbar-container">
            <div className="navbar-background"></div>
            <div className="navbar-content">
                <div>
                    <Link to="/">
                        <Text className='header'>iPersona</Text>
                    </Link>
                    <span>
                        <Text style={{fontSize: '0.9rem'}} className='pdf'></Text>
                    </span>
                </div>
                <Dropdown overlay={menu} trigger={['click']}>
                    <Button 
                        onClick={(e) => e.preventDefault()} 
                        className="profile-button"
                    >
                        <CgProfile size={30} />
                    </Button>
                </Dropdown>
            </div>
        </div>
    );
};

export default Navbar;