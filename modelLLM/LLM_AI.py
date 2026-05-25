from fastapi import APIRouter  , UploadFile , Response , HTTPException , Depends
from agro_back.agro_backend.models.sessions import Session
from agro_back.agro_backend.schemas.LLM import BreifInp_
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types
from agro_back.agro_backend.auth.auth_ import get_current_agrouser


load_dotenv()

# # Configure your API key
client = genai.configure(api_key=os.getenv("GEN_KEY"))
modeling = APIRouter(
    prefix="/model",
    tags =["LLM AND VM MODEL"]
)

@modeling.post("/llm_model")
def LLM(binp_ : BreifInp_ , token: Session = Depends (get_current_agrouser)):
    """
        This is the model for getting the input of breif text from the user
    """
    try:
        animal : str = binp_.animal_type.lower()
        breif : str = binp_.brief_explanation.lower()


        if len(animal) == 0 and len(breif) == 0:
            return {
                "status":"error",
                "reason":"Kindly fill the spot"
            }

        elif len(breif) == 0:
            return {
                "status":"error",
                "reason": "kindly input reason"
            }
        elif len(animal) == 0:
            return {
                "status":"error",
                "reason":"kindly input an animal"
            }
        
        

        mix_inp = f"""
                    You are a veterinary expert. 
                    A {animal} is experiencing the following issue: {breif}

                    Please provide:
                    1. Possible causes of this problem
                    2. Recommended solutions or treatments
                    3. When to seek professional veterinary help

                    Give a clear and practical response.
                """
        # Pass mix_inp to Gemini
        model = genai.GenerativeModel("gemini-3.5-flash")
        response = model.generate_content(mix_inp)


        
        return {
            "status":"successfull",
            "response": response.text
        }
    except Exception as error:
        return {
            "status":"error",
            "reason":str(error)
        }
    

@modeling.post("/vm_model")
async def VM(image_file : UploadFile , token: Session = Depends (get_current_agrouser)):
    """
        This is the model for getting the input of image being uploaded from the user
    """
    # Verify it's an image
    if not image_file.content_type in ("image/png", "image/jpeg", "image/jpg"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # 2. Read the file bytes directly from FastAPI
        image_bytes = await image_file.read()
        
        # 3. Call Gemini 3.5 Flash (The modern free-tier model)
        # response = genai.GenerativeModel(
        #     model="gemini-3.5-flash",
        #     contents=[
        #         "Please read all the text in this image and summarize the content.",
        #         # types.PartType.for(
        #         #     data=image_bytes,
        #         #     mime_type=image_file.content_type
        #         # )
        #     ]
        # )

        response = genai.GenerativeModel("gemini-3.5-flash").generate_content([
            {
                "mime_type": image_file.content_type,  # e.g image/png
                "data": image_bytes
            },
            "Analyse this image and describe what you see. just tell me only the name "
        ])

        return {
            "filename": image_file.filename,
            "analysis": response.text
        }

    except Exception as e:
        return {
            "status":"error",
            "reason":str(e)
        }
    finally:
        await image_file.close()