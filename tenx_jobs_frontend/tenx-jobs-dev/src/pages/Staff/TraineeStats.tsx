import { useCallback, useEffect, useState } from "react";
import { Button, Card, Col, Drawer, message, Row, Select, Switch, Typography } from "antd";
import { DateRange } from "react-day-picker";
import { Dayjs } from 'dayjs';
import { DatePicker } from 'antd';
import { Maximize01, Minimize01 } from '@untitled-ui/icons-react';
import {CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis} from "recharts";

// Components
import JobApplicationStats from "../../components/Staff/Stats/JobApplicationStats";
import ServerError from "../../components/commonComponents/ServerError";
import CustomSuccessProbabilityTooltip from "../../components/Staff/Stats/CustomProbabilityTooltip";
import EngagementMetrics from "../../components/Staff/Stats/EngagementMetrics";
import ScoringCriteria from "../../components/Staff/Stats/ScoringCriteria";
import CSVExportButton from "../../components/Staff/Stats/CSVExportBtn";
import StaffDataLoader from "../../components/commonComponents/StaffDataLoader";
import CountStats from "../../components/Staff/Stats/CountStats";

import { convertToDayjsRange, formatDateRange, formatToISO, getCurrentWeekRangeS } from "../../utils/dateUtils";
import { AggregatedData, GeneralAggregateCountStats, UserStats } from "../../types/statsTypes";
import { useAppSelector } from "../../redux/hooks/hooks";
import useAxiosRequest from "../../hooks/useAxiosRequest";
import '../../styles/stats.css'
import '../../styles/slidingCard.css'

const { RangePicker } = DatePicker;
const {Paragraph} = Typography;

