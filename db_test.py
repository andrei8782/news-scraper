from append_db import DatabaseController

db_controller = DatabaseController()
append_successful = db_controller.append_to_db("output/cryptoglobe/tmp_articles.csv")
print(append_successful)