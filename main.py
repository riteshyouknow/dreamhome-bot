# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from openai import OpenAI
# from dotenv import load_dotenv
# import os

# load_dotenv()
# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# sessions = {}

# PROPERTIES = [
#     {"id": 1, "name": "2BHK Andheri West", "price": "85 Lac",
#      "bhk": 2, "location": "Andheri", "status": "Ready to Move"},
#     {"id": 2, "name": "3BHK Powai Lake View", "price": "1.4 Cr",
#      "bhk": 3, "location": "Powai", "status": "Under Construction"},
#     {"id": 3, "name": "2BHK Thane West", "price": "65 Lac",
#      "bhk": 2, "location": "Thane", "status": "Ready to Move"},
#     {"id": 4, "name": "1BHK Navi Mumbai", "price": "42 Lac",
#      "bhk": 1, "location": "Navi Mumbai", "status": "Ready to Move"},
# ]

# SYSTEM_PROMPT = f"""
# Tu "DreamHome Properties" ka AI assistant hai.
# Hinglish mein baat kar (Hindi + English mix).
# Friendly aur professional reh.

# Tera kaam step by step:
# 1. Greet karo warmly
# 2. Budget poochho
# 3. Location preference poochho
# 4. BHK requirement poochho
# 5. Properties suggest karo neeche list se
# 6. Site visit ke liye naam aur phone number lo
# 7. Jab naam aur phone mil jaye toh exactly yeh format mein likho:
#    LEAD_CAPTURED|naam|phone|budget|location
   
#    budget example: "80lac" ya "1.4Cr"
#    location example: "Andheri" ya "Thane"

# Available Properties:
# {PROPERTIES}

# Rules:
# - Ek baar mein ek hi sawaal poochho
# - Properties sirf tab suggest karo jab budget+location pata ho
# - Lead capture (naam+phone) zaroor karo
# - LEAD_CAPTURED line ke baad normal confirmation message bhi likho
# """

# class ChatRequest(BaseModel):
#     session_id: str
#     message: str

# @app.post("/chat")
# async def chat(req: ChatRequest):
#     if req.session_id not in sessions:
#         sessions[req.session_id] = []

#     history = sessions[req.session_id]
#     history.append({"role": "user", "content": req.message})

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": SYSTEM_PROMPT},
#             *history
#         ],
#         max_tokens=500,
#         temperature=0.7
#     )

#     reply = response.choices[0].message.content
#     history.append({"role": "assistant", "content": reply})

#     if len(history) > 20:
#         sessions[req.session_id] = history[-20:]

#     # Auto lead capture detect karo
#     lead_detected = False
#     if "LEAD_CAPTURED|" in reply:
#         try:
#             parts = reply.split("LEAD_CAPTURED|")[1].split("|")
#             name = parts[0].strip()
#             phone = parts[1].strip()
#             requirement = parts[2].strip() if len(parts) > 2 else "Not specified"

#             # n8n ko call karo automatically
#             import httpx
#             async with httpx.AsyncClient() as http_client:
#                 await http_client.post(
#                     "http://localhost:5678/webhook/lead-capture",
#                     json={
#                         "name": name,
#                         "phone": phone,
#                         "requirement": requirement,
#                         "session_id": req.session_id
#                     }
#                 )
#             lead_detected = True

#             # LEAD_CAPTURED line reply se remove karo
#             reply = reply.replace(
#                 f"LEAD_CAPTURED|{name}|{phone}|{requirement}", ""
#             ).strip()

#         except Exception as e:
#             print(f"Lead capture error: {e}")

#     return {
#         "reply": reply,
#         "session_id": req.session_id,
#         "lead_captured": lead_detected
#     }

# @app.get("/properties")
# async def get_properties():
#     return {"properties": PROPERTIES}

# @app.get("/")
# async def root():
#     return {"status": "DreamHome Bot is running!"}

# class LeadData(BaseModel):
#     session_id: str
#     name: str
#     phone: str
#     requirement: str

# @app.post("/save-lead")
# async def save_lead(lead: LeadData):
#     import httpx
#     async with httpx.AsyncClient() as http_client:
#         await http_client.post(
#             "http://localhost:5678/webhook-test/lead-capture",
#             json={
#                 "name": lead.name,
#                 "phone": lead.phone,
#                 "requirement": lead.requirement,
#                 "session_id": lead.session_id
#             }
#         )
#     return {"status": "success", "message": "Lead saved"}












# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from openai import OpenAI
# from dotenv import load_dotenv
# import os
# import re
# import httpx

# load_dotenv()
# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # Store conversation history for each session
# sessions = {}

