import { useDispatch } from 'react-redux';
import { useAppSelector } from "../redux/hooks/hooks";
import { setEvidenceForm, T_Session } from "../redux/slices/updateEvidenceSlice";
import { SegmentedOption } from "../types/updated_profile";
import { SFIA_Dimension } from "../utils/commonUtils";

const useEvidenceForm = () => {
  const dispatch = useDispatch();
  const {sessions} = useAppSelector((state)=>state.updatedEvidenceForm)

  const handleSelectChange = (value: string, index: number) => {
    const sessionName = sessions.map((session: T_Session, i: number) => 
      i === index ? { ...session, name: value } : session
    );
    dispatch(setEvidenceForm({ sessions: sessionName }));
  };

  const handleMaxSectionChange = (value: number | null, index: number) => {
    const sessionMaxSection = sessions.map((session: T_Session, i: number) => 
      i === index ? { ...session, level: value } : session
    );
    dispatch(setEvidenceForm({ sessions: sessionMaxSection }));
  };

  const filterOptions = () => {
    const existingNames = sessions?.map((session: T_Session) => session.name?.toLowerCase() ?? "");
    return SFIA_Dimension.filter(option => !existingNames.includes(option?.toLowerCase()));
  };

  const capitalizedOptions: SegmentedOption[] = filterOptions().map(type => ({
    label: type.charAt(0).toUpperCase() + type.slice(1),
    value: type
  }));

  return {
    handleSelectChange,
    handleMaxSectionChange,
    filterOptions,
    capitalizedOptions,
  };
};

export default useEvidenceForm;