export default function TraineeStats() {
  const [data, setData] = useState<UserStats[]>([]);
  const [weeks, setWeeks] = useState<string[]>([]);
  const [numOfAssignments, setNumOfAssignments] = useState<number>(0);
  const [dateRange, setDateRange] = useState<DateRange>(getCurrentWeekRangeS());
  const [week, setWeek] = useState<string>();
  const [filteredData, setFilteredData] = useState<UserStats[]>([]);
  const [dataSelectionLoading, setDataSelectionLoading] = useState(false);
  const [genderFilter, setGenderFilter] = useState<string>("All");
  const [performanceFilter, setPerformanceFilter] = useState<string>("All");
  const [showAggregatedView, setShowAggregatedView] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<any>();
  
  const [generalAggregateCountStats, setGeneralAggregateCountStats] = useState<GeneralAggregateCountStats>();
  const [aggregatedData, setAggregatedData] = useState<AggregatedData>({
    gender: {},
    performance: {},
  });
  const [scoringCriteriaDrawer, setScoringCriteriaDrawer] = useState(false);
  const [width, setWidth] = useState(540);
  const [isResizing, setIsResizing] = useState(false);
  const {batch, role} = useAppSelector((state)=> state.user)
  const {contentCollapsed} = useAppSelector((state)=> state.tabs)

  useEffect(() => {
    const onMouseMoveHandler = (e: MouseEvent) => {
      if (isResizing) {
        const offsetRight =
          document.body.offsetWidth - (e.clientX - document.body.offsetLeft);
        const minWidth = 540;
        if (offsetRight > minWidth) {
          setWidth(offsetRight);
        }
      }
    };
    document.addEventListener("mousemove", onMouseMoveHandler);
    document.addEventListener("mouseup", onMouseUp);

    return () => {
      document.removeEventListener("mousemove", onMouseMoveHandler);
      document.removeEventListener("mouseup", onMouseUp);
    };
  }, [isResizing]);

  const handleMaximize = () => {
    const newWidth = width === 2000 ? 540 : 2000;
    setWidth(newWidth);
  };
  const onMouseDown = () => setIsResizing(true);
  const onMouseUp = () => setIsResizing(false);

  const calculateAggregatedData = useCallback(
    (data: UserStats[]): AggregatedData => {
      const aggregated: AggregatedData = {
        gender: {},
        performance: {},
      };

      data.forEach((user) => {
        (["gender", "performance"] as const).forEach((category) => {
          const key =
            category === "gender"
              ? user.Gender
              : user.Intensive_Training_Performance;
          if (!aggregated[category][key]) {
            aggregated[category][key] = {
              successProbability: 0,
              interested: 0,
              applied: 0,
              rejections: 0,
              interviews: 0,
              offers: 0,
              challengesCompleted: 0,
              standupAttendance: 0,
              count: 0,
            };
          }
          aggregated[category][key].successProbability += parseFloat(
            user.Success_Probability.replace("%", "")
          );
          aggregated[category][key].interested += user.Interested;
          aggregated[category][key].applied += user.Applied;
          aggregated[category][key].rejections += user.Rejections;
          aggregated[category][key].interviews += user.Interviews;
          aggregated[category][key].offers += user.Offers;
          aggregated[category][key].challengesCompleted +=
            user.Challenges_Completed;
          aggregated[category][key].standupAttendance +=
            user.Standup_Attendance;
          aggregated[category][key].count++;
        });
      });

      (["gender", "performance"] as const).forEach((category) => {
        Object.keys(aggregated[category]).forEach((key) => {
          const stats = aggregated[category][key];

          // divide the sum of each stat by the count to get the average(per person value)
          stats.successProbability = parseFloat(
            (stats.successProbability / stats.count).toFixed(2)
          );

          stats.interested = parseFloat(
            (stats.interested / stats.count).toFixed(2)
          );
          stats.applied = parseFloat((stats.applied / stats.count).toFixed(2));
          stats.rejections = parseFloat(
            (stats.rejections / stats.count).toFixed(2)
          );
          stats.interviews = parseFloat(
            (stats.interviews / stats.count).toFixed(2)
          );
          stats.offers = parseFloat((stats.offers / stats.count).toFixed(2));

          // Calculate percentages for challenges and standup attendance
          stats.challengesCompleted = Number(
            (
              (stats.challengesCompleted / (stats.count * numOfAssignments)) *
              100
            ).toFixed(2)
          );
          stats.standupAttendance = Number(
            ((stats.standupAttendance / (stats.count * 5)) * 100).toFixed(2)
          );
        });
      });

      return aggregated;
    },
    [numOfAssignments]
  );

  const { makeRequest, loading } = useAxiosRequest(); 
  const fetchDataWithPost = () => {
    try {
      const startDate = formatToISO(dateRange?.from);
      const endDate = formatToISO(dateRange?.to);
  
      const requestData = {
        user_role: role,
        prod_run_stage: true,
        run_stage: "dev",
        filter: {
          batch: batch,
          week: week,
          start_date: startDate,
          end_date: endDate,
        },
      };  
      makeRequest({
        url: '/sjob/get-general-leaderboard',
        method: 'POST',
        data: requestData,
        onSuccess: (response) => {
          setResponse(response.data);
        },
        onError: (error) => {
          setError(`Error fetching data from the server: ${error}`);
        }
      });
    } catch (error) {
      setError(`Error fetching data from the server: ${error}`);
    }
  };
  
  useEffect(() => {
    fetchDataWithPost();
  }, [week, batch, genderFilter, performanceFilter]); 

  useEffect(() => {
    if (response) {
      setData([...response.stats]);
      setWeeks([...response.weeks]);
      if (!week && response.weeks.length > 0) {
        setWeek(response.weeks.at(-1));
      }
      setNumOfAssignments(response.num_of_assignments);
    }
  }, [response]);

  useEffect(() => {
    const newFilteredData = data.filter(
      (user) =>
        (genderFilter === "All" || user.Gender === genderFilter) &&
        (performanceFilter === "All" ||
          user.Intensive_Training_Performance === performanceFilter)
    );
    setFilteredData(newFilteredData);
    const aggregateData = calculateAggregatedData(newFilteredData);
    setAggregatedData(aggregateData);
    setGeneralAggregateCountStats({
      maleCount: aggregateData?.gender?.Male?.count || 0,
      femaleCount: aggregateData?.gender?.Female?.count || 0,
      excellentPerformers: aggregateData?.performance?.Excellent?.count || 0,
      goodPerformers: aggregateData?.performance?.Good?.count || 0,
      poorPerformers: aggregateData?.performance?.Poor?.count || 0,
    });
  }, [calculateAggregatedData, data, genderFilter, performanceFilter]);


  const getApplicationStats = () => {
    if (!showAggregatedView) {
      const applicationStats = filteredData.map((user) => ({
        name: user.Name.split(" ")[0],
        Interested: user.Interested,
        Applied: user.Applied,
        Rejections: user.Rejections,
        Interviews: user.Interviews,
        Offers: user.Offers,
      }));

      applicationStats.sort(
        (a, b) =>
          b.Interested +
          b.Applied +
          b.Rejections +
          b.Interviews +
          b.Offers -
          (a.Interested + a.Applied + a.Rejections + a.Interviews + a.Offers)
      );

      return applicationStats;
    } else {
      return Object.entries(aggregatedData.gender)
        .map(([gender, stats]) => ({
          name: gender,
          Interested: stats.interested,
          Applied: stats.applied,
          Rejections: stats.rejections,
          Interviews: stats.interviews,
          Offers: stats.offers,
          Count: stats.count,
        }))
        .concat(
          Object.entries(aggregatedData.performance).map(
            ([performance, stats]) => ({
              name: performance,
              Interested: stats.interested,
              Applied: stats.applied,
              Rejections: stats.rejections,
              Interviews: stats.interviews,
              Offers: stats.offers,
              Count: stats.count,
            })
          )
        );
    }
  };

  const getEngagementStats = () => {
    if (!showAggregatedView) {
      return filteredData.map((user) => ({
        name: user.Name.split(" ")[0],
        "Challenges Completed(%)":
          (user.Challenges_Completed / numOfAssignments) * 100,
        "Standup Attendance(%)": (user.Standup_Attendance / 5) * 100,
      }));
    }
    return Object.entries(aggregatedData.gender)
      .map(([gender, stats]) => ({
        name: gender,
        "Challenges Completed(%)": stats.challengesCompleted,
        "Standup Attendance(%)": stats.standupAttendance,
      }))
      .concat(
        Object.entries(aggregatedData.performance).map(
          ([performance, stats]) => ({
            name: performance,
            "Challenges Completed(%)": stats.challengesCompleted,
            "Standup Attendance(%)": stats.standupAttendance,
          })
        )
      );
  };

  const handleFetchDataSelection = async () => {
    try {
      if (!dateRange.from || !dateRange.to) {
        message.error("Please select a date range");
        return;
      }
      setDataSelectionLoading(true);
       fetchDataWithPost();
      setDataSelectionLoading(false);
    } catch (err: any) {
      setDataSelectionLoading(false);
    }
  };

  const onDateRangeChanged = (dates: [Dayjs | null, Dayjs | null] | null) => {
    if (dates) {
      setDateRange({
        from: dates[0]?.toDate() || undefined,
        to: dates[1]?.toDate() || undefined,  
      });
    }
  };

  const getSuccessProbability = () => {
    if (!showAggregatedView) {
      return filteredData.map((user) => ({
        name: user.Name.split(" ")[0],
        "Success Probability": parseFloat(
          user.Success_Probability.replace("%", "")
        ),
        Remaining: 100 - parseFloat(user.Success_Probability.replace("%", "")),
      }));
    }
    return Object.entries(aggregatedData.gender)
      .map(([gender, stats]) => ({
        name: gender,
        "Success Probability": stats.successProbability,
        Remaining: 100 - stats.successProbability,
      }))
      .concat(
        Object.entries(aggregatedData.performance).map(
          ([performance, stats]) => ({
            name: performance,
            "Success Probability": stats.successProbability,
            Remaining: 100 - stats.successProbability,
          })
        )
      );
  };

  if(error) return <ServerError/>

  return (
    <Row gutter={16} className={`mt-32 ${contentCollapsed} ? "stats__content-collapsed":"stats__content-not_collapsed"`} style={{
      marginBottom:"2rem"}}>
      <Col span={24}>
        <Row gutter={16} className="stats__header-wrapper">
          <Col span={24}>
            <div  className="d-flex-between stats__header-container">
              <p className="stats__header" >Trainee's SJS Performance Dashboard</p>
              <div className="flex-center gap-16 cursor-pointer">
                <div className="flex-center gap-8">
                  <CSVExportButton<UserStats>
                    data={filteredData}
                    filename="Trainee-SJS-Performance.csv"
                    title="SJS Dashboard Export"
                    filterParams={{
                      Batch: batch,
                      Week: week ?? "",
                      Gender: genderFilter,
                      Performance: performanceFilter,
                      "Job Application Date Range": formatDateRange(dateRange),
                    }}
                  />
                </div>
                <p className="stats__scoring-criteria" onClick={()=> setScoringCriteriaDrawer(true)}>Scoring Criteria</p>
              </div>
            </div>
          </Col>
        </Row>
        <Row gutter={16} className="mt-16 stats__content">
          <Col xs={24} lg={6}>
            <Card title={<div>Data Selection</div>}>
            <Paragraph>Assignment & Challenge Week</Paragraph>
            <Select
              showSearch
              style={{ width: "100%" }}
              placeholder="Search to Select"
              optionFilterProp="label"
              onChange={(value) => setWeek(value)}
              filterSort={(optionA, optionB) =>
                (optionA?.label ?? '').toLowerCase().localeCompare((optionB?.label ?? '').toLowerCase())
              }
              options={weeks.map((week) => ({
                value: week, 
                label: week
              }))}
          />

            <Paragraph className="mt-16">Job Application Week</Paragraph>
            <RangePicker
                status="warning"
                value={convertToDayjsRange(dateRange)}
                onChange={onDateRangeChanged}
              />

              <Button className="mt-16 fetch__data-btn" onClick={handleFetchDataSelection}>
                Fetch Data
              </Button>
            </Card>
          </Col>
          <Col xs={24} lg={18}>
              <Card>
                <Row gutter={16}>
                  <Col xs={24} lg={8}>
                    <Paragraph>Gender Filter</Paragraph>
                    <Select
                        showSearch
                        style={{ width: "100%" }}
                        placeholder="Search to Select"
                        optionFilterProp="label"
                        filterSort={(optionA, optionB) =>
                          (optionA?.label ?? '').toLowerCase().localeCompare((optionB?.label ?? '').toLowerCase())
                        }
                        options={[
                          {
                            value: 'All',
                            label: 'All',
                          },
                          {
                            value: 'Male',
                            label: 'Male',
                          },
                          {
                            value: 'Female',
                            label: 'Female',
                          }
                        ]}
                        value={genderFilter}
                        onChange={(value) => setGenderFilter(value)}
                      />
                  </Col>
                  <Col xs={24} lg={8}>
                  <Paragraph>Performance Filter</Paragraph>  
                  <Select
                      showSearch
                      style={{ width: "100%" }}
                      placeholder="Search to Select"
                      optionFilterProp="label"
                      filterSort={(optionA, optionB) =>
                        (optionA?.label ?? '').toLowerCase().localeCompare((optionB?.label ?? '').toLowerCase())
                      }
                      options={[
                        {
                          value: '1All',
                          label: 'All',
                        },
                        {
                          value: 'Poor',
                          label: 'Poor',
                        },
                        {
                          value: 'Good',
                          label: 'Good',
                        }, 
                        { 
                          value: 'Excellent',
                          label: 'Excellent',
                        }
                      ]}
                      value={performanceFilter}
                      onChange={(value) => setPerformanceFilter(value)}
                    />
                  </Col>
                  <Col xs={24} lg={8}>
                  <Paragraph>Show Aggregated View</Paragraph>
                    <Switch  checked={showAggregatedView} onChange={setShowAggregatedView} />
                  </Col>
                </Row>
              </Card>
             
                <Card className="mt-8" style={{
                  paddingBottom: "1rem"
                }} title={<>
                  <div className="mt-16"> Success Probability {showAggregatedView && "(Per person)"}</div>
                  <p className="success__probability-sub-title">This chart shows how likely a trainee is to succeed based on Job Application Efforts, Challenges Completed, and Standup Attendance</p>
                  {showAggregatedView && generalAggregateCountStats && (
                    <CountStats
                      maleCount={generalAggregateCountStats.maleCount}
                      femaleCount={generalAggregateCountStats.femaleCount}
                      excellentPerformers={
                        generalAggregateCountStats.excellentPerformers
                      }
                      goodPerformers={generalAggregateCountStats.goodPerformers}
                      poorPerformers={generalAggregateCountStats.poorPerformers}
                    />
                  )}
                </>}>
                {(loading || dataSelectionLoading) ? <StaffDataLoader /> :
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart
                      data={getSuccessProbability()}
                      {...{
                        overflow: "visible",
                      }}
                    >
                      <CartesianGrid />
                      <XAxis dataKey="name" fontSize={12} interval={0} angle={-45} />
                      <YAxis
                        domain={[0, 100]}
                        label={{
                          value: "Percentage (%)",
                          angle: -90,
                          position: "insideLeft",
                        }}
                      />
                      <Tooltip
                        content={
                          <CustomSuccessProbabilityTooltip
                            engagements={getEngagementStats()}
                            applications={getApplicationStats()}
                            showAggregatedView={showAggregatedView}
                            aggregatedData={aggregatedData}
                          />
                        }
                      />
                      <Legend
                        wrapperStyle={{
                          position: "relative",
                          marginTop: "1px",
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="Success Probability"
                        stroke="#8884d8"
                        activeDot={{ r: 8 }}
                      />
                    </LineChart>
                </ResponsiveContainer>
                }
              </Card>
              <Card className="mt-8" title={<>
                  <div className="mt-16">Job Application Statistics {showAggregatedView ? "(Per person)" : ""}</div>
                  <p className="success__probability-sub-title">{formatDateRange(dateRange)}</p>
                  {showAggregatedView && generalAggregateCountStats && (
                  <CountStats
                    maleCount={generalAggregateCountStats.maleCount}
                    femaleCount={generalAggregateCountStats.femaleCount}
                    excellentPerformers={
                      generalAggregateCountStats.excellentPerformers
                    }
                    goodPerformers={generalAggregateCountStats.goodPerformers}
                    poorPerformers={generalAggregateCountStats.poorPerformers}
                  />
                )}
                </>}>
                {(loading || dataSelectionLoading) ? <StaffDataLoader /> :
                <JobApplicationStats
                  applications={getApplicationStats()}
                />
                } 
              </Card>
              <Card className="mt-8" style={{
                paddingBottom: "2rem"
              }} title={<>
                  <div className="mt-16"> Engagement Metrics {showAggregatedView && "(Per person)"}</div>
                  <p className="success__probability-sub-title">{week}</p>
                  {showAggregatedView && generalAggregateCountStats && (
                  <CountStats
                    maleCount={generalAggregateCountStats.maleCount}
                    femaleCount={generalAggregateCountStats.femaleCount}
                    excellentPerformers={
                      generalAggregateCountStats.excellentPerformers
                    }
                    goodPerformers={generalAggregateCountStats.goodPerformers}
                    poorPerformers={generalAggregateCountStats.poorPerformers}
                  />
                )}
                </>}>
                {(loading || dataSelectionLoading) ? <StaffDataLoader /> :
                  <EngagementMetrics
                    engagements={getEngagementStats()}
                />
                }
              </Card>
          </Col>
        </Row>
      </Col>
          <Drawer
           title={<div className="d-flex-between" style={{ marginRight: "1.25rem" }}>Scoring Criteria
           <Button
             type='text'
             style={{ border: 'none' }}
             icon={width === 2000 ? <Minimize01 /> : <Maximize01 />}
             onClick={handleMaximize} />
         </div>}
            placement="right"
            closable={true}
            onClose={() => setScoringCriteriaDrawer(false)}
            open={scoringCriteriaDrawer}
            width={width}
            className="close-btn-position"
          >
          <div className="dynamic-drawer-width" onMouseDown={onMouseDown} />
              <ScoringCriteria/>
          </Drawer> 
    </Row>
  )
}
