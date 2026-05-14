from sqlalchemy import text
from app.database import engine

def fix_enum_values():
    """Add missing values to roleenum type"""
    with engine.connect() as conn:
        # Check current enum values
        result = conn.execute(text("""
            SELECT unnest(enum_range(NULL::roleenum)) as value
        """))
        current_values = [row[0] for row in result]
        
        print(f"Current enum values: {current_values}")
        
        # Values that should be added
        needed_values = ['AGENT_STOCK', 'AGENT_COMMERCIAL', 'DIRECTEUR_COMMERCIAL']
        
        for value in needed_values:
            if value not in current_values:
                print(f"Adding {value} to enum...")
                try:
                    conn.execute(text(f"ALTER TYPE roleenum ADD VALUE '{value}'"))
                    conn.commit()
                    print(f"✅ Added {value}")
                except Exception as e:
                    print(f"Could not add {value}: {e}")
        
        # Verify final values
        result = conn.execute(text("SELECT unnest(enum_range(NULL::roleenum))"))
        print(f"Final enum values: {[row[0] for row in result]}")
