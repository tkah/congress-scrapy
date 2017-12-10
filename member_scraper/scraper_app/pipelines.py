from sqlalchemy.orm import sessionmaker
from .models import Members, db_connect, create_members_table

class MemberPipeline(object):
    def __init__(self):
        """Init database connection"""
        engine = db_connect()
        create_members_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        member = Members(**item)

        try:
            session.add(member)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item