# # Property database
# PROPERTIES = [
#     {"id": 1, "name": "2BHK Andheri West", "price": "85 Lac",
#      "bhk": 2, "location": "Andheri", "status": "Ready to Move"},
#     {"id": 2, "name": "3BHK Powai Lake View", "price": "1.4 Cr",
#      "bhk": 3, "location": "Powai", "status": "Under Construction"},
#     {"id": 3, "name": "2BHK Thane West", "price": "65 Lac",
#      "bhk": 2, "location": "Thane", "status": "Ready to Move"},
#     {"id": 4, "name": "1BHK Navi Mumbai", "price": "42 Lac",
#      "bhk": 1, "location": "Navi Mumbai", "status": "Ready to Move"},
# ]

# SYSTEM_PROMPT = f"""
# You are a professional real estate assistant for "DreamHome Properties".

# IMPORTANT - Language Rule:
# - The user's preferred language will be mentioned at the start as "LANGUAGE: Hindi" or "LANGUAGE: English" or "LANGUAGE: Hinglish"
# - Hindi: Respond in pure Hindi (Devanagari script)
# - English: Respond in pure English
# - Hinglish: Respond in Hindi + English mix (Roman script)
# - Always follow the selected language throughout the conversation

# Your job - follow these steps in order:
# 1. Greet the user warmly in their selected language
# 2. Ask for their budget
# 3. Ask for their preferred location
# 4. Ask for BHK requirement
# 5. Suggest matching properties from the list below
# 6. Ask for their name and phone number for site visit booking
# 7. Once you have name and phone, output EXACTLY this on a separate line:
#    LEAD_CAPTURED|name|phone|budget|location

#    budget format example: "80lac" or "1.4Cr"
#    location format example: "Andheri" or "Thane"
# 8. After LEAD_CAPTURED, show this confirmation message:

# "✅ Appointment Booked!

# Name: [naam]
# Phone: [phone]
# Date: Our team will call you within 24 hours to confirm your site visit.

# Thank you for choosing DreamHome Properties! 🏠"


# Available Properties:
# {PROPERTIES}

# Strict Rules:
# - Ask only ONE question at a time
# - Suggest properties ONLY after you know budget AND location
# - LEAD_CAPTURED line must be on its own separate line, nothing else on that line
# - After the LEAD_CAPTURED line, write a warm confirmation message on a new line
# - Never write "Yeh raha aapka lead capture" or any similar phrase
# - Never include extra text in the LEAD_CAPTURED line itself
# """

# class ChatRequest(BaseModel):
#     session_id: str
#     message: str

# class LeadData(BaseModel):
#     session_id: str
#     name: str
#     phone: str
#     budget: str
#     location: str

# @app.post("/chat")
# async def chat(req: ChatRequest):
#     # Initialize session if new user
#     if req.session_id not in sessions:
#         sessions[req.session_id] = []

#     history = sessions[req.session_id]
#     history.append({"role": "user", "content": req.message})

#     # Call OpenAI API
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": SYSTEM_PROMPT},
#             *history
#         ],
#         max_tokens=500,
#         temperature=0.7
#     )

#     reply = response.choices[0].message.content
#     history.append({"role": "assistant", "content": reply})

#     # Keep only last 20 messages to save memory
#     if len(history) > 20:
#         sessions[req.session_id] = history[-20:]

#     # Check if lead was captured
#     lead_detected = False
#     if "LEAD_CAPTURED|" in reply:
#         try:
#             # Extract lead data from the LEAD_CAPTURED line
#             lead_line = [line for line in reply.split("\n") if "LEAD_CAPTURED|" in line][0]
#             parts = lead_line.split("LEAD_CAPTURED|")[1].split("|")

#             name = parts[0].strip()
#             phone = parts[1].strip()
#             budget = parts[2].strip() if len(parts) > 2 else "Not specified"
#             location = parts[3].strip() if len(parts) > 3 else "Not specified"

#             # Send lead data to n8n webhook
#             async with httpx.AsyncClient() as http_client:
#                 await http_client.post(
#                     "http://localhost:5678/webhook/lead-capture",
#                     json={
#                         "name": name,
#                         "phone": phone,
#                         "budget": budget,
#                         "location": location,
#                         "session_id": req.session_id
#                     }
#                 )
#             lead_detected = True

#             # Remove LEAD_CAPTURED line from reply shown to user
#             reply = re.sub(r'LEAD_CAPTURED\|[^\n]*\n?', '', reply).strip()

#         except Exception as e:
#             print(f"Lead capture error: {e}")

#     return {
#         "reply": reply,
#         "session_id": req.session_id,
#         "lead_captured": lead_detected
#     }

# @app.get("/properties")
# async def get_properties():
#     return {"properties": PROPERTIES}

# @app.get("/")
# async def root():
#     return {"status": "DreamHome Bot is running!"}




from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import re
import httpx

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Store conversation history for each session
sessions = {}
# Store language preference for each session
session_languages = {}

# Property database
PROPERTIES = [
    {"id": 1, "name": "2BHK Andheri West", "price": "85 Lac",
     "bhk": 2, "location": "Andheri", "status": "Ready to Move"},
    {"id": 2, "name": "3BHK Powai Lake View", "price": "1.4 Cr",
     "bhk": 3, "location": "Powai", "status": "Under Construction"},
    {"id": 3, "name": "2BHK Thane West", "price": "65 Lac",
     "bhk": 2, "location": "Thane", "status": "Ready to Move"},
    {"id": 4, "name": "1BHK Navi Mumbai", "price": "42 Lac",
     "bhk": 1, "location": "Navi Mumbai", "status": "Ready to Move"},
]

