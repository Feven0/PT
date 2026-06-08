import { combineReducers, configureStore } from "@reduxjs/toolkit";
import {
    persistReducer,
    FLUSH,
    REHYDRATE,
    PAUSE,
    PERSIST,
    PURGE,
    REGISTER,
    persistStore,
} from "redux-persist";
import storage from "redux-persist/lib/storage";
import { encryptTransform } from "redux-persist-transform-encrypt";
import userReducer from "./slices/userSlices";
import experienceSlice from "./slices/experienceSlice";
import jobReducer from './slices/jobCardSlice'
import useStatsReducer from "./slices/userStatsSlice";
import tableReducer from './slices/tableExtension'
import leapProfileReducers from "./slices/leapProfileIdSlice";
import TabsReducer from './slices/tabsSlice'
import ProfileSkillReducer from './slices/profileSkillSlice'
import UpdateEvidenceReducer from './slices/evidenceSlice'
import UserReactionIdsReducer from './slices/userReactionIdsSlice'
import UpdateFilterReducer from './slices/filterSlice'
import recordReducer from './slices/engagementRowSlice'
import profileReducer from './slices/profileUploadSlice'
import otherProfileReducer from './slices/otherProfilesSlice'
import personalInformationReducer from './slices/personalInformationSlice'
import updatedEvidenceReducer from './slices/updateEvidenceSlice'
import traineeInfoReducer from './slices/traineeInfoSetByStaffsSlice'
import evidenceApprovalReducer from './slices/evidenceApprovalSlice'
import competencyApprovalReducer from './slices/staffCompetencySlice'
import mediaReducer from './slices/setMediaSlice'
import contactsFormReducer from './slices/setContactsSlice'
import otherProfileSubmitButtonReducer from './slices/otherProfileSubmitButtonsSlice'
import traineeResponseReducer from './slices/traineeProfileResponseSlice'
import evidenceUpdateReducer from './slices/evidenceUpdatingSlice'
import updateSfiaReducer from './slices/updatingTraineeSifaLevelSlice'
import gridViewReducer from './slices/gridViewSlice'
import locationReducer from './slices/Preferences/locationSlices'
import salaryReducer from './slices/Preferences/salarySlices'
import rolesReducer from './slices/Preferences/rolesSlices'
import matchingPercentageReducer from './slices/Preferences/matchingPercentageSlice'
import resumeReducer from './slices/Preferences/resumeTemplateSlice'
import industryReducer from './slices/Preferences/jobIndustrySlice'
import employmentTypeReducer from './slices/Preferences/employmentTypeSlice'
import experienceLevelReducer from './slices/Preferences/experienceLevelSlice'
import companySizePreference from './slices/Preferences/companySizeSlice'
import visibilityReducer from './slices/Preferences/systemSlice'
import preferenceReducer from './slices/Preferences/preferencesSlice'
import educationPreferenceReducer from './slices/Preferences/educationPreferenceSlice'
import jobFilterReducer from './slices/Preferences/jobFilterSlice'
import preferenceControlReducer from './slices/Preferences/preferenceControlSlice'
import traineeCompetencyEvidenceReducer from './slices/evidenceMssagesSlice'
import jobKeywordsIncludeReducer from './slices/Preferences/jobKeywordsIncludeSlice'
import jobKeywordsExcludeReducer from './slices/Preferences/jobKeywordsExcludeSlice'
import IdList from './slices/staff/IdListsSlice'
import updateSinceReducer from './slices/jobSinceFilterSlice'
import selectedSkillUUIDReducer from './slices/selectedSkillsUUIDSlice'

const persistConfig = {
    key: "root",
    storage,
    transforms: [
        encryptTransform({
            secretKey: "tenx-jobs",
        }),
    ],
};
const reducers = combineReducers({
   user: userReducer,
    experience: experienceSlice,
    jobCard: jobReducer,
    userStats: useStatsReducer,
    tableExtension: tableReducer,
    leapProfileId: leapProfileReducers,
    tabs: TabsReducer,
    userProfileSkill: ProfileSkillReducer,
    updateEvidence: UpdateEvidenceReducer,
    userReactionIds: UserReactionIdsReducer,
    updateFilter: UpdateFilterReducer,
    updateRecord: recordReducer,
    profileUpload: profileReducer,
    otherProfiles: otherProfileReducer,
    personalInformation: personalInformationReducer,
    updatedEvidenceForm: updatedEvidenceReducer,
    updateTraineeInfo: traineeInfoReducer,
    evidenceApproval: evidenceApprovalReducer,
    competencyApproval: competencyApprovalReducer,
    setMediaForm: mediaReducer,
    contactsForm: contactsFormReducer,
    otherProfileSubmitButtons: otherProfileSubmitButtonReducer,
    traineeProfileResponse: traineeResponseReducer,
    updateCompetencyEvidence: evidenceUpdateReducer,
    updatingTraineeSifaLevel: updateSfiaReducer,
    gridView: gridViewReducer,
    locationPreference: locationReducer,
    salaryPreference: salaryReducer,
    rolesPreference: rolesReducer,
    matchingPercentage: matchingPercentageReducer,
    jobKeywordsInclude: jobKeywordsIncludeReducer,
    jobKeywordsExclude: jobKeywordsExcludeReducer,
    resumePreference: resumeReducer,
    industryPreference: industryReducer,
    employmentType: employmentTypeReducer,
    experienceLevelPreference: experienceLevelReducer,
    companySizePreference: companySizePreference,
    visibility: visibilityReducer,
    preferences: preferenceReducer,
    educationPreference: educationPreferenceReducer,
    jobFilter: jobFilterReducer,
    preferenceControl: preferenceControlReducer,
    traineeCompetencyEvidence: traineeCompetencyEvidenceReducer,
    IdList: IdList,
    updateSince: updateSinceReducer,
    selectedSkillsUUID: selectedSkillUUIDReducer
});

const persistedReducer = persistReducer(persistConfig, reducers);
export const store = configureStore({
    reducer: persistedReducer,
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: {
                ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
            },
        }),
    devTools: import.meta.env.MODE !=="production",
});

export const persistor: any = persistStore(store);

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch