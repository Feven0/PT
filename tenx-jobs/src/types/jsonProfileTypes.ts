import { JSONSchemaType } from 'ajv';

type Resume = {
  $schema: string;
  basics: {
    name: string;
    label: string;
    image: string;
    email: string;
    phone: string;
    url: string;
    summary: string;
    location: {
      countryCode: string;
      address: string;
    };
    profiles: {
      network: string;
      username: string;
      url: string;
    }[];
  };
  work: {
    name: string;
    position: string;
    startDate: string;
    endDate: string;
    highlights: string[];
    summary: string;
    url: string;
    location: string;
  }[];
  volunteer: {
    organization: string;
    position: string;
    startDate: string;
    endDate: string;
    summary: string;
    highlights: string[];
    url: string;
  }[];
  education: {
    institution: string;
    area: string;
    studyType: string;
    startDate: string;
    endDate: string;
    score: string;
    courses: string[];
  }[];
  awards: {
    title: string;
    date: string;
    issuer: string;
    url: string;
  }[];
  certificates: {
    name: string;
    issuer: string;
    startDate: string;
    url: string;
  }[];
  publications: {
    name: string;
    publisher: string;
    releaseDate: string;
    summary: string;
    url: string;
  }[];
  skills: {
    name: string;
    level: string;
    keywords: string[];
  }[];
  languages: {
    fluency: string;
    language: string;
  }[];
  interests: string[];
  references: {
    name: string;
    reference: string;
  }[];
  projects: {
    name: string;
    startDate: string;
    endDate: string;
    summary: string;
    url: string;
    keywords: string[];
  }[];
};

export const resumeSchema: JSONSchemaType<Resume> = {
  $schema: "http://json-schema.org/draft-04/schema#",
  additionalProperties: false,
  properties: {
    $schema: {
      type: "string",
      format: "uri"
    },
    basics: {
      type: "object",
      properties: {
        name: { type: "string" },
        label: { type: "string" },
        image: { type: "string" },
        email: { type: "string", format: "email" },
        phone: { type: "string" },
        url: { type: "string", format: "uri" },
        summary: { type: "string" },
        location: {
          type: "object",
          properties: {
            address: { type: "string" },
            countryCode: { type: "string" }
          },
          required: ["countryCode", "address"],
          additionalProperties: false
        },
        profiles: {
          type: "array",
          items: {
            type: "object",
            properties: {
              network: { type: "string" },
              username: { type: "string" },
              url: { type: "string", format: "uri" }
            },
            required: ["network", "username", "url"],
            additionalProperties: false
          }
        }
      },
      required: [
        "name", "label", "image", "email", "phone", "url", "summary", "location", "profiles"
      ],
      additionalProperties: false
    },
    work: {
      type: "array",
      items: {
        type: "object",
        properties: {
          name: { type: "string" },
          position: { type: "string" },
          startDate: { $ref: "#/definitions/iso8601" },
          endDate: { $ref: "#/definitions/iso8601" },
          highlights: {
            type: "array",
            items: { type: "string" }
          },
          summary: { type: "string" },
          url: { type: "string", format: "uri" },
          location: { type: "string" }
        },
        required: [
          "name", "position", "startDate", "endDate", "highlights", "summary", "url", "location"
        ],
        additionalProperties: false
      }
    },
    volunteer: {
      type: "array",
      items: {
        type: "object",
        properties: {
          organization: { type: "string" },
          position: { type: "string" },
          startDate: { $ref: "#/definitions/iso8601" },
          endDate: { $ref: "#/definitions/iso8601" },
          summary: { type: "string" },
          highlights: {
            type: "array",
            items: { type: "string" }
          },
          url: { type: "string", format: "uri" }
        },
        required: [
          "organization", "position", "startDate", "endDate", "summary", "highlights", "url"
        ],
        additionalProperties: false
      }
    },
    education: {
      type: "array",
      items: {
        type: "object",
        properties: {
          institution: { type: "string" },
          area: { type: "string" },
          studyType: { type: "string" },
          startDate: { $ref: "#/definitions/iso8601" },
          endDate: { $ref: "#/definitions/iso8601" },
          score: { type: "string" },
          courses: {
            type: "array",
            items: { type: "string" }
          }
        },
        required: [
          "institution", "area", "studyType", "startDate", "endDate", "score", "courses"
        ],
        additionalProperties: false
      }
    },
    awards: {
      type: "array",
      items: {
        type: "object",
        properties: {
          title: { type: "string" },
          date: { $ref: "#/definitions/iso8601" },
          issuer: { type: "string" },
          url: { type: "string", format: "uri" }
        },
        required: ["title", "date", "issuer", "url"],
        additionalProperties: false
      }
    },
    certificates: {
      type: "array",
      items: {
        type: "object",
        properties: {
          name: { type: "string" },
          issuer: { type: "string" },
          startDate: { $ref: "#/definitions/iso8601" },
          url: { type: "string", format: "uri" }
        },
        required: ["name", "issuer", "startDate", "url"],
        additionalProperties: false
      }
    },
    publications: {
      type: "array",
      items: {
        type: "object",
        properties: {
          name: { type: "string" },
          publisher: { type: "string" },
          releaseDate: { $ref: "#/definitions/iso8601" },
          summary: { type: "string" },
          url: { type: "string", format: "uri" }
        },
        required: ["name", "publisher", "releaseDate", "summary", "url"],
        additionalProperties: false
      }
    },
    skills: {
      type: "array",
      items: {
        type: "object",
        properties: {
          name: { type: "string" },
          level: { type: "string" },
          keywords: {
            type: "array",
            items: { type: "string" }
          }
        },
        required: ["name", "level", "keywords"],
        additionalProperties: false
      }
    },
    languages: {
      type: "array",
      items: {
        type: "object",
        properties: {
          language: { type: "string" },
          fluency: { type: "string" }
        },
        required: ["language", "fluency"],
        additionalProperties: false
      }
    },
    interests: {
      type: "array",
      items: { type: "string" }
    },
    references: {
      type: "array",
      items: {
        type: "object",
        properties: {
          name: { type: "string" },
          reference: { type: "string" }
        },
        required: ["name", "reference"],
        additionalProperties: false
      }
    },
    projects: {
      type: "array",
      items: {
        type: "object",
        properties: {
          name: { type: "string" },
          startDate: { $ref: "#/definitions/iso8601" },
          endDate: { $ref: "#/definitions/iso8601" },
          summary: { type: "string" },
          url: { type: "string", format: "uri" },
          keywords: {
            type: "array",
            items: { type: "string" }
          }
        },
        required: ["name", "startDate", "endDate", "summary", "url", "keywords"],
        additionalProperties: false
      }
    }
  },
  required: [
    "$schema", "basics", "work", "volunteer", "education", "awards", "certificates", "publications", "skills", "languages", "interests", "references", "projects"
  ],
  title: "Resume Schema",
  type: "object"
};
