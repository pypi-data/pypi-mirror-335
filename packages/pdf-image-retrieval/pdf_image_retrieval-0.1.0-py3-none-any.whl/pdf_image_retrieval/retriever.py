import sqlite3

class ImageRetriever:
    def __init__(self, db_path="images.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY,
                image_url TEXT,
                keywords TEXT
            )
        """)
        self.conn.commit()

    def add_image(self, image_url, keywords):
        keywords_str = ",".join(keywords)
        self.cursor.execute("INSERT INTO images (image_url, keywords) VALUES (?, ?)", (image_url, keywords_str))
        self.conn.commit()

    def search_images(self, query):
        self.cursor.execute("SELECT image_url FROM images WHERE keywords LIKE ?", ('%' + query + '%',))
        return [row[0] for row in self.cursor.fetchall()]

if __name__ == "__main__":
    retriever = ImageRetriever()
    retriever.add_image("https://your-s3-bucket/image1.png", ["finance", "report"])
    result = retriever.search_images("finance")
    print("Matching Images:", result)
