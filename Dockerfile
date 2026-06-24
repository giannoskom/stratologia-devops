# 1. Παίρνουμε ένα έτοιμο, πανάλαφρο Linux που έχει ήδη Python 3.11
FROM python:3.11-slim

# 2. Ορίζουμε τον φάκελο εργασίας μέσα στο container
WORKDIR /app

# 3. Αντιγράφουμε ΠΡΩΤΑ μόνο το αρχείο με τις βιβλιοθήκες
COPY requirements.txt .

# 4. Εγκαθιστούμε τις βιβλιοθήκες της Python inside the container
RUN pip install --no-cache-dir -r requirements.txt

# 5. Αντιγράφουμε όλο τον υπόλοιπο κώδικα (app.py και φάκελο templates/)
COPY . .

# 6. Δηλώνουμε ότι το container θα ακούει στην πόρτα 5000
EXPOSE 5000

# 7. Η εντολή που θα τρέχει αυτόματα όταν πατάμε το "ON"
CMD ["python", "app.py"]