import { createSlice, PayloadAction } from "@reduxjs/toolkit";

type ReferenceType = {
  full_name: string
  email: string
  relationship: string 
  phone: string[]
  remark: string[]
}

type Profile = {
  languages: {
    id:string;
    fluency: string;
    language: string;
  },

  volunteer: {
    id: string;
    organization: string;
    position: string;
    duration: [string, string | null];
    summary: string;
    url?: string;
  },

  awards: {
    id: string
    awarder: string;
    title: string;
    date: string;
    summary: string;
    url?: string;
  },

  certificates: {
    id: string;
    name: string;
    date: string;
    issuer: string;
    url?: string;
  },
  achievements: {
    id: string;
    title: string;
    date: string;
    summary: string;
  },
  programming_languages: {
    id: string;
    name: string;
    level: string | number | null;
  }
  reference: {
    id: string;
    priority: number;
    reference_text: string;
    contact: ReferenceType;
  },
  publications: {
    id: string;
    name: string
    publisher: string
    release_date: string
    url?: string
    summary: string
  }
  languageUUID?: string;
  awardUUID?: string;
  volunteerUUID?: string;
  certificateUUID?: string;
  achievementUUID?: string;
  programming_languageUUID?: string;
  referenceUUID?: string;
  publicationUUID?: string;
}

const initialState: Profile = {
  languages: {
    id: "",
    fluency: "",
    language: ""
  },
  volunteer: {
    id: "",
    organization: "",
    position: "",
    duration: ["", ""],
    summary: ""
  },
  awards: {
    id: "",
    awarder: "",
    title: "",
    date: "",
    summary: "",
    url: ""
  },
  certificates: {
    id: "",
    name: "",
    date: "",
    issuer: "",
  },
  achievements: {
    id: "",
    title: "",
    date: "",
    summary: ""
  },
  programming_languages: {
    id: "",
    name: "",
    level: null
  },
  reference: {
    id: "",
    priority: 0,
    reference_text: "",
    contact: {
      full_name: "",
      email: "",
      relationship: "",
      phone: [],
      remark: []
    }
  },
  publications: {
    id: "",
    name: "",
    publisher: "",
    release_date: "",
    url: "",
    summary: ""
  },
  languageUUID: "",
  awardUUID: "",
  volunteerUUID: "",
  certificateUUID: "",
  achievementUUID: "",
  programming_languageUUID: "",
  referenceUUID: "",
  publicationUUID: ""
}

const otherProfilesSlice = createSlice({
  name: "otherProfiles",
  initialState,
  reducers: {
    setLanguages: (state, action: PayloadAction<Profile['languages']>) => {
      state.languages = action.payload;
    },

    setVolunteerWork: (state, action: PayloadAction<Profile['volunteer']>) => {
      state.volunteer = action.payload;
    },

    setTraineeAwards: (state, action: PayloadAction<Profile['awards']>) => {
      state.awards = action.payload;
    },

    setTraineeCertificates: (state, action: PayloadAction<Profile['certificates']>) => {
      state.certificates = action.payload
    },
    setTraineeAchievements: (state, action: PayloadAction<Profile['achievements']>) => { 
      state.achievements = action.payload
    },

    setLanguageUUID: (state, action: PayloadAction<string>) => {
      state.languageUUID = action.payload
    },
    setAwardUUID: (state, action: PayloadAction<string>) => {
      state.awardUUID = action.payload
    },

    setVolunteerId: (state, action: PayloadAction<string>) => {
      state.volunteerUUID = action.payload
    },

    setCertificateUUID: (state, action: PayloadAction<string>) => {
      state.certificateUUID = action.payload
    },
    setAchievementUUID: (state, action: PayloadAction<string>) => {
      state.achievementUUID = action.payload
    },
    setTraineeProgrammingLanguages: (state, action: PayloadAction<Profile['programming_languages']>) => {
      state.programming_languages = action.payload
    },
    setProgrammingLanguesUUID: (state, action: PayloadAction<string>) => {
      state.programming_languageUUID = action.payload
    },

    setTraineeReferences: (state, action: PayloadAction<Profile['reference']>) => {
      state.reference = action.payload
    },
    setReferenceUUID: (state, action: PayloadAction<string>) => {
      state.referenceUUID = action.payload
    },

    setTraineePublications: (state, action: PayloadAction<Profile['publications']>) => {
      state.publications = action.payload
    },
    setPublicationUUID: (state, action: PayloadAction<string>) => {
      state.publicationUUID = action.payload
    },

    resetLanguages: (state) => {
      state.languages = initialState.languages;
    },
    resetVolunteerWork: (state) => {
      state.volunteer = initialState.volunteer;
    },
    resetTraineeAwards: (state) => {
      state.awards = initialState.awards;
    },

    resetTraineeCertificates: (state) => {
      state.certificates = initialState.certificates;
    },
    resetAchievements: (state) => {
      state.achievements = initialState.achievements
    },
    resetProgrammingLanguages: (state) => {
      state.programming_languages = initialState.programming_languages
    },
    resetTraineeReferences: (state) => {
      state.reference = initialState.reference
    },
    resetTraineePublications: (state) => {
      state.publications = initialState.publications
    }
  }
})

export const { 
    setLanguages, 
    setLanguageUUID, 
    setTraineeCertificates, 
    resetTraineeCertificates, 
    setTraineeAwards, 
    resetTraineeAwards,
    setVolunteerWork, 
    resetVolunteerWork, 
    setVolunteerId,
    setAwardUUID, 
    setTraineeAchievements,
    setAchievementUUID,
    setTraineeProgrammingLanguages,
    setProgrammingLanguesUUID,
    resetProgrammingLanguages,
    resetAchievements,
    setCertificateUUID,
    resetTraineeReferences,
    setTraineeReferences,
    setReferenceUUID,
    resetTraineePublications,
    setTraineePublications,
    setPublicationUUID,
    resetLanguages } = otherProfilesSlice.actions;
export default otherProfilesSlice.reducer;