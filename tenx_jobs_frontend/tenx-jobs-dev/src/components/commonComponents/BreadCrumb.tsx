import React from "react";
import { Link, useLocation } from "react-router-dom";

export const BreadCrumb = () => {
  const location = useLocation();
  const { pathname } = location;
  
  // Split the pathname into segments, filter out empty segments
  const segments = pathname.split('/').filter((segment) => segment !== '');

  let url = '';

  // Helper function to create readable labels for each segment
  const getSegmentLabel = (segment: string) => {
    if (!isNaN(Number(segment))) {
      return null; // Ignore numeric segments (IDs)
    }
    switch (segment) {
      case 'staff':
        return 'Home'; // Treat /staff as Home
      case 'trainee_details':
        return 'Trainee Details'; // Convert to readable label
      case 'trainee_engagements':
        return 'Trainee Engagements'; // Convert to readable label
      default:
        // Capitalize and format other segments
        return segment
          .split('-')
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');
    }
  };

  const breadCrumbLinks = segments.map((segment, index) => {
    url += `/${segment}`; // Construct the full URL segment by segment

    const isLastSegment = index === segments.length - 1;

    // Get readable label for the segment
    const label = getSegmentLabel(segment);
    if (!label) return null;

    const linkStyle = {
      color: '#000',
      opacity: isLastSegment ? 1 : 0.5,
    };

    // Check if it's a dynamic route with parameters (like /staff/trainee_details/:id/:profile_id)
    if (segment === 'trainee_details' && !isLastSegment) {
      // Ensure the URL includes the dynamic parameters by adding the remaining path segments
      url += `/${segments[index + 1]}/${segments[index + 2]}`;
    } else if (segment === 'trainee_engagements' && !isLastSegment) {
      // Ensure the URL includes the dynamic parameters by adding the remaining path segments
      url += `/${segments[index + 1]}/${segments[index + 2]}`;
    }

    return (
      <React.Fragment key={index}>
        {index > 0 && ' > '}
        {isLastSegment ? (
          <span style={linkStyle}>{label}</span>
        ) : (
          <Link to={url} style={linkStyle}>
            {label}
          </Link>
        )}
      </React.Fragment>
    );
  });

  return (
    <div>
      {breadCrumbLinks}
    </div>
  );
};
