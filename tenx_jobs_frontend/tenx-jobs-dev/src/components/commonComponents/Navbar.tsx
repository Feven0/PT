import type { MenuProps } from 'antd';
import { Button, Avatar, Dropdown } from 'antd'
import { LogOut01 } from '@untitled-ui/icons-react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from "@apollo/client";
import { ReactElement } from "react";

// Redux and custom hooks
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks";
import { reset } from "../../redux/slices/userSlices";
import { persistor } from "../../redux/store";
import { log } from "../../graphql/mutations/Log";
import { resetReloadCount } from "../../redux/slices/leapProfileIdSlice";

// Assets and styles
import { tenAccLogo } from '../../assets';
import { setSiderTab } from "../../redux/slices/tabsSlice";

type NavbarProps = {
  link?: string
  NavbarComponent: ReactElement
}

export default function Navbar({link, NavbarComponent}: NavbarProps){
    const navigate = useNavigate()
    const dispatch = useAppDispatch()
    const username = useAppSelector((state) => state.user?.username) as string
    const email = useAppSelector((state) => state.user?.email) as string
    const strapiId = useAppSelector((state) => state.user?.strapiId)

    const [createLog] = useMutation(log);

    const handleProfileView = () => {
      if(link) {
        navigate(link)
      }
    }
    const handleLogout = () => {
        createLog({ variables: { "userId": strapiId, "action": "logout" } })
        dispatch(reset())
        sessionStorage.clear()
        localStorage.clear()
        dispatch(setSiderTab('1'));
        persistor.pause();
        persistor.flush().then(() => {
          return persistor.purge();
        });
        dispatch(resetReloadCount());
        persistor.persist();
        navigate("/login")
    }

    const items: MenuProps['items'] = [
        {
            key: '1',
            label: <div className="d-flex align-items-center">
                <Avatar style={{ 
                    width: "2rem", 
                    height: "1.75rem", 
                    borderRadius: "50%" }} 
                    icon={username.charAt(0)} />
                <div style={{ marginLeft: 8 }}>
                    <div>{username}</div>
                    <div>{email}</div>
                </div>
            </div>,
        },
        {
          key: '2',
          label: 
          <div className="flex-center mt-4 mb-4 br-4" onClick={handleProfileView} style={{border:"1px solid #FBFCFC",  padding:"0.5rem 0.5rem"}}>
            <span className="dark-orange-color">View Profile</span>
          </div>
          
        },
        {
            key: '3',
            label: <Button 
                    className="flex-center" 
                    style={{ width: "100%", border: "none", margin: "0rem" }} 
                    icon={<LogOut01 />}>Logout</Button>,
            onClick: handleLogout
        }
    ];

    const getColorFromCharacter = (character: string) => {
        const charCode = character.charCodeAt(0);
        const color = `hsl(${charCode % 360}, 70%, 50%)`;
        return color;
      };
    
      const avatarColor = getColorFromCharacter(username.charAt(0));

      
    return (
        <div style={{zIndex: "1"}} className="d-flex-between">
          <Link to="/">
          <div className="flex-center gap-16">
            <img src = {tenAccLogo} alt="10 Academy logo" width={36} />
            <h2 className="logo-text">Job Search</h2>
          </div>
          </Link>
          <div className="flex-center gap-16">
            {NavbarComponent}
            <Dropdown menu={{ items }} placement="bottomRight" arrow>
                  <div className="flex-center gap-16" style={{ cursor: 'pointer' }}>
                    <Avatar style={{ borderRadius: "50%", backgroundColor: avatarColor }} icon={username.charAt(0)} />
                  </div>
            </Dropdown>
          </div>
        </div>
    )
}
