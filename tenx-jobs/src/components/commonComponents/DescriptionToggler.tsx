import { useState } from 'react';
import Linkify from 'react-linkify';

type DescriptionToggleProps = {
  bio: string;
  maxDescriptionLength: number;
}

export default function DescriptionToggle({ bio, maxDescriptionLength }:DescriptionToggleProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleDescription = () =>  setIsExpanded(!isExpanded);

  return (
    <p className="mt-8">
    {isExpanded ? (
      <>
        <Linkify>{bio}</Linkify> {"   "} &nbsp; &nbsp;
        <span className="cursor-pointer dark-orange-color" onClick={toggleDescription}>
          Show Less
        </span>
      </>
    ) : (
      <>
        {bio.length > maxDescriptionLength
          ? (
            <>
              <Linkify>{bio.substring(0, maxDescriptionLength)}</Linkify> ...
            </>
          )
          : <Linkify>{bio}</Linkify>
        }
        {bio.length > maxDescriptionLength && (
          <span className="cursor-pointer dark-orange-color" onClick={toggleDescription}>
            &nbsp; Read More
          </span>
        )}
      </>
    )}
  </p>
  );
}

