import { useEffect } from "react";
import { InfoCircleOutlined } from '@ant-design/icons';
import { Col, Divider, Form, Row, Slider } from "antd";

import { useAppSelector, useAppDispatch } from "../../../redux/hooks/hooks";
import { setDaysExtracted } from "../../../redux/slices/Preferences/jobFilterSlice";
import { setPreferenceControlTag } from "../../../redux/slices/Preferences/preferenceControlSlice";

export default function JobFilter() {
  const dispatch = useAppDispatch();
  const { days_extracted } = useAppSelector((state) => state.jobFilter);
  const [form] = Form.useForm();

  useEffect(() => {
    form.setFieldsValue({
      days_since_extracted: days_extracted,
    });
  }
    , [days_extracted]);
    
  
  return (
    <>
      <div className="d-flex-between roles-header">
          <span className="preference__header__title">Job Extraction</span>
           <div className="flex-center gap-8">
          {days_extracted}{""} {days_extracted === 1 ? "day" : "days"}
        </div>
        </div>
        <div className="description-text">
          <InfoCircleOutlined />
          <span style={{ marginLeft: "8px" }}>
            Write a date here to view job postings from that specific day onwards, ensuring your search results show only the most recent Jobs.
          </span>
      </div>
      <div className="company-size-tags-div mt-8 industry-tag-div">
        <Row gutter={16} className="full-width">
          <Col span={24}>
            <div>Days since extracted</div>
            <Slider
                  step={1}
                  min={1}
                  max={100}
                  value={days_extracted ?? 5}
                  onChange={(value) => {
                    if (value !== null && value !== undefined) {
                      dispatch(setDaysExtracted(value));
                      dispatch(setPreferenceControlTag(true));
                    }
                  }}
                />
          </Col>
        </Row>
      </div>
      <Divider />
    </>
  );
}
