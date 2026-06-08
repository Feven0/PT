import { Col } from 'antd'
import signUpBg from '../../assets/images/authImages/sign-up.webp'
import signUpMobile from '../../assets/images/authImages/singn-up-mobile.webp'
import backgroundPattern from '../../assets/images/authImages/authBackgroundImage.webp'
import { useMediaQuery } from 'react-responsive'

export default function AuthBackgroundPattern() {
  const isMobile = useMediaQuery({maxWidth:767})
  const isLargeScreen = useMediaQuery({minWidth: 1200})

  
  return (
    <Col xs={24} md={10} className="background-pattern-column">
    {isLargeScreen ? <img src={backgroundPattern} alt="background pattern" className="background-pattern" style={{height:"100vh", width:"100%"}} />:
    !isMobile ? <img src={signUpBg} alt="background pattern" className="sign-up-image" style={{height:"100vh", width:"100%"}} />
    : <img src={signUpMobile} alt="background pattern" className="sign-up-image-mobile" />}
</Col>
  )
}
