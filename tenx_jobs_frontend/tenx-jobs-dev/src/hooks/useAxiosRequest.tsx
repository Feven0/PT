import { useState } from 'react';
import axios from 'axios';
import { getWithExpiry } from "../utils/BrowserFunction";
const backendUrl = import.meta.env.VITE_API_LEAP_JOB_BACKEND_URL;

interface UseAxiosRequestParams {
  url: string;
  method: 'POST' | 'GET' | 'PUT' | 'DELETE';
  data?: any;
  onSuccess?: (response: any) => void;
  onError?: (error: any) => void;
}

const useAxiosRequest = () => {
  const token  = getWithExpiry("token");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);

  const makeRequest = async ({
    url,
    method,
    data,
    onSuccess,
    onError,
  }: UseAxiosRequestParams) => {
    setLoading(true);

    try {
      const response = await axios({
        url: `${backendUrl}${url}`,
        method,
        data,
        headers : {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        }
      });

      if (response.status === 200 && onSuccess) {
        onSuccess(response);
      }
    } catch (error) {
      setError(error);

      if (onError) onError(error);
      setError(`Error fetching data: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return { makeRequest, loading, error };
};

export default useAxiosRequest;
