
class FamilyMember(Base):
    """Family profiles linked to a primary patient account"""
    __tablename__ = "family_members"
    
    id = Column(Integer, primary_key=True)
    member_id = Column(String(100), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    primary_patient_id = Column(String(100), ForeignKey("patient_profiles.patient_id"), nullable=False)
    
    name = Column(String(200), nullable=False)
    relation = Column(String(50), nullable=False) # Father, Mother, Spouse, Child, Other
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    medical_conditions = Column(Text, nullable=True) # JSON
    allergies = Column(Text, nullable=True) # JSON
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship to allow Primary Patient to see their family
    # Note: We need to ensure PatientProfile has the backref or we define it here if possible. 
    # For simplicity in this existing codebase, we rely on the FK.
