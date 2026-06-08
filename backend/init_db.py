import os
from sqlalchemy import text
from database import engine

def init_db():
    sql_file = "../mentorat_matching_utilisateurs.sql"
    print(f"Reading SQL file: {sql_file}")
    with open(sql_file, 'r') as file:
        sql_content = file.read()
    
    # SQLAlchemy a besoin de séparer les requêtes ou exécuter le bloc en une fois.
    # Pour PostgreSQL, on peut envoyer tout le script avec connection.execute()
    # si on l'entoure de text().
    
    with engine.connect() as conn:
        with conn.begin(): # Transaction begin
            print("Executing SQL script...")
            # split by ; is sometimes risky but simple scripts usually work.
            # actually psycopg2 handles multiple statements in one execute call well.
            conn.execute(text(sql_content))
            print("SQL script executed successfully! Tables are created.")

if _name_ == "_main_":
    init_db()