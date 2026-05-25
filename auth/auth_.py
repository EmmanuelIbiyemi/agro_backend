from fastapi import APIRouter , Depends , status , HTTPException 
from fastapi.security import OAuth2PasswordBearer
import bcrypt
from agro_back.agro_backend.schemas.auth_schemy import RegisterRequest , LoginRequest
from agro_back.agro_backend.models.auth_model import Agro_Acc
from sqlalchemy import select , insert 
from sqlalchemy.orm import Session
from agro_backend.models.sessions import get_db
import uuid
from datetime import timedelta , datetime
from jose import JWTError , jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 10

auth_router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_agrouser(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        farm_id: str = payload.get("sub")

        if farm_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired"
        )
    
    stmt = select(Agro_Acc).where(Agro_Acc.farmer_id == farm_id)
    user = db.execute(stmt).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user



def generate_user_id():
    return "agro" + str(uuid.uuid4()).replace("-", "").upper()[:6]


@auth_router.post("/register")
def register(inp_ : RegisterRequest , db: Session = Depends(get_db)):
    try:

        # Check if the email already exists in the database
        existing_user = select(Agro_Acc.farmer_id).where(Agro_Acc.farm_email == inp_.farm_email)
        check_user  = db.execute(existing_user).scalar_one_or_none()

        if check_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        
        hashed_password = bcrypt.hashpw(inp_.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


        # Create a new ecouser instance and save it to the database
        new_user = insert(Agro_Acc).values(
            {
                "farmer_id" : generate_user_id(),
                "farm_name" : inp_.farm_name,
                "farm_email":inp_.farm_email,
                "farm_livestocks" : inp_.farm_livestocks,
                "hashed_password": str(hashed_password)
            }
        )
        db.execute(new_user)
        db.commit()
        return {
            "message": "Registration successful", 
            "status": "success"
        }
    except Exception as e:
        return {
            "message": "Registration failed", 
            "status": "error", 
            "error": str(e)
        }

@auth_router.post("/login")
def login(inp_ : LoginRequest ,db : Session = Depends(get_db)):
    try:
        # == For the AgroTech signin
        loginstmt_ = select(Agro_Acc).where(Agro_Acc.farm_email == inp_.farm_email)
        execute = db.execute(loginstmt_)
        result = execute.scalar_one_or_none()


            
        if result == None :
            return {
                "status":"error",
                "message":"Such Agro Account don't exist"
            }, 404
        
        

        if result != None:
            verify = bcrypt.checkpw(inp_.farm_password.encode('utf-8'), result.hashed_password.encode('utf-8'))


            if result and verify:
                access_token = create_access_token(data={"sub": str(result.farmer_id)})
                
                return {
                    "status":"successfull",
                    "message": "AgroFarmer login successful",
                    "farm_name": result.farm_name,
                    "farn_livestock": result.farm_livestocks,
                    "farm_id":result.farmer_id,
                    "token":str(access_token)
                }, 200
            elif result and not verify :
                return {"error": "Invalid password", "role": "EcoDash"}, 401
            
            elif not result:
                return {"error": "User not found", "role": "EcoDash"}, 404

    except Exception as e:
        return {
                    "message": "Login failed", 
                    "status": "error", 
                    "error": str(e)
                }
    
