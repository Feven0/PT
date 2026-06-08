import { Avatar, Button, Dropdown } from "antd"
import { useNavigate } from "react-router-dom"
import { LogOut01 } from '@untitled-ui/icons-react'
import { useMutation } from "@apollo/client"
import type { MenuProps } from 'antd';

import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks"
import { log } from "../../graphql/mutations/Log"
import { reset } from "../../redux/slices/userSlices"
import { persistor } from "../../redux/store"
import { resetReloadCount } from "../../redux/slices/leapProfileIdSlice"
import { setSiderTab } from "../../redux/slices/tabsSlice";
import '../../styles/auth.css'

export default function UserHeadline() {
  const username = useAppSelector((state) => state.user?.username) as string
  const email = useAppSelector((state) => state.user?.email) as string
  const strapiId = useAppSelector((state) => state.user?.strapiId)
  
  const dispatch = useAppDispatch()
  const navigate = useNavigate()

  const [createLog] = useMutation(log);

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
        label: <div className="flex-center gap-8">
              <Avatar style={{ 
                  width: "2rem", 
                  height: "2rem", 
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
        label: <Button
                className="flex-center logout-button" 
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
      <div className="flex-center gap-16">
        <Dropdown menu={{ items }}  arrow>
          <div className="flex-center gap-16" style={{ cursor: 'pointer' }}>
            <Avatar shape="square" style={{ backgroundColor: avatarColor }} icon={username.charAt(0)} />
          </div>
        </Dropdown>
    </div>
  )
}
