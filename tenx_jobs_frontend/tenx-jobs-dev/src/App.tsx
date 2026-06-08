import { ConfigProvider } from 'antd';
import { Provider } from 'react-redux'
import MainRoutes from './routes/MainRoutes';
import { ApolloClient, InMemoryCache, ApolloProvider, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { getWithExpiry } from "./utils/BrowserFunction";
import { store } from "./redux/store";
import { App as UseAntdApp } from 'antd';
import theme from "./utils/theme";
const backendUrl = import.meta.env.VITE_API_BACKEND_URL;

const httpLink = createHttpLink({
  uri: `${backendUrl}/graphql`,
});

const authLink = setContext((_, { headers }) => {
  const token = getWithExpiry("token");
  return {
    headers: {
      ...headers,
      authorization: token ? `bearer ${token}` : "",
    }
  }
});

const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
});

const App = () => {
  return (
    <>
      <Provider store={store}>
        <ApolloProvider client={client}>
          <ConfigProvider theme={theme} >
            <UseAntdApp>
              <MainRoutes />
            </UseAntdApp>
          </ConfigProvider>
        </ApolloProvider>
      </Provider>
    </>
  )
}

export default App

