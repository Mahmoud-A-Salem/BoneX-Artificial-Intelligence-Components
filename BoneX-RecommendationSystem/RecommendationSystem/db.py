from sqlalchemy import create_engine

def get_connection():
    connection_string = (
        "mssql+pyodbc://mahmoudd:123456@localhost/BoneXRecommendationSystem?driver=ODBC+Driver+17+for+SQL+Server"
    )
    engine = create_engine(connection_string)
    return engine
