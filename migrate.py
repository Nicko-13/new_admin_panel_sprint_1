from sqlite_to_postgres.data_migration import DataMigration

if __name__ == '__main__':
    migration = DataMigration()
    migration.migrate()
