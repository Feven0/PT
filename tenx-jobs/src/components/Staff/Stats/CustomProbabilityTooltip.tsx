interface EngagementStat {
  name: string;
  "Challenges Completed(%)": number;
  "Standup Attendance(%)": number;
}

interface ApplicationStat {
  name: string;
  Interested: number;
  Applied: number;
  Rejections: number;
  Interviews: number;
  Offers: number;
}

interface AggregatedData {
  gender: Record<string, any>;
  performance: Record<string, any>;
}

interface CustomSuccessProbabilityTooltipProps {
  active?: boolean;
  payload?: any;
  label?: string;
  engagements: EngagementStat[];
  applications: ApplicationStat[];
  showAggregatedView: boolean;
  aggregatedData: AggregatedData;
}
export default function CustomSuccessProbabilityTooltip({
  active,
  payload,
  label,
  engagements,
  applications,
  showAggregatedView,
  aggregatedData,
}: CustomSuccessProbabilityTooltipProps) {
  const engagementStats = engagements.find((user) => user.name === label);
  const applicationStats = applications.find((user) => user.name === label);

  if (active && payload && payload.length) {
    if (showAggregatedView && label) {
      const categoryStats = aggregatedData.gender[label] || aggregatedData.performance[label];
      if (categoryStats) {
        return (
          <div className="custom-tooltip">
            <p className="label">{`${label} : ${payload[0].value.toFixed(2)}%`}</p>
            <p className="desc">
              Challenges Completed: {categoryStats.challengesCompleted.toFixed(2)}%
            </p>
            <p className="desc">
              Standup Attendance: {categoryStats.standupAttendance.toFixed(2)}%
            </p>
            <p className="desc">
              Interested: {categoryStats.interested.toFixed(2)}
            </p>
            <p className="desc">Applied: {categoryStats.applied.toFixed(2)}</p>
            <p className="desc">
              Rejections: {categoryStats.rejections.toFixed(2)}
            </p>
            <p className="desc">
              Interviews: {categoryStats.interviews.toFixed(2)}
            </p>
            <p className="desc">Offers: {categoryStats.offers.toFixed(2)}</p>
          </div>
        );
      }
    } else {
      return (
        <div className="custom-tooltip">
          <p className="label">{`${label} : ${payload[0].value}%`}</p>
          {engagementStats && (
            <>
              <p className="desc">
                Challenges Completed: {engagementStats["Challenges Completed(%)"]}%
              </p>
              <p className="desc">
                Standup Attendance: {engagementStats["Standup Attendance(%)"]}%
              </p>
            </>
          )}

          {applicationStats && (
            <>
              <p className="desc">Interested: {applicationStats.Interested}</p>
              <p className="desc">Applied: {applicationStats.Applied}</p>
              <p className="desc">Rejections: {applicationStats.Rejections}</p>
              <p className="desc">Interviews: {applicationStats.Interviews}</p>
              <p className="desc">Offers: {applicationStats.Offers}</p>
            </>
          )}
        </div>
      );
    }
  }

  return null;
}