// useUpdateMedia.ts
import { useDispatch } from 'react-redux';
import { useAppSelector } from "../redux/hooks/hooks";
import { setMediaForm, TMedia } from "../redux/slices/setMediaSlice";
import { SegmentedOption } from "../types/updated_profile";

const media_d = [
  "Resume",
  "LinkedIn",
  "GitHub",
  "StackOverflow",
  "Medium",
  "Twitter",
  "Quora",
  "Blog",
  "Website",
  "Other"
];

const useUpdateMedia = () => {
  const dispatch = useDispatch();
  const { media } = useAppSelector((state) => state.setMediaForm);

  const handleSelectChange = (value: string, index: number) => {
    const updatedMedia = media.map((me: TMedia, i: number) => 
      i === index ? { ...me, name: value } : me
    );
    dispatch(setMediaForm({ media: updatedMedia }));
  };

  const handleMaxSectionChange = (value: string | null, index: number) => {
    const updatedMedia = media.map((me: TMedia, i: number) => 
      i === index ? { ...me, link: value ?? null } : me
    );
    dispatch(setMediaForm({ media: updatedMedia }));
  };

  const filterOptions = () => {
    const existingNames = media.map((mediaItem) => mediaItem.name.toLowerCase());
    return media_d.filter(option => !existingNames.includes(option.toLowerCase()));
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

export default useUpdateMedia;
