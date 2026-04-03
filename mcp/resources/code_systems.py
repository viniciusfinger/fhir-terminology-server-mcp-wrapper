import json

from fastmcp.resources import resource

CODE_SYSTEMS = [
    {
        "name": "SNOMED CT",
        "url": "http://snomed.info/sct",
        "oid": "2.16.840.1.113883.6.96",
        "domain": "Clinical / Multi-purpose",
        "description": (
            "Systematized Nomenclature of Medicine - Clinical Terms. "
            "Comprehensive multilingual clinical terminology covering "
            "diagnoses, procedures, body structures, substances, "
            "organisms, and more. The most expressive clinical "
            "terminology, with hierarchical relationships (is-a) "
            "and post-coordination."
        ),
        "example_codes": [
            {"code": "73211009", "display": "Diabetes mellitus"},
            {"code": "386661006", "display": "Fever"},
            {"code": "25064002", "display": "Headache"},
        ],
        "version_format": "http://snomed.info/sct/[sctid]/version/[YYYYMMDD]",
    },
    {
        "name": "LOINC",
        "url": "http://loinc.org",
        "oid": "2.16.840.1.113883.6.1",
        "domain": "Laboratory / Observations",
        "description": (
            "Logical Observation Identifiers Names and Codes. "
            "International standard for identifying laboratory and "
            "clinical observations, surveys/assessments, vital signs, "
            "and document types."
        ),
        "example_codes": [
            {"code": "2339-0", "display": "Glucose [Mass/volume] in Blood"},
            {"code": "718-7", "display": "Hemoglobin [Mass/volume] in Blood"},
            {"code": "8480-6", "display": "Systolic blood pressure"},
        ],
    },
    {
        "name": "ICD-10-CM",
        "url": "http://hl7.org/fhir/sid/icd-10-cm",
        "oid": "2.16.840.1.113883.6.90",
        "domain": "Diagnoses / Morbidity",
        "description": (
            "International Classification of Diseases, 10th Revision, "
            "Clinical Modification. Used in the United States for "
            "diagnosis coding in clinical and billing contexts."
        ),
        "example_codes": [
            {"code": "E11.9", "display": "Type 2 diabetes mellitus without complications"},
            {"code": "I10", "display": "Essential (primary) hypertension"},
            {"code": "J06.9", "display": "Acute upper respiratory infection, unspecified"},
        ],
    },
    {
        "name": "ICD-10",
        "url": "http://hl7.org/fhir/sid/icd-10",
        "oid": "2.16.840.1.113883.6.3",
        "domain": "Diagnoses / Mortality / Morbidity",
        "description": (
            "International Classification of Diseases, 10th Revision "
            "(WHO edition). Used internationally for mortality and "
            "morbidity statistics."
        ),
        "example_codes": [
            {"code": "E11", "display": "Type 2 diabetes mellitus"},
            {"code": "I10", "display": "Essential (primary) hypertension"},
        ],
    },
    {
        "name": "ICD-11",
        "url": "http://id.who.int/icd/release/11/mms",
        "domain": "Diagnoses / Mortality / Morbidity",
        "description": (
            "International Classification of Diseases, 11th Revision (WHO). "
            "Successor to ICD-10 with enhanced digital integration, "
            "post-coordination, and extension codes."
        ),
        "example_codes": [
            {"code": "5A11", "display": "Type 2 diabetes mellitus"},
            {"code": "BA00", "display": "Essential hypertension"},
        ],
    },
    {
        "name": "RxNorm",
        "url": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "oid": "2.16.840.1.113883.6.88",
        "domain": "Medications",
        "description": (
            "Normalized names and codes for clinical drugs and drug "
            "delivery devices in the United States. Provides links "
            "between drug vocabularies (NDC, SNOMED CT, etc.) and "
            "supports clinical decision support."
        ),
        "example_codes": [
            {"code": "860975", "display": "Metformin hydrochloride 500 MG Oral Tablet"},
            {"code": "197361", "display": "Amlodipine 5 MG Oral Tablet"},
        ],
    },
    {
        "name": "CPT",
        "url": "http://www.ama-assn.org/go/cpt",
        "oid": "2.16.840.1.113883.6.12",
        "domain": "Procedures / Billing",
        "description": (
            "Current Procedural Terminology. Published by AMA, widely "
            "used in the US for reporting medical, surgical, and "
            "diagnostic procedures and services for billing."
        ),
        "example_codes": [
            {"code": "99213", "display": "Office/outpatient visit, established patient, low complexity"},
            {"code": "36415", "display": "Collection of venous blood by venipuncture"},
        ],
    },
    {
        "name": "HCPCS Level II",
        "url": "https://www.cms.gov/Medicare/Coding/HCPCSReleaseCodeSets",
        "oid": "2.16.840.1.113883.6.285",
        "domain": "Supplies / Services / Billing",
        "description": (
            "Healthcare Common Procedure Coding System Level II. "
            "Codes for products, supplies, and services not covered "
            "by CPT, including durable medical equipment, prosthetics, "
            "orthotics, and ambulance services."
        ),
        "example_codes": [
            {"code": "J0135", "display": "Injection, adalimumab, 20 mg"},
        ],
    },
    {
        "name": "NDC",
        "url": "http://hl7.org/fhir/sid/ndc",
        "oid": "2.16.840.1.113883.6.69",
        "domain": "Medications / Drug Products",
        "description": (
            "National Drug Code. FDA-maintained unique product "
            "identifier for drugs in the United States, identifying "
            "the labeler, product, and trade package size."
        ),
        "example_codes": [
            {"code": "0069-2587-10", "display": "Lipitor 10mg tablet"},
        ],
    },
    {
        "name": "CVX",
        "url": "http://hl7.org/fhir/sid/cvx",
        "oid": "2.16.840.1.113883.12.292",
        "domain": "Immunizations",
        "description": (
            "Vaccine Administered codes maintained by the CDC. "
            "Used in immunization records to identify the vaccine "
            "product administered."
        ),
        "example_codes": [
            {"code": "208", "display": "SARS-COV-2 (COVID-19) vaccine, mRNA"},
            {"code": "08", "display": "Hepatitis B vaccine"},
            {"code": "03", "display": "MMR vaccine"},
        ],
    },
    {
        "name": "UCUM",
        "url": "http://unitsofmeasure.org",
        "oid": "2.16.840.1.113883.6.8",
        "domain": "Units of Measure",
        "description": (
            "Unified Code for Units of Measure. Provides a code "
            "system for all units of measures used in international "
            "science, engineering, and business. Required by FHIR "
            "for Quantity data types."
        ),
        "example_codes": [
            {"code": "mg/dL", "display": "milligram per deciliter"},
            {"code": "mm[Hg]", "display": "millimeter of mercury"},
            {"code": "kg", "display": "kilogram"},
            {"code": "/min", "display": "per minute"},
        ],
    },
    {
        "name": "ATC",
        "url": "http://www.whocc.no/atc",
        "oid": "2.16.840.1.113883.6.73",
        "domain": "Medications / Drug Classification",
        "description": (
            "Anatomical Therapeutic Chemical classification. "
            "WHO-maintained hierarchical classification of drugs "
            "by therapeutic, pharmacological, and chemical properties."
        ),
        "example_codes": [
            {"code": "A10BA02", "display": "Metformin"},
            {"code": "C09AA01", "display": "Captopril"},
        ],
    },
    {
        "name": "NUCC Health Care Provider Taxonomy",
        "url": "http://nucc.org/provider-taxonomy",
        "oid": "2.16.840.1.113883.6.101",
        "domain": "Provider Specialty / Classification",
        "description": (
            "National Uniform Claim Committee provider taxonomy. "
            "Classifies healthcare providers by type, classification, "
            "and area of specialization."
        ),
        "example_codes": [
            {"code": "207R00000X", "display": "Internal Medicine Physician"},
            {"code": "261QM1300X", "display": "Multi-Specialty Clinic"},
        ],
    },
    {
        "name": "HL7 v3 Code Systems (ActCode, RoleCode, etc.)",
        "url": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "domain": "FHIR Infrastructure",
        "description": (
            "HL7 v3 vocabulary code systems used throughout FHIR "
            "for encounter types, roles, act reasons, and more. "
            "Multiple code systems exist under http://terminology.hl7.org/CodeSystem/."
        ),
        "related_systems": [
            {"name": "ActCode", "url": "http://terminology.hl7.org/CodeSystem/v3-ActCode"},
            {"name": "RoleCode", "url": "http://terminology.hl7.org/CodeSystem/v3-RoleCode"},
            {"name": "ObservationInterpretation", "url": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation"},
            {"name": "MaritalStatus", "url": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus"},
            {"name": "NullFlavor", "url": "http://terminology.hl7.org/CodeSystem/v3-NullFlavor"},
        ],
    },
    {
        "name": "HL7 FHIR-defined Code Systems",
        "url": "http://hl7.org/fhir/",
        "domain": "FHIR Infrastructure",
        "description": (
            "Code systems defined by the FHIR specification itself "
            "for resource status fields, administrative data, and "
            "other structural elements."
        ),
        "related_systems": [
            {"name": "AdministrativeGender", "url": "http://hl7.org/fhir/administrative-gender"},
            {"name": "ConditionClinicalStatus", "url": "http://terminology.hl7.org/CodeSystem/condition-clinical"},
            {"name": "ConditionVerificationStatus", "url": "http://terminology.hl7.org/CodeSystem/condition-ver-status"},
            {"name": "AllergyIntoleranceClinicalStatus", "url": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical"},
            {"name": "MedicationRequestStatus", "url": "http://hl7.org/fhir/CodeSystem/medicationrequest-status"},
            {"name": "ObservationStatus", "url": "http://hl7.org/fhir/observation-status"},
            {"name": "DiagnosticReportStatus", "url": "http://hl7.org/fhir/diagnostic-report-status"},
        ],
    },
    {
        "name": "SNOMED CT (Body Structures)",
        "url": "http://snomed.info/sct",
        "domain": "Anatomy",
        "description": (
            "SNOMED CT body structure hierarchy. Use SNOMED CT "
            "with an ECL filter or ValueSet for body structures "
            "(hierarchy: << 123037004 |Body structure|)."
        ),
        "usage_hint": "Filter with ECL: << 123037004 |Body structure|",
        "example_codes": [
            {"code": "80891009", "display": "Heart structure"},
            {"code": "39607008", "display": "Lung structure"},
            {"code": "64033007", "display": "Kidney structure"},
        ],
    },
    {
        "name": "ISO 3166-1 (Country Codes)",
        "url": "urn:iso:std:iso:3166",
        "domain": "Geography / Administrative",
        "description": (
            "Country codes defined by ISO 3166-1. Used in FHIR "
            "for patient addresses, jurisdiction, and locale."
        ),
        "example_codes": [
            {"code": "BR", "display": "Brazil"},
            {"code": "US", "display": "United States of America"},
        ],
    },
    {
        "name": "BCP 47 (Language Tags)",
        "url": "urn:ietf:bcp:47",
        "domain": "Language / Locale",
        "description": (
            "IETF language tags. Used in FHIR for communication "
            "language preferences and resource translations."
        ),
        "example_codes": [
            {"code": "pt-BR", "display": "Portuguese (Brazil)"},
            {"code": "en-US", "display": "English (United States)"},
            {"code": "es", "display": "Spanish"},
        ],
    },
]


@resource(
    uri="fhir://code-systems",
    name="FHIR Common Code Systems",
    description=(
        "Catalog of widely-used FHIR code systems with their canonical "
        "URLs, OIDs, domain, descriptions, and example codes. Use this "
        "resource to discover the correct system URI before calling "
        "tools like lookup_code, validate_code, or expand_valueset."
    ),
    mime_type="application/json",
)
def get_code_systems() -> str:
    """Return the full catalog of common FHIR code systems."""
    return json.dumps(CODE_SYSTEMS, indent=2)


DOMAIN_INDEX = {}
for cs in CODE_SYSTEMS:
    domain = cs["domain"]
    for part in domain.split(" / "):
        key = part.strip().lower()
        DOMAIN_INDEX.setdefault(key, []).append(
            {"name": cs["name"], "url": cs["url"]}
        )


@resource(
    uri="fhir://code-systems/by-domain/{domain}",
    name="Code Systems by Domain",
    description=(
        "Look up code systems filtered by clinical domain. "
        "Accepted domains include: clinical, laboratory, observations, "
        "diagnoses, medications, procedures, billing, immunizations, "
        "anatomy, units of measure, fhir infrastructure, and others. "
        "Returns matching code systems with their canonical URLs."
    ),
    mime_type="application/json",
)
def get_code_systems_by_domain(domain: str) -> str:
    """Return code systems that belong to the given clinical domain."""
    key = domain.strip().lower()
    matches = []
    for cs in CODE_SYSTEMS:
        cs_domain = cs["domain"].lower()
        if key in cs_domain or any(key in part.strip() for part in cs_domain.split("/")):
            matches.append(cs)

    if not matches:
        available = sorted(DOMAIN_INDEX.keys())
        return json.dumps(
            {
                "error": f"No code systems found for domain '{domain}'",
                "available_domains": available,
            },
            indent=2,
        )

    return json.dumps(matches, indent=2)
