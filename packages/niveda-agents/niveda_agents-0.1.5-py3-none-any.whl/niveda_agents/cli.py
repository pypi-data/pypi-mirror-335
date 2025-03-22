import click
from niveda_agents.db.postgres import PostgresDB
from niveda_agents.db.mongo import MongoDB
from niveda_agents.utils.logger import logger


@click.group()
def cli():
    """Niveda Agents Command Line Tool"""
    pass


# ---------------------- PostgreSQL CLI ----------------------
@click.command()
@click.option('--dbname', prompt="Database Name", default=None, help="PostgreSQL Database Name")
@click.option('--user', prompt="Username", default=None, help="PostgreSQL Username")
@click.option('--password', prompt="Password", hide_input=True, help="PostgreSQL Password")
@click.option('--host', prompt="Host", default="localhost", help="PostgreSQL Host")
@click.option('--port', prompt="Port", default="5432", help="PostgreSQL Port")
def connect_postgres(dbname, user, password, host, port):
    """Connect to PostgreSQL"""
    db = PostgresDB(dbname=dbname, user=user,
                    password=password, host=host, port=port)
    logger.info("✅ Connected to PostgreSQL via CLI")
    db.close_connection()


# ---------------------- MongoDB CLI ----------------------
@click.command()
@click.option('--mongo_uri', prompt="MongoDB URI", default="mongodb://localhost:27017", help="MongoDB Connection URI")
@click.option('--db_name', prompt="Database Name", default=None, help="MongoDB Database Name")
def connect_mongo(mongo_uri, db_name):
    """Connect to MongoDB"""
    mongo = MongoDB(mongo_uri=mongo_uri, db_name=db_name)
    logger.info("✅ Connected to MongoDB via CLI")
    mongo.close_connection()


# ---------------------- AI & API CLI ----------------------
@click.command()
def run_ai():
    """Run AI Models (Groq, Azure OpenAI, Hugging Face)"""
    logger.info("🚀 AI Models Running... (Feature Coming Soon)")


@click.command()
def start_api():
    """Start the FastAPI Server"""
    logger.info("🌍 FastAPI Server Starting... (Feature Coming Soon)")


# ---------------------- Register Commands ----------------------
cli.add_command(connect_postgres, name="db_connect_postgres")
cli.add_command(connect_mongo, name="db_connect_mongo")
cli.add_command(run_ai, name="ai_run")
cli.add_command(start_api, name="api_start")


if __name__ == "__main__":
    cli()
