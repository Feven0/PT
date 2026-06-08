import { useEffect, useState } from "react";
import { PlusOutlined, InfoCircleOutlined, CloseOutlined } from "@ant-design/icons";
import { Tag, Input, Button, Form, Select, message, Row, Col } from "antd";
import axios from "axios";

import { useAppDispatch, useAppSelector } from "../../../redux/hooks/hooks";
import { addLocation, removeLocation, updateLocationPriority } from "../../../redux/slices/Preferences/locationSlices";
import { capitalizeFirstChar, priorityLevels } from "../../../utils/commonUtils";
import { useIconRender } from "../../../hooks/useIconRender";
import AddNewPref from "./Empty/AddNewPref";
import { setPreferenceControlTag } from "../../../redux/slices/Preferences/preferenceControlSlice";
import "../../../styles/preference.css";

export default function LocationPreference() {
  const [selectedLocation, setSelectedLocation] = useState<string | null>(null);
  const [newPriority, setNewPriority] = useState<"high" | "medium" | "low" | null>(null);
  const [addingNewLocation, setAddingNewLocation] = useState(false)
  const [formValues, setFormValues] = useState<{ country: string; state: string; city: string; priority: "high" | "medium" | "low" | null }>({
    country: "",
    state: "",
    city: "", 
    priority: null,
  });
  const [nationalities, setNationalities] = useState<{ label: string, value: string }[]>([]);
  const { locations } = useAppSelector((state) => state.locationPreference);
  const [form] = Form.useForm();
  const dispatch = useAppDispatch();

  const { renderIcon } = useIconRender();

  useEffect(() => {
    const fetchNationalities = async () => {
      try {
        const response = await axios.get('https://restcountries.com/v3.1/all');
        const nationalitiesData = response.data;

        const formattedNationalities = nationalitiesData.map((country: any) => ({
          label: country.name.common,
          value: country.name.common,
        }));

        formattedNationalities.sort((a:any, b:any) => a.label.localeCompare(b.label));
        const additionalLocations = [
          { label: 'Remote', value: 'Remote' },
          { label: 'EMEA', value: 'EMEA' },
          { label: 'Europe', value: 'Europe' },
          { label: 'Asia', value: 'Asia' },
          { label: 'Africa', value: 'Africa' },
          { label: 'Anywhere', value: 'Anywhere' },
        ];
        setNationalities([...additionalLocations, ...formattedNationalities]);
      } catch (error) {
        console.error('Error fetching nationalities:', error);
      }
    };

    fetchNationalities();
  }, []);

  const handleLocationClick = (locationCountry: string) => {
    if (selectedLocation === locationCountry) {
      setSelectedLocation(null);
      setNewPriority(null); 
    } else {
      setSelectedLocation(locationCountry);
      setNewPriority(null);
    }
  };

  const handlePriorityClick = (priority: "high" | "medium" | "low" | null) => {
    setNewPriority(priority);
    if (selectedLocation) {
      dispatch(updateLocationPriority({ country: selectedLocation, priority }));
      dispatch(setPreferenceControlTag(true));
      setSelectedLocation(null);
      setTimeout(() => setNewPriority(null), 1000);
    }
  };

  const handleAddLocation = () => {
    if (!newPriority) {
      message.error('Please select a priority level');
      return;
    }
    if (formValues.country) {
      dispatch(addLocation({ ...formValues, priority: newPriority }));
      dispatch(setPreferenceControlTag(true));
      setFormValues({ country: "", state: "", city: "", priority: "medium" });
      form.resetFields();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormValues((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleTagClose = (locationCountry: string) => {
    dispatch(removeLocation(locationCountry));
    dispatch(setPreferenceControlTag(true));
    if (selectedLocation === locationCountry) {
      setSelectedLocation(null);
    }
  };

  const handleAddRoleClick = () => setAddingNewLocation(!addingNewLocation);

  return (
    <>
      <div className="d-flex-between roles-header mb-8">
        <span className="preference__header__title">Location</span>
      </div>

      <div className="description-text">
        <InfoCircleOutlined />
        <span style={{ marginLeft: "8px" }}>
          Selected locations will narrow down jobs to those available in your preferred region or city
        </span>
      </div>

      {(locations?.length === 0 && !addingNewLocation) ? (
       <AddNewPref
          desc="Refine your search by the type of location, like Europe, Asia, Anywhere, etc..."
          showAddButton={handleAddRoleClick}
          />
      ) : (
        <div className="company-size-tags-div mt-16 industry-tag-div">
          {locations?.map((location) => (
            <Tag
              key={location.country}
              className="preference__tags roles-tag"
              color={selectedLocation === location.country ? "#FF4405" : undefined}
              style={{ padding: "4px 8px", cursor: 'pointer', fontSize:"14px" }}
              closable={selectedLocation === location.country}
              onClick={() => handleLocationClick(location.country)}
              onClose={() => handleTagClose(location.country)}
            >
              {renderIcon(location.priority)}
              {capitalizeFirstChar(location.country)}
            </Tag>
          ))}
           <Button
            style={{ 
              borderColor: '#FF4405',
              background: addingNewLocation ? '#FF4405' : 'white',
              color: addingNewLocation ? 'white' : '#000',
              opacity: addingNewLocation ? 1 : 0.7,
            }}
            icon={ !addingNewLocation ? <PlusOutlined /> : <CloseOutlined />}
           onClick={handleAddRoleClick}
        >
           {addingNewLocation ? 'Cancel' : 'New'}
        </Button>
        </div>
      )}

      {(selectedLocation || addingNewLocation) && (
        <div className="mt-16 mb-16 location__priority">
          <div className="mt-4">
            {priorityLevels?.map((priority) => (
              <Tag
                key={priority}
                color={newPriority === priority ? '#FF4405' : undefined}
                style={{
                  color: newPriority === priority ? '#fff' : '#000',
                  cursor: 'pointer',
                  marginBottom: '0.5rem',
                  padding: '0.25rem 0.5rem',
                }}
                onClick={() => handlePriorityClick(priority)}
              >
                {priority.charAt(0).toUpperCase() + priority.slice(1)}
              </Tag>
            ))}
          </div>
        </div>
      )}
       {addingNewLocation &&
       <div className="location__form">
          <Form layout="vertical" form={form} className="location__input__wrapper">
            <Row gutter={16}>
              <Col xs={24} lg={8}>
                <Form.Item
                  label="Country (required)"
                  name="country"
                  rules={[{ required: true, message: "Field is required!" }]}
                  labelCol={{ span: 24 }}
                >
                  <Select
                    showSearch
                    value={formValues.country}
                    onChange={(value) => setFormValues((prev) => ({ ...prev, country: value }))}
                    placeholder="Select a location"
                  >
                    {nationalities.map((opt) => (
                      <Select.Option key={opt.value} value={opt.value}>
                        {opt.label}
                      </Select.Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col xs={24} lg={8}>
                <Form.Item label="State (optional)" name="state">
                  <Input
                    placeholder="State (optional)"
                    name="state"
                    value={formValues.state}
                    onChange={handleInputChange}
                  />
                </Form.Item>
              </Col>
              <Col xs={24} lg={8}>
                <Form.Item label="City (optional)" name="city">
                  <Input
                    placeholder="City (optional)"
                    name="city"
                    value={formValues.city}
                    onChange={handleInputChange}
                  />
                </Form.Item>
              </Col>
            </Row>
            <Form.Item className="d-flex-center">
              <Button onClick={handleAddLocation} className="dark-orange-bg white-color primary-button">
                Add Location
              </Button>
            </Form.Item>
          </Form>
        </div>
       }
    </>
  );
}
