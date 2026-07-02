try:
    print("Trying to import pipeline...")
    from app.astra.pipeline import AstraPipeline
    print("AstraPipeline Import SUCCESS")
    from app.enhanced_inference import AstraModelInference
    print("AstraModelInference Import SUCCESS")
    print("Initializing components...")
    model = AstraModelInference()
    pipeline = AstraPipeline(model_service=model)
    print("Pipeline Initialization SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
