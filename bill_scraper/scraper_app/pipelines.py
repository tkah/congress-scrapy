from sqlalchemy.orm import sessionmaker
from .models import Bills, db_connect, create_bills_table

class BillPipeline(object):
    def __init__(self):
        """Init database connection"""
        engine = db_connect()
        create_bills_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        bill = Bills(**item)

        try:
            session.add(bill)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item