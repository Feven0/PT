// import React,{ useState, useEffect } from "react";
// import Api from "../Services/Services";
// export const ProviderContext = React.createContext();

// Update the ProviderValue interface to include setStart
// interface ProviderValue {
//     session?: any; 
//     latestsession?: any; 
//     setStart?: React.Dispatch<React.SetStateAction<boolean>>; // Include setStart
// }

// export const PersonaContext = ({ children }) => {
//     const [session, setSession] = useState()
//     const [latestsession, setLatestSession] = useState()
//     const [refresh, setRefresh] = useState(0);
//     const [start, setStart] = useState(false)
    
    

//     const sessionData = async () => {
//       const userId= localStorage.getItem("userId")
//       const response = await Api.fetchSession({userId})
//       console.log("fetching user session...", response.data)
//       setSession(response.data.all_user_data)
//       setLatestSession(response.data.latest_user_data)
//       setStart(false);
//     }

    
    
//     // useEffect(() => {
//     //   // if (start) {        
//     //     sessionData();
//     //     const intervalId = setInterval(() => {
//     //       setRefresh((prev) => prev + 1);
//     //     }, 5000);
  
//     //     return () => clearInterval(intervalId); 
//     //   // }
//     //   //start, latestsession
//     // },[refresh]);
    
//       return (
//         <ProviderContext.Provider
//           value={{
//             session,
//             latestsession,
//             setStart
//             }}
//           >
//           {children}
//         </ProviderContext.Provider>
//       )
//   };

//             return () => clearInterval(intervalId);
//         }
//     }, [refresh]);

//     return (
//         <ProviderContext.Provider value={{ session, latestsession, setStart }}>
//             {children}
//         </ProviderContext.Provider>
//     );
// };