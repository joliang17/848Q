import time
import re

from guesser import Guesser

training_data = [
  {"start": 1789, "stop": 1797, "name": "George Washington"},
  {"start": 1797, "stop": 1801, "name": "John Adams"},
  {"start": 1801, "stop": 1809, "name": "Thomas Jefferson"},
  {"start": 1809, "stop": 1817, "name": "James Madison"},
  {"start": 1817, "stop": 1825, "name": "James Monroe"},
  {"start": 1825, "stop": 1829, "name": "John Quincy Adams"},
  {"start": 1829, "stop": 1837, "name": "Andrew Jackson"},
  {"start": 1837, "stop": 1841, "name": "Martin Van Buren"},
  {"start": 1841, "stop": 1841, "name": "William Henry Harrison"},
  {"start": 1841, "stop": 1845, "name": "John Tyler"},
  {"start": 1845, "stop": 1849, "name": "James K. Polk"},
  {"start": 1849, "stop": 1850, "name": "Zachary Taylor"},
  {"start": 1850, "stop": 1853, "name": "Millard Fillmore"},
  {"start": 1853, "stop": 1857, "name": "Franklin Pierce"},
  {"start": 1857, "stop": 1861, "name": "James Buchanan"},
  {"start": 1861, "stop": 1865, "name": "Abraham Lincoln"},
  {"start": 1865, "stop": 1869, "name": "Andrew Johnson"},
  {"start": 1869, "stop": 1877, "name": "Ulysses S. Grant"},
  {"start": 1877, "stop": 1881, "name": "Rutherford Birchard Hayes"},
  {"start": 1881, "stop": 1881, "name": "James A. Garfield"},
  {"start": 1881, "stop": 1885, "name": "Chester A. Arthur"},
  {"start": 1885, "stop": 1889, "name": "Grover Cleveland"},
  {"start": 1889, "stop": 1893, "name": "Benjamin Harrison"},
  {"start": 1893, "stop": 1897, "name": "Grover Cleveland"},
  {"start": 1897, "stop": 1901, "name": "William McKinley"},
  {"start": 1901, "stop": 1905, "name": "Theodore Roosevelt"},
  {"start": 1905, "stop": 1909, "name": "Theodore Roosevelt"},
  {"start": 1909, "stop": 1913, "name": "William H. Taft"},
  {"start": 1913, "stop": 1921, "name": "Woodrow Wilson"},
  {"start": 1921, "stop": 1923, "name": "Warren G. Harding"},
  {"start": 1923, "stop": 1929, "name": "Calvin Coolidge"},
  {"start": 1929, "stop": 1933, "name": "Herbert Hoover"},
  {"start": 1933, "stop": 1945, "name": "Franklin D. Roosevelt"},
  {"start": 1945, "stop": 1953, "name": "Harry S. Truman"},
  {"start": 1953, "stop": 1961, "name": "Dwight D. Eisenhower"},
  {"start": 1961, "stop": 1963, "name": "John F. Kennedy"},
  {"start": 1963, "stop": 1969, "name": "Lyndon B. Johnson"},
  {"start": 1969, "stop": 1974, "name": "Richard M. Nixon"},
  {"start": 1974, "stop": 1977, "name": "Gerald R. Ford"},
  {"start": 1977, "stop": 1981, "name": "Jimmy Carter"},
  {"start": 1981, "stop": 1989, "name": "Ronald Reagan"},
  {"start": 1989, "stop": 1993, "name": "George Bush"},
  {"start": 1993, "stop": 2001, "name": "Bill Clinton"},
  {"start": 2001, "stop": 2009, "name": "George W. Bush"},
  {"start": 2009, "stop": 2017, "name": "Barack Obama"},
  {"start": 2017, "stop": 2021, "name": "Donald J. Trump"},
  {"start": 2021, "stop": 2025, "name": "Joseph R. Biden"}
]

