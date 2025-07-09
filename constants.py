#Method questions

DOCUMENT_QUESTIONS = {
    "Method": [
        "Pre/Post Employment drug screening/testing",
        "MVR Check",
        "Does the business use H-2A labor or program",
        "Is there a full-time risk/safety manager employed whose job is 50%+ safety related?",
        "What is the maximum height at which employees might work?",
        "Is there a formal return to work program?",
        "Safety program/manual",
        "Safety training held for employees",
        "Safety meetings held for employees",
        "Is fall protection used?",
        "What is the maximum depth at which employees might work?",
        "What percentage of work is over 30 feet?",
        "What percentage of work is below 10 feet?",
        "Group Health Insurance provided",
        "Does the business provide group transportation?",
        "Percentage of workforce subcontracted",
        "Are certificates of insurance obtained?",
        "Type of subcontracted labor",
        "Is there any driving/delivery exposure?",
        "In which states does travel generally happen?"
    ],

    "Foresight": [
        "Does the business have a formal safety program?",
        "Are owners active in daily operations?",
        "Do any of your customers represent more than 25% of your revenue?",
        "Do you expect to have any large (>10%) fluctuations in payroll this coming policy year?",
        "What jobs do you have planned?",
        "Will you be increasing staff by 10% in the next 12 months (outside of seasonality adjustments)?",
        "Will you be decreasing staff by 10% in the next 12 months (outside of seasonality adjustments)?",
        "What is the reason for this fluctuation?",
        "Is any of your workforce paid piece rate or hourly?",
        "Do you have a documented process on how you pay employees?",
        "What is your Employee Count vs W2 Count?",
        "What percentage of your workforce is 1099?",
        "Do you require 1099 contractors to have their own coverage?",
        "Have you used any temp or day labor in the last 12 months?",
        "Do Foremen hire employees at jobsites?",
        "Do you plan to use any temp or day labor in the next 12 months?",
        "Do you subcontract out work?",
        "What work do you subcontract out?",
        "Do you require subcontractors to have a Certificate of Insurance (COI)?",
        "Do you perform reference checks on new employees?",
        "Are pre/post placement physicals required?",
        "Is pre/post-employment drug testing required?",
        "Do you ensure new employees have appropriate certifications for their role?",
        "Is there a formal IIPP / Safety Program in place?",
        "Is there a formal Fall Protection Program in place?",
        "Are all required SDS's available for employees to review?",
        "Do you perform regular safety inspections?",
        "Do you perform regular safety meetings?",
        "Are employees trained on the correct use of equipment, machinery and vehicles?",
        "Do you have a dedicated Safety Manager?",
        "Are they a full time or part time safety manager?",
        "What are their responsibilities?",
        "What are their qualifications?",
        "What is the ratio of general staff vs supervisors with safety compliance responsibilities?",
        "Do you have a documented incident investigation process?",
        "How are findings used to prevent recurrence?",
        "Do you have a documented return to work program in place?",
        "Do you provide safety orientation for new employees?",
        "What topics are covered in safety orientation?",
        "Is the orientation on-the-job, in a dedicated room, or blended?",
        "Do you record your employee safety training?",
        "How do you enforce safety protocols to your employees?",
        "Do you record safety violations?",
        "Have you ever terminated someone for safety violations?",
        "Do you track safety KPIs?",
        "Do you have a safety incentive program for employees?",
        "Do you provide PPE to your employees?",
        "Describe the PPE you provide and the related tasks.",
        "How is the use of PPE enforced?",
        "Do you have a Lock Out Tag Out policy in place?",
        "Describe how you manage this process and ensure the policy is being followed.",
        "Do employees operate heavy machinery (forklifts, excavators, etc.)?",
        "Are operators of heavy machinery trained and certified?",
        "How do you enforce safety protocols to your heavy machine operators?",
        "Do you have drivers employed in your operations?",
        "Do you pull MVRs for all of your drivers?",
        "How frequently are MVRs pulled?",
        "How do you document the handling of MVR violations?",
        "How do you document enforcement of MVR violation handling?",
        "Do employees drive personal vehicles to multiple work locations within a day?",
        "Do 6 or more employees travel in the same vehicle together to work?",
        "Do you collect employee Uninsured/Underinsured Motorist coverage for personal vehicles?",
        "Do you provide employee transportation to work?",
        "What is the highest amount of employees you transport on a daily basis?",
        "What is the average amount of employees you transport on a daily basis?",
        "What type of vehicles are used?",
        "Do you transport employees on unpaved roads?",
        "Do you transport between 6–15 employees in passenger vans?",
        "Do you have a distracted driving program?",
        "Do all vehicles have telematics tracking with GPS in place?",
        "Do all vehicles have front/rear/driver-facing cameras?",
        "Do you engage a third-party contractor to provide employee transportation?",
        "Do you collect Certificates of Liability Insurance from driving contractors?",
        "Do third-party contractors have a distracted driving program?",
        "Do all third-party vehicles have telematics tracking with GPS in place?",
        "Do all third-party vehicles have front/rear/driver-facing cameras?",
        "Do you provide company vehicles?",
        "Do employees take vehicles home daily?",
        "Are front and rear-facing cameras installed in company vehicles?",
        "Is there a telematics device in the vehicles?",
        "Do employees transport company property in personal vehicles?",
        "Are employees paid for transportation time?",
        "Does the insured have a distracted driving program?",
        "How frequently are motor vehicle records pulled?",
        "Are employees required to travel international, interstate, or overnight for work?"
    ]
}

DOC_TYPE_PROMPTS = {
    "safety_manual": [
        "safety manual", "safety policy", "safety program",
        "safety written program", "IIPP", "safety procedures"
        
    ],
    "compliance_report": [
        "compliance report", "audit findings", "violations",
        "corrective actions", "safety metrics"
    ],
    "fall protection": [
        "ladder", "scaffold", "fall protection","sccisors", "aerial lift",
        "fall arrest", "safety harness", "guardrail", "safety net"
    ],
    "MVR Check": [
        "motor vehicle record", "mvr checks", "mvr"
    ],
    "Pre/Post Employment drug screening/testing": [
        "drug testing", "pre employment drug", "post employment drug"
    ]
}

# Configuration
SIMILARITY_THRESHOLD = 0.42
OCR_CONFIG = '--psm 6 -c preserve_interword_spaces=1'