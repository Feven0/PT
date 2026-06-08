import { useState } from 'react';
import { FormInstance } from 'antd';
import { checkboxOptions } from "../utils/commonUtils";

export type ActionState = {
  option: string;
  action: string | null;
};

const useActionHandler = (form: FormInstance) => {
  const [bubblingOption, setBubblingOption] = useState<string | null>(null);
  const [isSkipping, setIsSkipping] = useState(false);
  const [actions, setActions] = useState<ActionState[]>(checkboxOptions.map(option => ({ option, action: null })));

  const handleAction = (option: string, action: 'like' | 'dislike' | null) => {
    setIsSkipping(false);
    if (action === 'like') {
      setBubblingOption(option);
    } else if (action === 'dislike') {
      setBubblingOption(null);
    }
    setTimeout(() => setBubblingOption(null), 300);
    setActions(prevActions => {
      const existingAction = prevActions.find(item => item.option === option);
      if (existingAction) {
        const newAction = existingAction.action === action ? null : action;
        return prevActions.map(item =>
          item.option === option ? { ...item, action: newAction } : item
        );
      } else {
        return [...prevActions, { option, action }];
      }
    });
  };

  const handleSubmitFeedback = (feedbackText: string) => {
    setActions(prevActions => {
      const existingAction = prevActions.find(item => item.option === 'Other');
      if (existingAction) {
        return prevActions.map(item =>
          item.option === 'Other' ? { ...item, action: feedbackText } : item
        );
      } else {
        return [...prevActions, { option: 'Other', action: feedbackText }];
      }
    });
    form.resetFields();
  };

  return {
    bubblingOption,
    isSkipping,
    actions,
    handleAction,
    setActions,
    setIsSkipping,
    handleSubmitFeedback,
  };
};

export default useActionHandler;
