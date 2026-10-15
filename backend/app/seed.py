from datetime import datetime, timezone
from .database import db
from .config import settings
from .security import hash_password

SAMPLE_COMPANIES = [
 {"name":"Tata Consultancy Services","industry":"IT Services","location":"Pan India","website":"https://www.tcs.com"},
 {"name":"Infosys","industry":"IT Services","location":"Bengaluru, India","website":"https://www.infosys.com"},
 {"name":"Wipro","industry":"IT Services","location":"Pan India","website":"https://www.wipro.com"},
 {"name":"Accenture","industry":"Consulting & Technology","location":"Pan India","website":"https://www.accenture.com"},
 {"name":"Microsoft","industry":"Software","location":"Hyderabad, India","website":"https://www.microsoft.com"},
 {"name":"Google","industry":"Software","location":"Bengaluru, India","website":"https://careers.google.com"},
 {"name":"Amazon","industry":"E-commerce & Cloud","location":"Hyderabad, India","website":"https://www.amazon.jobs"},
 {"name":"Deloitte","industry":"Consulting","location":"Pan India","website":"https://www.deloitte.com"},
 {"name":"Zoho","industry":"Software","location":"Chennai, India","website":"https://www.zoho.com"},
 {"name":"Freshworks","industry":"Software","location":"Chennai, India","website":"https://www.freshworks.com"},
]
SAMPLE_JOBS = [
 {"title":"Junior Python Developer","company":"Infosys","location":"Bengaluru / Hybrid","job_type":"Full-time","description":"Build and maintain APIs, write tests and collaborate with product teams.","skills":["python","fastapi","mongodb","git"],"salary":"₹4–7 LPA"},
 {"title":"Frontend Developer Intern","company":"Zoho","location":"Chennai / Hybrid","job_type":"Internship","description":"Create accessible responsive interfaces and work with REST APIs.","skills":["javascript","react","html","css","git"],"salary":"₹15k–25k/month"},
 {"title":"Graduate Software Engineer","company":"Tata Consultancy Services","location":"Pan India","job_type":"Full-time","description":"Solve engineering problems, develop features and participate in code reviews.","skills":["java","data structures","algorithms","sql"],"salary":"₹3.5–6 LPA"},
 {"title":"Data Analyst Intern","company":"Accenture","location":"Pune / Hybrid","job_type":"Internship","description":"Clean datasets, build dashboards and communicate insights.","skills":["python","pandas","sql","excel"],"salary":"₹20k–30k/month"},
 {"title":"React Developer","company":"Freshworks","location":"Chennai / Remote","job_type":"Full-time","description":"Ship reusable UI components, integrate APIs and improve performance.","skills":["react","javascript","css","rest api"],"salary":"₹6–10 LPA"},
]

async def seed():
    now=datetime.now(timezone.utc)
    admin_email=settings.admin_email.lower().strip()
    await db.users.update_one({"email":admin_email},{"$setOnInsert":{"name":settings.admin_name,"email":admin_email,"password_hash":hash_password(settings.admin_password),"role":"admin","education":"","experience":"","skills":[],"target_role":"","location":"","created_at":now}},upsert=True)
    for c in SAMPLE_COMPANIES:
        await db.companies.update_one({"name":c["name"]},{"$setOnInsert":{**c,"description":"Sample company record. Verify current openings on the official careers site.","created_at":now}},upsert=True)
    for j in SAMPLE_JOBS:
        await db.jobs.update_one({"title":j["title"],"company":j["company"]},{"$setOnInsert":{**j,"active":True,"created_at":now}},upsert=True)
    print(f"Seed complete. Admin login: {admin_email} / {settings.admin_password}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed())
