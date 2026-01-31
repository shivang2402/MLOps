# main.py
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field
from typing import List
from predict import predict_data, get_encoders

app = FastAPI(
    title="Calorie Burn Estimator API",
    description="Estimate calories burned based on activity and body weight",
    version="1.0.0"
)

# Load encoders at startup
activity_encoder, activity_decoder = get_encoders()

class CalorieInput(BaseModel):
    activity: str = Field(..., description="Type of exercise/activity")
    weight_kg: float = Field(..., ge=30, le=200, description="Body weight in kg")

class RecommendInput(BaseModel):
    target_calories: float = Field(..., ge=50, le=2000, description="Target calories to burn")
    weight_kg: float = Field(..., ge=30, le=200, description="Body weight in kg")
    top_n: int = Field(default=5, ge=1, le=20, description="Number of recommendations")

class CalorieResponse(BaseModel):
    calories_burned: float
    activity: str
    weight_kg: float

class RecommendResponse(BaseModel):
    target_calories: float
    weight_kg: float
    recommendations: list

@app.get("/", status_code=status.HTTP_200_OK)
async def health_ping():
    return {"status": "healthy"}

@app.get("/activities")
async def get_activities():
    """Get list of all supported activities."""
    return {"activities": list(activity_encoder.keys())}

@app.post("/predict", response_model=CalorieResponse)
async def predict_calories(input_data: CalorieInput):
    try:
        # Check if activity exists
        if input_data.activity not in activity_encoder:
            raise HTTPException(
                status_code=400, 
                detail=f"Activity '{input_data.activity}' not found. Use /activities to see available options."
            )
        
        features = [[
            activity_encoder[input_data.activity],
            input_data.weight_kg
        ]]
        
        prediction = predict_data(features)
        
        return CalorieResponse(
            calories_burned=round(float(prediction[0]), 1),
            activity=input_data.activity,
            weight_kg=input_data.weight_kg
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend", response_model=RecommendResponse)
async def recommend_activities(input_data: RecommendInput):
    """Recommend activities to burn target calories."""
    try:
        # Predict calories for all activities
        all_predictions = []
        for activity, encoded in activity_encoder.items():
            features = [[encoded, input_data.weight_kg]]
            predicted_cal = float(predict_data(features)[0])
            diff = abs(predicted_cal - input_data.target_calories)
            all_predictions.append({
                "activity": activity,
                "calories_burned": round(predicted_cal, 1),
                "difference": round(diff, 1)
            })
        
        # Sort by closest to target
        all_predictions.sort(key=lambda x: x["difference"])
        top_recommendations = all_predictions[:input_data.top_n]
        
        # Remove difference from output
        for rec in top_recommendations:
            del rec["difference"]
        
        return RecommendResponse(
            target_calories=input_data.target_calories,
            weight_kg=input_data.weight_kg,
            recommendations=top_recommendations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))