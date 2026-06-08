// useUpdateMedia.ts
import { useDispatch } from 'react-redux';
import { useAppSelector } from "../redux/hooks/hooks";
import { SegmentedOption } from "../types/updated_profile";
import { setContactsForm, TContacts } from "../redux/slices/setContactsSlice";

const contacts = [
  "Main",
  "WhatsApp",
  "Telegram",
  "Skype"
];

const useContactsForm = () => {
  const dispatch = useDispatch();
  const { phone } = useAppSelector((state) => state.contactsForm);

  const handleContactSelectChange = (value: string, index: number) => {
    const updatedMedia = phone.map((me: TContacts, i: number) => 
      i === index ? { ...me, name: value } : me
    );
    dispatch(setContactsForm({ phone: updatedMedia }));
  };

  const handleContactMaxSectionChange = (value: string | null, index: number) => {
    const updatedMedia = phone.map((me: TContacts, i: number) => 
      i === index ? { ...me, value: value ?? null } : me
    );
    dispatch(setContactsForm({ phone: updatedMedia }));
  };

  const filterContactOptions = () => {
    const existingNames = phone.map((mediaItem) => mediaItem.name.toLowerCase());
    return contacts.filter(option => !existingNames.includes(option.toLowerCase()));
  };

  const capitalizeContactsOptions: SegmentedOption[] = filterContactOptions().map(type => ({
    label: type.charAt(0).toUpperCase() + type.slice(1),
    value: type
  }));

  return {
    handleContactSelectChange,
    handleContactMaxSectionChange,
    capitalizeContactsOptions,
  };
};

export default useContactsForm;
