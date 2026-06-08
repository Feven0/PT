import { TagProps } from "../components/commonComponents/Tag";

const useTagType = () => {
  const getType = (sentiment: string): TagProps['type'] => (
    sentiment.toLowerCase() === 'neutral' ? 'neutral10' :
      sentiment.toLowerCase() === 'positive' ? 'high1' :
        sentiment.toLowerCase() === 'negative' ? 'low7' :
        sentiment.toLowerCase() === 'approved' ? 'high1' :
        sentiment.toLowerCase() === 'verified' ? 'high1' :
        sentiment.toLowerCase() === 'rejected' ? 'low7' :
        sentiment.toLowerCase() === 'declined' ? 'low7' :
          'info11'
  );

  const getConfidenceType = (confidence: string): TagProps['type'] => (
    confidence.toLowerCase() === 'high' ? 'high2' :
      confidence.toLowerCase() === 'medium' ? 'mid5' :
        confidence.toLowerCase() === 'low' ? 'low7' :
          'info11'
  );

  return { getType, getConfidenceType };
};

export default useTagType;
