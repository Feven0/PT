import React, { useState } from 'react';
import { Input, Form, Tooltip } from 'antd';

const ChartTest = () => {
  const [input, setInput] = useState('');
  const [error, setError] = useState('');
  const charLimit = 200; 

  const handleChange = (e) => {
      const newInput = e.target.value;

      if (newInput.length <= charLimit) {
          setInput(newInput);
          setError('');
      } else {
          setError(`Character limit of ${charLimit} exceeded.`);
      }
  };

  return (
      <Form>
          <Form.Item>
              <Input.TextArea
                  value={input}
                  placeholder="Put your answer here"
                  onChange={handleChange}
                  rows={2}
                  className="input-area"
              />
              <div style={{ marginTop: '5px' }}>
                  <span>{`Character Count: ${input.length}/${charLimit}`}</span>
              </div>
              {error && (
                  <Tooltip title={error} color="red">
                      <span style={{ color: 'red', marginTop: '5px', display: 'block' }}>
                          {error}
                      </span>
                  </Tooltip>
              )}
          </Form.Item>
      </Form>
  );
};

export default ChartTest;