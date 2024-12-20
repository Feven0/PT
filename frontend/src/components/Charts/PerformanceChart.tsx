import { useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Input, Button, Row, Col } from 'antd';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);
interface Data {
  data: any
}


const PerformanceChart: React.FC<Data> =({ data }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [filteredData, setFilteredData] = useState(data);
  const itemsPerPage = 3;


  // Function to filter out users with missing metric values
  const getValidUsers = (filteredData: any) => {
    return filteredData.filter((user: any) => {
      return (
        user.metrics.average_confidence_level !== null &&
        user.metrics.average_confidence_level !== undefined &&
        user.metrics.average_clarity_level !== null &&
        user.metrics.average_clarity_level !== undefined &&
        user.metrics.average_engagement_level !== null &&
        user.metrics.average_engagement_level !== undefined
      );
    });
  };

  // Pagination handling functions
  const nextPage = () => {
    if (currentPage * itemsPerPage < filteredData.length) {
      setCurrentPage(currentPage + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleSearch = (value: any) => {
    if (value) {
      const filtered = data.filter((user: any) =>
        user.name.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredData(getValidUsers(filtered));
      setCurrentPage(1); // Reset to first page when filtering
    } else {
      setFilteredData(getValidUsers(data)); // Reset to full data when search is cleared
      setCurrentPage(1); // Reset to first page when search is cleared
    }
  };

  // Get the current page data slice after filtering out invalid users
  const pageData = getValidUsers(filteredData).slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  return (
    <div>
      {/* Search bar */}
      <Row style={{ marginBottom: 20 }}>
        <Col span={24}>
          <Input
            placeholder="Search by user name"
            onChange={(e) => handleSearch(e.target.value)}
          />
        </Col>
      </Row>

      {/* Chart Display */}
      <Bar
        style={{ width: "100%", height: "25rem" }}
        data={{
          labels: pageData.map((user: any) => user.name),
          datasets: [
            {
              label: "Confidence Level",
              backgroundColor: "rgba(75,192,192,0.6)",
              borderColor: "rgba(75,192,192,1)",
              borderWidth: 1,
              hoverBackgroundColor: "rgba(75,192,192,0.8)",
              hoverBorderColor: "rgba(75,192,192,1)",
              data: pageData.map((user: any) => user.metrics.average_confidence_level),
            },
            {
              label: "Clarity Level",
              backgroundColor: "rgba(153,102,255,0.6)",
              borderColor: "rgba(153,102,255,1)",
              borderWidth: 1,
              hoverBackgroundColor: "rgba(153,102,255,0.8)",
              hoverBorderColor: "rgba(153,102,255,1)",
              data: pageData.map((user: any) => user.metrics.average_clarity_level),
            },
            {
              label: "Engagement Level",
              backgroundColor: "rgba(255,159,64,0.6)",
              borderColor: "rgba(255,159,64,1)",
              borderWidth: 1,
              hoverBackgroundColor: "rgba(255,159,64,0.8)",
              hoverBorderColor: "rgba(255,159,64,1)",
              data: pageData.map((user: any) => user.metrics.average_engagement_level),
            },
          ],
        }}
        options={{          
            responsive: true,
            plugins: {
              legend: {
                position: "top",
              },
              title: {
                display: true,
                text: "User Performance Levels",
              },
            },
            scales: {
              y: {
                beginAtZero: true,
                max: 3,
              },
            },
        }}
      />

      {/* Pagination Controls */}
      <Row style={{ marginTop: 20 }}>
        <Col span={24} style={{ textAlign: "center" }}>
          <Button onClick={prevPage} disabled={currentPage === 1}>
            Previous
          </Button>
          <Button
            onClick={nextPage}
            disabled={currentPage * itemsPerPage >= filteredData.length}
            style={{ marginLeft: 20 }}
          >
            Next
          </Button>
        </Col>
      </Row>
    </div>
  );
};

export default PerformanceChart;