def get_system_prompt(language: str) -> str:
    return f"""
You are a professional real estate assistant for "DreamHome Properties".
The user has selected "{language}" as their preferred language.

Language rules:
- If language is "Hindi": respond ONLY in Hindi using Devanagari script
- If language is "English": respond ONLY in English
- If language is "Hinglish": respond in Hindi + English mix using Roman script
- NEVER mention or show the language name in your responses
- NEVER write "LANGUAGE: English" or similar in your replies
- Just follow the language silently throughout the conversation

Your job - follow these steps in order:
1. Greet the user warmly and ask how you can assist them in finding their dream home.
  
2. After user responds, then ask for their budget
3. Ask for their preferred location
4. Ask for BHK requirement
5. Suggest matching properties from the list below
6. Ask for their name and phone number for site visit booking
7. Once you have name and phone, output EXACTLY this on a separate line:
   LEAD_CAPTURED|name|phone|budget|location

   budget format example: "80lac" or "1.4Cr"
   location format example: "Andheri" or "Thane"

8. After LEAD_CAPTURED line, show this confirmation on a new line:
   Appointment Booked!
   Name: [name]
   Phone: [phone]
   Our team will call you within 24 hours to confirm your site visit.
   Thank you for choosing DreamHome Properties!

Available Properties:
{PROPERTIES}

Strict Rules:
- Ask only ONE question at a time
- Suggest properties ONLY after you know budget AND location
- LEAD_CAPTURED line must be on its own separate line, nothing else on that line
- Never use markdown formatting like **bold** or *italic*
- Never write "LANGUAGE:" anywhere in responses
- Never say "Yeh raha aapka lead capture" or similar
"""

class ChatRequest(BaseModel):
    session_id: str
    message: str

class LeadData(BaseModel):
    session_id: str
    name: str
    phone: str
    budget: str
    location: str

@app.post("/chat")
async def chat(req: ChatRequest):
    # Initialize session if new user
    if req.session_id not in sessions:
        sessions[req.session_id] = []

    history = sessions[req.session_id]

    # Detect and save language from first message
    if "LANGUAGE:" in req.message:
        if "Hindi" in req.message:
            session_languages[req.session_id] = "Hindi"
        elif "Hinglish" in req.message:
            session_languages[req.session_id] = "Hinglish"
        else:
            session_languages[req.session_id] = "English"
        # Clean the message — remove LANGUAGE prefix before saving
        clean_message = re.sub(r'LANGUAGE:.*?\.', '', req.message).strip()
        history.append({"role": "user", "content": clean_message})
    else:
        history.append({"role": "user", "content": req.message})

    # Get language for this session
    language = session_languages.get(req.session_id, "English")

    # Call OpenAI API with language-specific system prompt
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": get_system_prompt(language)},
            *history
        ],
        max_tokens=500,
        temperature=0.7
    )

    reply = response.choices[0].message.content

    # Remove any accidental LANGUAGE: mentions from reply
    reply = re.sub(r'LANGUAGE:\s*\w+', '', reply).strip()

    history.append({"role": "assistant", "content": reply})

    # Keep only last 20 messages to save memory
    if len(history) > 20:
        sessions[req.session_id] = history[-20:]

    # Check if lead was captured
    lead_detected = False
    if "LEAD_CAPTURED|" in reply:
        try:
            # Extract lead data from the LEAD_CAPTURED line
            lead_line = [line for line in reply.split("\n") if "LEAD_CAPTURED|" in line][0]
            parts = lead_line.split("LEAD_CAPTURED|")[1].split("|")

            name = parts[0].strip()
            phone = parts[1].strip()
            budget = parts[2].strip() if len(parts) > 2 else "Not specified"
            location = parts[3].strip() if len(parts) > 3 else "Not specified"

            # Send lead data to n8n webhook
            async with httpx.AsyncClient() as http_client:
                await http_client.post(
                    "http://localhost:5678/webhook/lead-capture",
                    json={
                        "name": name,
                        "phone": phone,
                        "budget": budget,
                        "location": location,
                        "session_id": req.session_id
                    }
                )
            lead_detected = True

            # Remove LEAD_CAPTURED line from reply shown to user
            reply = re.sub(r'LEAD_CAPTURED\|[^\n]*\n?', '', reply).strip()

        except Exception as e:
            print(f"Lead capture error: {e}")

    return {
        "reply": reply,
        "session_id": req.session_id,
        "lead_captured": lead_detected
    }

@app.get("/properties")
async def get_properties():
    return {"properties": PROPERTIES}

@app.get("/")
async def root():
    return {"status": "DreamHome Bot is running!"}