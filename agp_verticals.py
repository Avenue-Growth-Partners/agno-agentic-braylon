from enum import Enum


class VerticalCategory(str, Enum):
    """
    Enum representing vertical business categories.
    """

    AEROSPACE = ("Aerospace", "Aerospace. ")
    AGTECH = ("AgTech", "Agriculture & Forestry. Key Words: Agriculture, forestry, farming, logging, NAICS Sectors: Agriculture, Forestry, Fishing & Hunting, GICS Sectors (quick & dirty): Materials (15)")
    ART_ENTERTAIN = ("Art_Entertain", "Arts, Entertainment & Recreation. Key Words: Art, museum, theme park, country club, theater, entertainment center, community park, sports venue, recreation, gaming, NAICS Sectors: Arts, Entertainment & Recreation, GICS Sectors (quick & dirty): Consumer Discretionary (25)")
    AUTO = ("Auto", "Automotive. Key Words: Car, truck, vehicle, dealership, automotive, NAICS Sectors: Wholesale Trade / Retail Trade, GICS Sectors (quick & dirty): Consumer Discretionary (25), Consumer Staples (30)")
    AVIATION___DRONES = ("Aviation & Drones", "Aviation & Drones. ")
    BIOTECH_PHARMA = ("Biotech/Pharma", "Biotech/Pharma. ")
    CANNABIS = ("Cannabis", "Cannabis. ")
    CARE_ECONOMY = ("Care Economy", "Care Economy. ")
    CHEMICALS = ("Chemicals", "Chemicals. ")
    CLIMATE = ("Climate", "Climate. ")
    CONSTRUCTION = ("Construction", "Construction. ")
    CPG = ("CPG", "CPG. ")
    CRE = ("CRE", "Commercial Real Estate. ")
    CREATOR_ECONOMY = ("Creator Economy", "Creator Economy. ")
    ECOMMERCE = ("Ecommerce", "Ecommerce. ")
    EDTECH = ("EdTech", "Education. Key Words: K-12, preschool, elementary school, middle school, high school, college, university, higher education, student, teacher, NAICS Sectors: Educational Services, GICS Sectors (quick & dirty): Consumer Discretionary (25")
    HARDWARE = ("HARDWARE", "Electronics and Equipment. ")
    ENERGY = ("Energy", "Energy. ")
    ESG = ("ESG", "ESG. ")
    FIELD_SVCS = ("Field Svcs", "Field Services. Key Words: Field service, HVAC, plumbing, heating, air conditioning, ventilation, pests, home repair, gardening, NAICS Sectors: Professional, Scientific and Technical Services, GICS Sectors (quick & dirty): Information Technology (45)")
    FINANCIAL_SVCS = ("Financial Svcs", "Financial Services. Key Words: Financial institution, credit union, community bank, hedge fund, private equity, venture capital, asset management, insurance, P&C, property & casualty, NAICS Sectors: Finance & Insurance, GICS Sectors (quick & dirty): Financials (40)")
    FITNESS = ("Fitness", "Fitness. ")
    FOOD_SVC = ("Food svc", "Restaurants & Food Service. Key Words: Restaurant, fine dining, quick-service restaurant, fast food, food service, NAICS Sectors: Accommodation and Food Service, GICS Sectors (quick & dirty): Consumer Discretionary (25)")
    GENERAL_CONTRACTOR = ("General Contractor", "General Contractor. ")
    GROCERY = ("Grocery", "Grocery. Key Words: Grocery, food market, NAICS Sectors: Wholesale Trade / Retail Trade, GICS Sectors (quick & dirty): Consumer Discretionary (25), Consumer Staples (30)")
    HEALTHCARE = ("Healthcare", "Health Care. Key Words: Dental, dentist, nursing, acute care facility, hospice, primary care, healthcare, outpatient, emergency room, clinic, life sciences, NAICS Sectors: Health Care and Social Assistance, GICS Sectors (quick & dirty): Health Care (35)")
    HOME_SERVICES = ("Home Services", "Home Services. ")
    HORIZONTAL = ("Horizontal", "Horizontal. ")
    HOSPITALITY = ("Hospitality", "Hospitality. Key Words: Hospitality, hotel, motel, bed and breakfast, vacation, vacation property, airline, airport, cruise, travel agent, NAICS Sectors: Accommodation and Food Service, GICS Sectors (quick & dirty): Consumer Discretionary (25)")
    INDUSTRIAL = ("Industrial", "Industrial. ")
    INSURANCE = ("Insurance", "Insurance. ")
    IT_MSPS = ("IT MSPs", "IT MSPs. Key Words: IT MSP, helpdesk, IT support, NAICS Sectors: Professional, Scientific and Technical Services, GICS Sectors (quick & dirty): Information Technology (45)")
    LEGAL = ("Legal", "Legal. Key Words: Legal, law firm, lawyer, practice management, NAICS Sectors: Professional, Scientific and Technical Services, GICS Sectors (quick & dirty): Information Technology (45)")
    MANUFACTURING = ("Manufacturing", "Manufacturing. Key Words: Manufacturing, manufacturer, discreet manufacturing, process manufacturing, job shop, NAICS Sectors: Manufacturing, GICS Sectors (quick & dirty): Industrials (20)")
    MEDIA = ("Media", "Media. Key Words: Media, publisher, publishing, news paper, news network, broadcast, advertising, NAICS Sectors: Information, GICS Sectors (quick & dirty): Communications Services (50), Information Technology (45)")
    N_A__BROAD_HORIZ_ = ("N/A: Broad horiz.", "Broad Horizontal. Key Words: Horizontal, generalist. The software usually covers 2,3 or more verticals.")
    NATURAL_RESOURCES = ("Natural Resources", "Natural Resources. Key Words: Natural resources, Oil & gas, upstream, downstream, minerals, mining, NAICS Sectors: Mining, Quarrying and Oil & Gas Extraction, GICS Sectors (quick & dirty): Energy (10), Materials (15)")
    NONPROFIT = ("Nonprofit", "Nonprofit. Key Words: Nonprofit, charity, foundation, endowment, donor")
    OTHER = ("Other", "Other. NAICS Sectors: Management of Companies and Enterprises, Other Services (except Public Administration), GICS Sectors (quick & dirty): Other, Information Technology (45)")
    PET_TECH = ("Pet Tech", "Pet Tech. ")
    PROF__SVCS = ("Prof. Svcs", "Professional Services. Key Words: Professional services, accounting, architecture & engineering, consulting, advisory, NAICS Sectors: Professional, Scientific and Technical Services, GICS Sectors (quick & dirty): Information Technology (45)")
    PROPTECH = ("PropTech", "PropTech. ")
    PUBLIC_SECTOR = ("Public Sector", "Government / Public Sector. Key Words: Public sector, government, armed services, municipality, city government, state government, local government, NAICS Sectors: Public Administration, GICS Sectors (quick & dirty): N/A")
    REAL_ESTATE = ("Real Estate", "Real Estate. Key Words: Real estate, residential real estate, commercial real estate, property management, construction, NAICS Sectors: Real Estate and Rental and Leasing, GICS Sectors (quick & dirty): Real Estate (60)")
    RETAIL = ("Retail", "Specialty Retail & Wholesale. Key Words: Spa and salon, barber shop, fitness studio, gym, yoga, athletic center, NAICS Sectors: Retail & Wholesale Trade, GICS Sectors (quick & dirty): Consumer Discretionary (25), Consumer Staples (30)")
    SALON___SPA = ("Salon & Spa", "Salon & Spa. ")
    SPORTS = ("Sports", "Sports. ")
    TELECOM = ("Telecom", "Telecommunications. Key Words: Telecommunications, telco, fiber, wireline, wireless, spectrum, NAICS Sectors: Information, GICS Sectors (quick & dirty): Communications Services (50), Information Technology (45)")
    TRAFFIC = ("Traffic", "Traffic. ")
    TRANSPORT___LOGISTICS = ("Transport & logistics", "Transportation & Logistics. Key Words: Transportation, logistics, freight, distribution, fleet, trucking, shipping, NAICS Sectors: Transportation & Warehousing, GICS Sectors (quick & dirty): Industrials (20 - specifically 2030)")
    TRANSPORTATION = ("Transportation", "Transportation. ")
    UTILITIES = ("Utilities", "Utilities. Key Words: Utility, grid management, power, water & power, energy, NAICS Sectors: Utilities, GICS Sectors (quick & dirty): Utilities (55)")
    WASTE_MGMT = ("Waste Mgmt", "Waste Management. Key Words: Waste management, NAICS Sectors: Administrative and Support and Waste Management and Remediation Services, GICS Sectors (quick & dirty): Industrials (20)")

    def __new__(cls, value, details):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.details = details
        return obj

    @classmethod
    def instructions(cls) -> str:
        """Compile detailed instructions from each enum type."""
        lines = []
        for member in cls:
            lines.append(f"{member.value}: {member.details}")
        return "\n".join(lines)