import { Slab } from 'react-loading-indicators';


const LoadingIndicator = ({message}) => {
    const styles = {
        container: {
            display: 'flex',
            justifyContent: 'center',
            flexDirection: 'column', 
            alignItems: 'center',
            height: '70vh',
            fontFamily: 'Arial, sans-serif',
            color: '#d1cccb',
        },
        loadingBox: {
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
            padding: '20px',
            borderRadius: '10px',
        },
        loadingText: {
            fontSize: '18px',
            color: '#333', 
            fontWeight: '500',
            marginTop: '10px', 
        },
      };
      
      const Loading = () => {
          return (
              <div style={styles.container}>
                  <h1>{message}</h1>
                  <div style={styles.loadingBox}>
                      <Slab color="#ee582b" size="medium" text="" textColor="#333" />
                  </div>
              </div>
          );
      };
  return (
    <div>
        <Loading/>
    </div>
  )
}

export default LoadingIndicator