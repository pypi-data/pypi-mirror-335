import sys
from fortune_teller.mood_fortune import mood_fortune
from fortune_teller.fortune_stories import fortune_story
from fortune_teller.cs_fortune import cs_fortune
from fortune_teller.date_time import rand_date_time
from datetime import datetime

FORTUNE_COOKIE_ART = r"""

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠐⠒⠂⠀⠐⠀⠠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠜⠁⠀⠀⣀⣠⣄⡀⠀⠀⠀⠉⠂⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡌⠀⠀⡐⣡⣿⣿⣿⣿⣷⣦⣄⠀⠀⠀⠑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⠰⢱⢟⠸⢿⣿⣿⣿⣿⣿⣿⣦⡀⠀⠀⠑⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⡎⡿⠀⠀⠀⠿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠈⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠇⠀⢰⢱⡇⠀⠀⠀⠀⠉⠻⣿⣿⣿⣿⣿⣿⣦⠀⠀⠈⠢⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠸⣼⠱⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣷⡄⠀⠀⢣⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⢨⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⡄⠀⠀⢆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⢨⡧⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⣿⡀⠀⠘⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠀⠀⢸⡇⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣿⣿⣿⣧⠀⠀⢣⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡎⠀⠀⣹⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⠀⠀⠸⠀⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠀⠤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⣾⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⡆⠀⠀⠀⠀⠀⣀⣀⣤⢤⣤⣀⣤⣤⣠⣄⣀⡀⠀⠀⠀⠀⠈⠁⠂⠄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⡀⠠⠀⠀⠈⠁⠀⠀⠀⠀⠀⣀⡀⠤⠤⠄⣒⣦⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⡇⠤⠔⢊⣩⣴⡾⠿⠛⠋⠉⠉⠉⠉⠉⠉⠉⠙⠛⠓⠶⣤⣤⣀⠀⠀⠀⠁⠢⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⡀⠔⠉⠀⠀⠀⣀⠠⠤⠐⣒⣊⣭⣥⡶⠶⠶⠚⠛⠉⠁⠘⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣇⣤⡶⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⢿⣖⡤⡀⠀⠀⠈⠢⠀⠀⠀⠀⠀⠀⠀⠀
⠀⡜⠁⠀⢀⡤⣒⣩⣤⠶⠞⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⢾⣗⢄⡀⠀⠀⠐⢀⠀⠀⠀⠀⠀
⢠⠃⠀⢰⠏⢾⡋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣶⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⢘⡧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢷⣍⢢⡀⠀⠈⠢⠀⠀⠀⠀
⠈⡆⠀⠈⠙⡌⢷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⠾⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢨⡗⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢷⣜⣄⠀⠀⠱⡀⠀⠀
⠀⠈⠢⠀⠀⠈⢌⡻⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣮⣦⠀⠀⢱⠀⠀
⠀⠀⠀⠱⡀⠀⠀⠑⢽⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⡀⠀⠀⢃⠀
⠀⠀⠀⠀⠈⠢⡀⠀⠀⠙⠯⣷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣼⠿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣷⡀⠀⠘⡄
⠀⠀⠀⠀⠀⠀⠈⠒⣀⠀⠀⠉⠫⢿⢦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⣸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡇⠀⠀⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⠄⡀⠀⠀⠈⠛⠹⢟⡳⠶⢦⣤⣤⣤⣤⣤⡴⠶⠛⢻⡉⢿⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⠀⠀⢠⠃
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠢⢀⠀⠀⠀⠀⠉⠉⠈⠈⠁⠀⠀⠀⠀⠀⠀⠑⠤⣉⣛⣻⢿⠷⣷⢶⣶⣶⣦⣴⣦⣤⣤⣤⣀⡀⠀⣰⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⠇⠀⠀⡎⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠒⠂⠀⠀⠀⠀⠀⠀⠐⠀⠈⠢⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠋⢽⣻⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣫⠃⠀⠀⡜⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠐⠒⠒⠒⠂⠂⠀⠀⠀⠀⠀⠐⡂⠀⠀⢀⢪⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣾⣿⢟⠝⠁⠀⢀⠜⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠁⠀⢀⢃⣾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣴⣾⣿⣿⢟⡷⠁⠀⠀⡠⠋⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡸⠀⠀⡨⣼⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⣿⣿⡟⡯⠋⠀⠀⢀⠊⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⣷⡏⡀⠀⡀⠀⠀⠀⠀⠀⣀⣀⣤⣴⡶⠟⡛⠉⠀⣿⣿⣿⡟⡻⠋⠀⠀⢀⠔⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⣿⢸⣿⣿⣿⣿⣿⣿⣿⣿⡟⠉⠁⢠⠼⣴⢺⡄⠀⠘⢿⣏⠉⠀⠀⠀⡔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⣿⣆⠉⠿⠿⡿⣿⣿⣿⢿⣇⠀⠀⠸⣷⢈⡿⠀⠀⠀⠀⠿⣷⡀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⠀⠀⠘⢍⠛⠾⠶⠶⠶⠶⠶⡶⢿⣆⠀⠀⠀⠙⠁⠀⣀⣤⣶⠾⠟⠋⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠣⡀⠀⠀⠈⠉⠉⠉⠉⠁⠀⠀⠀⠻⣧⣄⣤⡶⠾⠛⠋⠉⠀⠀⠀⠀⣀⠜⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⠂⠠⠤⠤⠀⠀⠀⠀⠄⠀⠀⠀⠁⠀⠀⠀⠀⠀⣀⠠⠀⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⠂⠀⠀⠀⠀⠒⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""
# cookie art taken from emojicombos website

def print_fortune_in_cookie(fortune_text: str) -> None:
    print(FORTUNE_COOKIE_ART)
    print("\nHere's your fortune:")
    print("               ↓")
    print(f"  {fortune_text}\n")

def main():

    print("Welcome to the ⊹₊⟡⋆Fortune Teller⊹₊⟡⋆")
    print("\nTry your luck today with one of the following fortune functions:\n")
    while True:
        print("\n")
        #print("Welcome to the ⊹₊⟡⋆Fortune Teller⊹₊⟡⋆")
        #print("\nTry your luck today with one of the following fortune functions:\n")
        print("  1. mood_fortune (receive fortunes based on your mood) ૮ ˶ᵔ ᵕ ᵔ˶ ა")
        print("  2. fortune_story (receive personalized story fortunes) (˶ᵔ ᵕ ᵔ˶)")
        print("  3. cs_fortune (receive fortunes based on a computer science topic) ٩(ˊᗜˋ*)و ♡")
        print("  4. Quit ૮(˶╥︿╥)ა")
        print("\n")
        
        choice = input("\nWhich fortune function would you like to use? Enter 1, 2, 3, or 4: ").strip()
        
        if choice == "1":
            handle_mood_fortune()
        elif choice == "2":
            handle_fortune_story()
        elif choice == "3":
            handle_cs_fortune()
        elif choice == "4":
            print("\nGoodbye for now, but remember: luck waits for no one!")
            sys.exit(0)
        else:
            print("\nOops, invalid choice ( • ᴖ • ｡) Please enter 1, 2, 3, or 4.")

def handle_mood_fortune():
    """
    Asks the user to pick a mood, gets a fortune, and puts it with a random date.
    """
    print("\nYou chose 'mood_fortune'. Now, choose your mood: positive, funny, cursed, motivational.")
    mood = input("\nEnter your mood: ").strip()
    
    fortune = mood_fortune(mood)
    
    if fortune.startswith("Oops:"):
        print(fortune)
        return
    

    current_date_str = datetime.today().strftime('%Y-%m-%d')
    combined = rand_date_time(current_date_str, fortune)
    print_fortune_in_cookie(combined)

def handle_fortune_story():
    """
    Asks the user to provide a name, gets a story fortune, and puts it with a random date.
    """
    print("\nYou chose 'fortune_story'.")
    name = input("\nFor whom is this fortune? (enter a name): ").strip()
    
    story = fortune_story(name)
    
    if story.startswith("Oops:"):
        print(story)
        return
    
    
    current_date_str = datetime.today().strftime('%Y-%m-%d')
    combined = rand_date_time(current_date_str, story)

    print_fortune_in_cookie(combined)

def handle_cs_fortune():
    """
    Asks the user to pick a category, gets a CS fortune, and puts it with a random date.
    """
    print("\nYou chose 'cs_fortune'. Now, please pick a category: tech, startup, open source, ai, career.")
    category = input("\nEnter your category: ").strip()
    
    cs_message = cs_fortune(category)
    
    if cs_message.startswith("Oops:"):
        print(cs_message)
        return
    
    current_date_str = datetime.today().strftime('%Y-%m-%d')
    combined = rand_date_time(current_date_str, cs_message)
    print_fortune_in_cookie(combined)

if __name__ == "__main__":
    main()
