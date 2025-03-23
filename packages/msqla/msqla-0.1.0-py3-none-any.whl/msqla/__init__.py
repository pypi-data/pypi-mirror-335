from sqlalchemy.dialects import registry 
registry.register("msqla", "msqla.dialect.base", "MSQLADialect")