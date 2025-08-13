import { Template } from '../types';

export const sampleTemplates: Template[] = [
  {
    form_type: "PGH Form No. P-610005",
    form_title: "NURSES' ADMITTING NOTES",
    length: 1575,
    width: 2080,
    use_coordinates: true,
    regions: [
      {
        name: "Name",
        type: "text",
        coordinates: [143, 295, 686, 332]
      },
      {
        name: "Ward",
        type: "text", 
        coordinates: [768, 301, 853, 332]
      },
      {
        name: "Bed",
        type: "text",
        coordinates: [907, 298, 987, 332]
      },
      {
        name: "Date",
        type: "text",
        coordinates: [1053, 297, 1154, 328]
      },
      {
        name: "Case No",
        type: "text",
        coordinates: [1271, 301, 1502, 332]
      },
      {
        name: "Age",
        type: "text",
        coordinates: [125, 358, 220, 392]
      },
      {
        name: "Sex",
        type: "text",
        coordinates: [263, 367, 357, 394]
      },
      {
        name: "Philhealth Member = Yes",
        type: "encirclement",
        coordinates: [379, 409, 448, 472]
      },
      {
        name: "Philhealth Member = No", 
        type: "encirclement",
        coordinates: [458, 411, 522, 471]
      },
      {
        name: "Mental Status = Calm",
        type: "encirclement",
        coordinates: [303, 826, 402, 861]
      },
      {
        name: "Mental Status = Anxious",
        type: "encirclement", 
        coordinates: [403, 825, 535, 863]
      }
    ]
  },
  {
    form_type: "PGH Form No. P-310010",
    form_title: "CLINICAL ABSTRACT - PAGE 1",
    length: 1570,
    width: 2070,
    use_coordinates: true,
    regions: [
      {
        name: "Data Received",
        type: "text",
        coordinates: [1187, 140, 1476, 218]
      },
      {
        name: "Name of Hospital / Ambulatory Clinic",
        type: "text",
        coordinates: [87, 481, 885, 642]
      },
      {
        name: "Case No",
        type: "text",
        coordinates: [1192, 427, 1482, 482]
      },
      {
        name: "Patient Name: Last Name",
        type: "text",
        coordinates: [366, 838, 898, 935]
      },
      {
        name: "Sex = Male",
        type: "checkbox",
        coordinates: [1200, 854, 1262, 895]
      },
      {
        name: "Sex = Female",
        type: "checkbox",
        coordinates: [1199, 894, 1261, 927]
      }
    ]
  },
  {
    form_type: "PGH Form",
    form_title: "ADMITTING ORDERS",
    length: 1480,
    width: 2180,
    use_coordinates: true,
    regions: [
      {
        name: "Date",
        type: "text",
        coordinates: [295, 455, 1423, 526]
      },
      {
        name: "Name",
        type: "text",
        coordinates: [296, 530, 1009, 601]
      },
      {
        name: "Age/Sex",
        type: "text",
        coordinates: [1149, 531, 1423, 601]
      },
      {
        name: "Diagnosis",
        type: "text",
        coordinates: [308, 609, 1228, 680]
      },
      {
        name: "Diagnostics: CBC with pc and dc",
        type: "checkbox",
        coordinates: [128, 986, 226, 1019]
      },
      {
        name: "Diagnostics: Blood typing",
        type: "checkbox",
        coordinates: [689, 984, 780, 1018]
      }
    ]
  }
];