class PresidentGuesser(Guesser):
    def train(self, training_data):
        self._lookup = {}
        
        for row in training_data:
            self._lookup[row["name"]] = (time.strptime(str(row["start"]), "%Y"), time.strptime(str(row["stop"]), "%Y"))
            
    def __call__(self, question, n_guesses=1):
        """
        
        """
        
        # Update this code so that we can have a different president than Joe
        # Biden
        # print(question)

        question_time = re.findall(r'\w{3} \w{3} \d{2} \d{2}:\d{2}:\d{2} \d{4}', question)
        if len(question_time) == 0:
            return []
        
        q_time = time.strptime(question_time[0], "%a %b %d %H:%M:%S %Y")

        hb = 12

        if q_time.tm_year == 1789:
            if (q_time.tm_mon < 4) or (q_time.tm_mon == 4 and q_time.tm_mday < 30) or (q_time.tm_mon == 4 and q_time.tm_mday == 30 and q_time.tm_hour < hb):
                return []
            else:
                guesses = [{"guess": 'George Washington'}]
                return guesses[:n_guesses]
            
        if q_time.tm_year == 1849 and q_time.tm_mon == 3:
            if (q_time.tm_mday == 4 and q_time.tm_hour >= hb) or (q_time.tm_mday == 5 and q_time.tm_hour < hb):
                guesses = [{"guess": 'David Rice Atchison'}]
                return guesses[:n_guesses]
            
        if q_time.tm_year == 1881:
            if (q_time.tm_mon < 3) or (q_time.tm_mon == 3 and q_time.tm_mday < 4) or (q_time.tm_mon == 3 and q_time.tm_mday == 4 and q_time.tm_hour < hb):
                guesses = [{"guess": 'Rutherford Birchard Hayes'}]
                return guesses[:n_guesses]
            elif (q_time.tm_mon < 9) or (q_time.tm_mon == 9 and q_time.tm_mday < 19) or (q_time.tm_mon == 9 and q_time.tm_mday == 19 and q_time.tm_hour < hb):
                guesses = [{"guess": 'James A. Garfield'}]
                return guesses[:n_guesses]
            else:
                guesses = [{"guess": 'Chester A. Arthur'}]
                return guesses[:n_guesses]
        
        if q_time.tm_year == 1841:
            if (q_time.tm_mon < 3) or (q_time.tm_mon == 3 and q_time.tm_mday < 4) or (q_time.tm_mon == 3 and q_time.tm_mday == 4 and q_time.tm_hour < hb):
                guesses = [{"guess": 'Martin Van Bure'}]
                return guesses[:n_guesses]
            elif (q_time.tm_mon < 4) or (q_time.tm_mon == 4 and q_time.tm_mday < 6) or (q_time.tm_mon == 4 and q_time.tm_mday == 6 and q_time.tm_hour < hb):
                guesses = [{"guess": 'William Henry Harrison'}]
                return guesses[:n_guesses]
            else:
                guesses = [{"guess": 'John Tyler'}]
                return guesses[:n_guesses]
            
        if q_time.tm_year == 1923:
            if (q_time.tm_mon < 8) or (q_time.tm_mon == 8 and q_time.tm_mday < 2) or (q_time.tm_mon == 8 and q_time.tm_mday == 2 and q_time.tm_hour < hb):
                guesses = [{"guess": 'Warren G. Harding'}]
                return guesses[:n_guesses]
            else:
                guesses = [{"guess": 'Calvin Coolidge'}]
                return guesses[:n_guesses]
        
        if q_time.tm_year == 1945:
            if (q_time.tm_mon < 4) or (q_time.tm_mon == 4 and q_time.tm_mday < 12) or (q_time.tm_mon == 4 and q_time.tm_mday == 12 and q_time.tm_hour < hb):
                guesses = [{"guess": 'Franklin D. Roosevelt'}]
                return guesses[:n_guesses]
            else:
                guesses = [{"guess": 'Harry S. Truman'}]
                return guesses[:n_guesses]
            
        if q_time.tm_year <= 1933:
            if (q_time.tm_mon == 3 and q_time.tm_mday < 4) or (q_time.tm_mon == 3 and q_time.tm_mday == 4 and q_time.tm_hour < hb):
                q_year = q_time.tm_year - 1
            else:
                q_year = q_time.tm_year

        elif q_time.tm_year <= 2025:
            if (q_time.tm_mon == 1 and q_time.tm_mday < 20) or (q_time.tm_mon == 1 and q_time.tm_mday == 20 and q_time.tm_hour < hb):
                q_year = q_time.tm_year - 1
            else:
                q_year = q_time.tm_year
        
        else:
            return []

        candidates = []
        for name, period in self._lookup.items():
            if q_year >= period[0].tm_year and q_year < period[1].tm_year: 
                candidates.append(name)

        # print(candidates)
        guesses = []
        for ii in candidates:
            guesses.append({"guess": ii})

        return guesses[:n_guesses]
        
if __name__ == "__main__":
    pg = PresidentGuesser()

    pg.train(training_data)
    
    for date in ["Who was president on Wed Jan 25 06:20:00 2023?", 
                    "Who was president on Sat May 23 02:00:00 1982?",
                    "Who was president on Sun Mar 04 02:00:00 1849?",
                    "Who was president on Sun Mar 04 16:00:00 1849?",
                    "Who was president on Sun Mar 05 02:00:00 1849?",
                    "Who was president on Sun Mar 05 14:00:00 1849?",
                    "Who was president on Tue Jan 17 11:00:00 2021?",
                    "Who was president on Tue Jan 20 11:00:00 2021?",
                    "Who was president on Tue Jan 21 12:00:00 2025?",
                    ]:
        print(date, pg(date)[0]["guess"])

