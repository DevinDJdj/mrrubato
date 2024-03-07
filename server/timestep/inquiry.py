from db import get_db

class Inquiry:
    def __init__(self, query, response, context, prompt, userid, confidence, created):
        self.query = query
        self.response = response
        self.context = context
        self.prompt = prompt
        self.userid = userid
        self.confidence = confidence
        self.created = created

    @staticmethod
    def get(user_id):
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2], profile_pic=user[3]
        )
        return user

    @staticmethod
    def create(id_, name, email, profile_pic):
        db = get_db()
        db.execute(
            "INSERT INTO user (id, name, email, profile_pic) "
            "VALUES (?, ?, ?, ?)",
            (id_, name, email, profile_pic),
        )
        db.commit()