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
    def get(numrows=10):
        db = get_db()
        inquiry = db.execute(
            "SELECT * FROM inquiries ORDER BY ROWID ASC LIMIT ?", (numrows,)
        ).fetchone()
        if not inquiry:
            return None

        inquiry = Inquiry(
            query=inquiry[0], response=inquiry[1], context=inquiry[2], prompt=inquiry[3], userid=inquiry[4], confidence=inquiry[5], created=inquiry[6]
        )
        return inquiry

    @staticmethod
    def create(query, response, context, prompt, userid, confidence):
        db = get_db()
        db.execute(
            "INSERT INTO inquiries (query, response, context, prompt, userid, confidence) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (query, response, context, prompt, userid, confidence),
        )
        db.commit()