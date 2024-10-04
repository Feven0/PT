import { CgProfile } from 'react-icons/cg';
import { Link } from 'react-router-dom';
import { useState, useContext } from 'react';
import { Dropdown, Menu, Button, Typography } from 'antd';
import { ProviderContext } from '../context/context';
import '../styles/Navbar/navbar.css'
const { Text } = Typography;

const Navbar = () => {
    const {latestsession} = useContext(ProviderContext)
    const [open, setOpen] = useState(false);

    const menu = (
        <Menu>
            <Menu.Item key="2">
                <Link to="/personal_dashboard">Activity</Link>
            </Menu.Item>
            <Menu.Item key="3">
                <Link to="/upload">Upload</Link>
            </Menu.Item>
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
                        <Text className='header'>Ipersona</Text>
                    </Link>
                    <span>
                        <Text style={{fontSize: '0.9rem'}} className='pdf'>{latestsession?.username}</Text>
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