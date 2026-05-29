export const scoringCriteria = {
  Interested: {
    bins: [0, 1, 10, 50, 100, Infinity],
    weights: [0, 0.1, 0.2, 0.3, 0.4],
    criterion_weight: 0.05,
  },
  Applied: {
    bins: [0, 1, 10, 30, 50, Infinity],
    weights: [0, 0.1, 0.2, 0.3, 0.4],
    criterion_weight: 0.2,
  },
  Change_2: {
    Rejections: {
      bins: [0, 1, 2, 5, Infinity],
      weights: [0, 0.2, 0.3, 0.5],
    },
    Interviews: {
      bins: [0, 1, 3, Infinity],
      weights: [0, 0.4, 0.6],
    },
    Offers: {
      bins: [0, 1, Infinity],
      weights: [0, 1],
    },
    criterion_weight: 0.4,
  },
  Challenges_Completed: {
    bins: [0, 1, 2, Infinity],
    weights: [0, 0.3, 0.7],
    criterion_weight: 0.15,
  },
  Standup_Attendance: {
    bins: [0, 1, 4, Infinity],
    weights: [0, 0.4, 0.6],
    criterion_weight: 0.2,
  },
};