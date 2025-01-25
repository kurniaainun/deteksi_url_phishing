from flask import Flask, render_template, request
import joblib
import pandas as pd
from feature import generate_data_set
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Konfigurasi database PostgreSQL
app.config.from_object('database.config.Config')
db = SQLAlchemy(app)

# Model database
class PhishingDetection(db.Model):
    __tablename__ = 'phishing_detection'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False, unique=True)
    score = db.Column(db.Numeric(5, 2), nullable=False)
    status = db.Column(db.Text, nullable=False)
    features = db.Column(db.JSON, nullable=False)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    detection_count = db.Column(db.Integer, default=1)

# Load model yang sudah dilatih
model_path = "decision_tree_phishing.pkl"
model = joblib.load(model_path)

# Nama fitur yang sesuai dengan data pelatihan
feature_names = [
    "UsingIP", "LongURL", "ShortURL", "Symbol@", "Redirecting//", "PrefixSuffix-",
    "SubDomains", "HTTPS", "DomainRegLen", "Favicon", "NonStdPort", "HTTPSDomainURL",
    "RequestURL", "AnchorURL", "LinksInScriptTags", "ServerFormHandler", "InfoEmail",
    "AbnormalURL", "WebsiteForwarding", "StatusBarCust", "DisableRightClick",
    "UsingPopupWindow", "IframeRedirection", "AgeofDomain", "DNSRecording",
    "WebsiteTraffic", "PageRank", "GoogleIndex", "LinksPointingToPage", "StatsReport"
]

# Route untuk halaman utama
@app.route("/")
def home():
    return render_template("home.html")

# Route untuk halaman pencarian
@app.route("/search", methods=["GET"])
def search():
    return render_template("search.html")

# Route untuk hasil analisis URL
@app.route("/results", methods=["GET"])
def results():
    url = request.args.get("url")
    if not url:
        return render_template("results.html", error="URL tidak ditemukan. Masukkan URL yang valid.")
    
    try:
        # Ekstraksi fitur dari URL menggunakan fungsi generate_data_set
        features = generate_data_set(url)
        feature_df = pd.DataFrame([features], columns=feature_names)

        # Prediksi menggunakan model yang sudah dilatih
        probabilities = model.predict_proba(feature_df)[0]
        score = round(probabilities[0] * 100, 2)  # Skor keamanan (0-100)
        status = "Phishing" if probabilities[0] > probabilities[1] else "Legitimate"
        
        # Periksa apakah URL sudah ada di database
        existing_record = PhishingDetection.query.filter_by(url=url).first()

        if existing_record:
            # Update data jika URL sudah ada
            existing_record.score = score
            existing_record.status = status
            existing_record.features = features
            existing_record.analysis_date = datetime.utcnow()
            existing_record.detection_count += 1
        else:
            # Tambahkan data baru jika URL belum ada
            new_record = PhishingDetection(
                url=url,
                score=score,
                status=status,
                features=features
            )
            db.session.add(new_record)
        
        db.session.commit()  # Simpan perubahan ke database

        return render_template(
            "results.html",
            url=url,
            prediction=status,
            score=score,
            features=[f"{feature}: {value}" for feature, value in zip(feature_names, features)],
            analysis_date=datetime.utcnow().strftime("%d %B %Y %H:%M:%S")
        )
    except Exception as e:
        return render_template("results.html", error=f"Terjadi kesalahan: {str(e)}")

# Route untuk halaman riwayat
@app.route("/history", methods=["GET"])
def history():
    records = PhishingDetection.query.order_by(PhishingDetection.analysis_date.desc()).all()
    return render_template("history.html", records=records)

# Main entry point
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Membuat tabel jika belum ada
    app.run(debug=True)
