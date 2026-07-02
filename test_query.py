import asyncio
from dotenv import load_dotenv
load_dotenv()

from app.astra.pipeline import AstraPipeline

async def test_interaction():
    pipeline = AstraPipeline()
    user_query = "what is ayureveda"
    print(f"\nPatient Query: \"{user_query}\"")
    
    # Get AI Response
    response = await pipeline.process_query(
        user_id="e42d18936177a9ac", 
        message=user_query, 
        history=[]
    )
    print(f"\nAstra Response:\n{response}")

if __name__ == "__main__":
    asyncio.run(test_interaction())
