import requests
from bs4 import BeautifulSoup
import pandas as pd

# List of all 25 cadre codes
cadre_codes = [
    "UT", "AP", "AM", "BH", "CG", "GJ", "HY", "HP", "JH", "KN",
    "KL", "MP", "MH", "MN", "NL", "OD", "PB", "RJ", "SK", "TN",
    "TG", "TR", "UP", "UD", "WB"
]

base_url = "https://iascivillist.dopt.gov.in/Home/ViewList/Download"

all_officers = []

for code in cadre_codes:
    print(f"Fetching cadre: {code}")

    # POST data
    payload = {
        "ViewCadreCode": code,
        "btn_submit": "Submit"
    }

    response = requests.post(base_url, data=payload)
    soup = BeautifulSoup(response.text, "html.parser")

    # Each officer is inside a div with class 'IAS_cardCont'
    officers = soup.find_all("div", class_="IAS_cardCont")

    for officer in officers:
        # English and Hindi Names
        name_en = officer.find("h2").get_text(strip=True).replace("Name:", "").strip()
        name_hi_tag = officer.find("h3")
        name_hi = name_hi_tag.get_text(strip=True) if name_hi_tag else ""

        # DOB
        dob_tag = officer.find("p", class_="dob_design")
        dob = dob_tag.get_text(strip=True).replace("DOB:", "").strip() if dob_tag else ""

        # Other fields
        identity_no = allot_year = source = qualification = pay_scale = ""
        cadre_domicile = remarks = current_posting = posting_wef = ""

        # Left/Center/Right divs
        cols = officer.find_all("div", class_="col-md-6")
        if cols:
            center_col = cols[0]
            # Identity, Allotment, Source, Qualification, Pay Scale, Remarks
            for p in center_col.find_all("p"):
                text = p.get_text(strip=True)
                if "Identity No." in text:
                    identity_no = text.replace("Identity No.:", "").strip()
                elif "Allotment Year:" in text:
                    allot_year = text.replace("Allotment Year:", "").strip()
                elif "Source of Recruitment:" in text:
                    source = text.replace("Source of Recruitment:", "").strip()
                elif "Qualification" in text:
                    qualification = text.replace("Qualification(Subject):", "").strip()
                elif "Pay Scale" in text:
                    pay_scale = text.replace("Pay Scale:", "").strip()
                elif "Remarks" in text:
                    remarks = text.replace("Remarks:", "").strip()

        # Right column contains Cadre & Domicile and Posting
        right_col = officer.find("div", class_="col-md-4")
        if right_col:
            cadre_tag = right_col.find("p")
            if cadre_tag:
                cadre_domicile = cadre_tag.get_text(strip=True).replace("Cadre & Domicile:", "").strip()

            posting_li = right_col.find("ul")
            if posting_li:
                current_posting = posting_li.li.get_text(strip=True).split(", Posting W.E.F.:")[0].replace("Posting:-",
                                                                                                           "").strip()
                posting_wef = posting_li.li.get_text(strip=True).split("Posting W.E.F.:")[1].strip()

        officer_data = {
            "Cadre Code": code,
            "Name (English)": name_en,
            "Name (Hindi)": name_hi,
            "DOB": dob,
            "Identity No.": identity_no,
            "Allotment Year": allot_year,
            "Source of Recruitment": source,
            "Qualification": qualification,
            "Pay Scale": pay_scale,
            "Cadre & Domicile": cadre_domicile,
            "Remarks": remarks,
            "Current Posting": current_posting,
            "Posting W.E.F.": posting_wef
        }

        all_officers.append(officer_data)

# Convert to DataFrame and save to Excel
df = pd.DataFrame(all_officers)
df.to_excel("NewIAS_Civil_List_All_Cadres.xlsx", index=False)
print("Data extraction complete! Saved to 'IAS_Civil_List_All_Cadres.xlsx'.")
