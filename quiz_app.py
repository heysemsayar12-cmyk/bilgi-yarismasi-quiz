from flask import Flask, request, redirect, url_for, render_template_string, session
import time
import uuid
import random
import os

app = Flask(__name__)
app.secret_key = "degistir_bunu_cok_gizli_bir_sey_yap"  # istersen değiştir

# --- Admin bilgileri (bunları kendine göre değiştir) ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "sifre123"

# --- Soru Kütüphanesi (genel kültür, 4 seçenekli) ---
# difficulty: "kolay", "orta", "zor", "cok_zor"

QUESTION_BANK = [
    # KOLAY (%30)
    {
        "id": 1,
        "text": "Türkiye'nin başkenti neresidir?",
        "options": ["İstanbul", "Ankara", "İzmir", "Bursa"],
        "correct_index": 1,
        "difficulty": "kolay"
    },
    {
        "id": 2,
        "text": "Su'nun kimyasal formülü nedir?",
        "options": ["H2O", "CO2", "O2", "NaCl"],
        "correct_index": 0,
        "difficulty": "kolay"
    },
    {
        "id": 3,
        "text": "Osmanlı İmparatorluğu’nun kurucusu kimdir?",
        "options": ["Fatih Sultan Mehmet", "Kanuni Sultan Süleyman", "Yavuz Sultan Selim", "Osman Bey"],
        "correct_index": 3,
        "difficulty": "kolay"
    },
    {
        "id": 4,
        "text": "Aşağıdakilerden hangisi bir gezegendir?",
        "options": ["Mars", "Ay", "Güneş", "Sirius"],
        "correct_index": 0,
        "difficulty": "kolay"
    },
    {
        "id": 5,
        "text": "İnsan vücudunda hangi organ kanı pompalar?",
        "options": ["Böbrek", "Akciğer", "Kalp", "Karaciğer"],
        "correct_index": 2,
        "difficulty": "kolay"
    },
    {
        "id": 6,
        "text": "Türkiye'nin para birimi nedir?",
        "options": ["Euro", "Dolar", "Lira", "Sterlin"],
        "correct_index": 2,
        "difficulty": "kolay"
    },
    {
        "id": 7,
        "text": "Haftanın ilk günü hangisidir? (Türkiye’de resmi olarak)",
        "options": ["Pazartesi", "Pazar", "Cumartesi", "Cuma"],
        "correct_index": 0,
        "difficulty": "kolay"
    },
    {
        "id": 8,
        "text": "İstanbul'u ikiye bölen boğazın adı nedir?",
        "options": ["Çanakkale Boğazı", "İstanbul Boğazı", "Cebelitarık Boğazı", "Bosphorus Kanalı"],
        "correct_index": 1,
        "difficulty": "kolay"
    },

    # ORTA (%30)
    {
        "id": 101,
        "text": "Türkiye'nin en uzun nehri hangisidir?",
        "options": ["Fırat", "Dicle", "Kızılırmak", "Yeşilırmak"],
        "correct_index": 2,
        "difficulty": "orta"
    },
    {
        "id": 102,
        "text": "İkinci Dünya Savaşı hangi yıllar arasında gerçekleşmiştir?",
        "options": ["1939-1945", "1914-1918", "1923-1930", "1950-1953"],
        "correct_index": 0,
        "difficulty": "orta"
    },
    {
        "id": 103,
        "text": "Aşağıdaki bilim insanlarından hangisi görelilik teorisi ile tanınır?",
        "options": ["Isaac Newton", "Albert Einstein", "Nikola Tesla", "Marie Curie"],
        "correct_index": 1,
        "difficulty": "orta"
    },
    {
        "id": 104,
        "text": "Dünyanın en büyük okyanusu hangisidir?",
        "options": ["Atlantik Okyanusu", "Hint Okyanusu", "Pasifik Okyanusu", "Arktik Okyanusu"],
        "correct_index": 2,
        "difficulty": "orta"
    },
    {
        "id": 105,
        "text": "Bir yıl içinde kaç ay 31 gündür?",
        "options": ["4", "5", "6", "7"],
        "correct_index": 3,
        "difficulty": "orta"
    },
    {
        "id": 106,
        "text": "Hangisi bir asal sayıdır?",
        "options": ["21", "29", "39", "51"],
        "correct_index": 1,
        "difficulty": "orta"
    },
    {
        "id": 107,
        "text": "Türkiye'nin yüzölçümü en büyük ili hangisidir?",
        "options": ["Konya", "Ankara", "Sivas", "Erzurum"],
        "correct_index": 0,
        "difficulty": "orta"
    },
    {
        "id": 108,
        "text": "Hangisi bir programlama dili değildir?",
        "options": ["Python", "Java", "HTML", "C#"],
        "correct_index": 2,
        "difficulty": "orta"
    },

    # ZOR (%30)
    {
        "id": 201,
        "text": "Kuantum fiziğinde Heisenberg belirsizlik ilkesi hangi iki nicelik arasındaki ilişkiyi tanımlar?",
        "options": ["Enerji ve kütle", "Konum ve momentum", "Hız ve ivme", "Sıcaklık ve basınç"],
        "correct_index": 1,
        "difficulty": "zor"
    },
    {
        "id": 202,
        "text": "Osmanlı'da Tanzimat Fermanı hangi padişah döneminde ilan edilmiştir?",
        "options": ["II. Mahmud", "Abdülmecid", "Abdülaziz", "II. Abdülhamid"],
        "correct_index": 1,
        "difficulty": "zor"
    },
    {
        "id": 203,
        "text": "Aşağıdaki ülkelerden hangisi Avrupa Birliği üyesi değildir?",
        "options": ["Polonya", "İsveç", "Norveç", "Portekiz"],
        "correct_index": 2,
        "difficulty": "zor"
    },
    {
        "id": 204,
        "text": "Hangisi bir Nobel Edebiyat Ödülü sahibi Türk yazardır?",
        "options": ["Yaşar Kemal", "Orhan Pamuk", "Nazım Hikmet", "Ahmet Hamdi Tanpınar"],
        "correct_index": 1,
        "difficulty": "zor"
    },
    {
        "id": 205,
        "text": "Dünya'nın çekirdeğinde baskın olarak bulunan metal hangisidir?",
        "options": ["Bakır", "Alüminyum", "Demir", "Çinko"],
        "correct_index": 2,
        "difficulty": "zor"
    },
    {
        "id": 206,
        "text": "Hangisi bir yığın (stack) veri yapısının karakteristik özelliğidir?",
        "options": ["FIFO", "LIFO", "Rastgele erişim", "Ağaç tabanlı arama"],
        "correct_index": 1,
        "difficulty": "zor"
    },
    {
        "id": 207,
        "text": "Aşağıdaki şehirlerden hangisi İpek Yolu güzergâhında tarihsel olarak önemli bir duraktır?",
        "options": ["Konya", "Sivas", "Bursa", "Semerkant"],
        "correct_index": 3,
        "difficulty": "zor"
    },
    {
        "id": 208,
        "text": "Fotosentez sırasında bitkiler hangi gazı tüketir?",
        "options": ["Oksijen", "Karbon dioksit", "Azot", "Metan"],
        "correct_index": 1,
        "difficulty": "zor"
    },

    # ÇOK ZOR (%10)
    {
        "id": 301,
        "text": "“Tabula rasa” kavramı hangi filozofla özdeşleşmiştir?",
        "options": ["Immanuel Kant", "John Locke", "Rene Descartes", "David Hume"],
        "correct_index": 1,
        "difficulty": "cok_zor"
    },
    {
        "id": 302,
        "text": "1917 yılında yayımlanan ve Rusya'da Bolşevik Devrimi'ne giden süreci belirleyen bildirinin adı nedir?",
        "options": ["Versay Bildirgesi", "Ekim Manifestosu", "Nisan Tezleri", "Balfour Deklarasyonu"],
        "correct_index": 2,
        "difficulty": "cok_zor"
    },
    {
        "id": 303,
        "text": "Şöyle tanımlanan veri yapısı hangisidir: Ekleme ve silme işlemleri sadece uçlardan yapılabilir.",
        "options": ["Stack", "Queue", "Deque", "Heap"],
        "correct_index": 2,
        "difficulty": "cok_zor"
    },
    {
        "id": 304,
        "text": "Bir sinyalin frekans bileşenlerine ayrılması için en sık kullanılan matematiksel araç hangisidir?",
        "options": ["Laplace dönüşümü", "Fourier dönüşümü", "Taylor serisi", "Gauss integrali"],
        "correct_index": 1,
        "difficulty": "cok_zor"
    }
]

DIFFICULTY_MULTIPLIER = {
    "kolay": 1,
    "orta": 2,
    "zor": 3,
    "cok_zor": 4
}

# --- Oyun durumu ---

PLAYERS = {}  # player_id -> {"name": "Heysem"}

GAME_STATE = {
    "question_active": False,
    "question_start_time": None,
    "question_duration": 20,   # saniye
    "answers": {},             # player_id -> {"answer_index": int, "answer_time": float}
    "scores": {},              # player_id -> toplam puan
    "last_results": [],        # skor tablosu (büyükten küçüğe)
    "selected_questions": [],  # seçilen soru listesi
    "current_round": 0,        # 0-based index
    "total_rounds": 0,         # toplam soru sayısı
    "streaks": {}              # player_id -> ardışık doğru sayısı
}

# --- Ortak stil (CSS) ---

BASE_CSS = """
<style>
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    body {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: linear-gradient(135deg, #4c6fff, #9b5cff);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #1f2933;
    }
    .page-wrapper {
        width: 100%;
        max-width: 900px;
        padding: 24px;
    }
    .card {
        background: #ffffff;
        border-radius: 18px;
        box-shadow: 0 14px 35px rgba(15, 23, 42, 0.25);
        padding: 24px 28px;
        border: 1px solid rgba(148, 163, 184, 0.4);
    }
    .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
    }
    .card-title {
        font-size: 24px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 10px;
        color: #111827;
    }
    .card-subtitle {
        font-size: 13px;
        color: #6b7280;
        margin-top: 4px;
    }
    .badge {
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    .badge-primary {
        background: rgba(59, 130, 246, 0.1);
        color: #1d4ed8;
    }
    .badge-success {
        background: rgba(16, 185, 129, 0.12);
        color: #047857;
    }
    .badge-warning {
        background: rgba(245, 158, 11, 0.12);
        color: #92400e;
    }
    .badge-secondary {
        background: rgba(148, 163, 184, 0.18);
        color: #374151;
    }
    h1, h2, h3 {
        margin-bottom: 10px;
    }
    p {
        margin-bottom: 8px;
        font-size: 14px;
        line-height: 1.5;
    }
    a {
        color: #4f46e5;
        text-decoration: none;
        font-weight: 500;
    }
    a:hover {
        text-decoration: underline;
    }
    .button-row {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 16px;
    }
    .btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 999px;
        border: none;
        padding: 9px 18px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.16s ease-in-out;
    }
    .btn-primary {
        background: linear-gradient(135deg, #4f46e5, #6366f1);
        color: white;
        box-shadow: 0 10px 25px rgba(79, 70, 229, 0.4);
    }
    .btn-primary:hover {
        transform: translateY(-1px);
        box-shadow: 0 16px 30px rgba(79, 70, 229, 0.5);
    }
    .btn-outline {
        background: white;
        color: #111827;
        border: 1px solid rgba(148, 163, 184, 0.8);
    }
    .btn-outline:hover {
        background: #f3f4ff;
    }
    .btn-sm {
        padding: 6px 12px;
        font-size: 12px;
    }
    .form-group {
        margin-bottom: 12px;
    }
    label {
        font-size: 13px;
        font-weight: 600;
        color: #374151;
        display: block;
        margin-bottom: 4px;
    }
    input[type="text"], input[type="number"], input[type="password"] {
        width: 100%;
        padding: 8px 10px;
        border-radius: 10px;
        border: 1px solid #d1d5db;
        font-size: 14px;
        outline: none;
        transition: border-color 0.16s ease, box-shadow 0.16s ease;
    }
    input[type="text"]:focus, input[type="number"]:focus, input[type="password"]:focus {
        border-color: #4f46e5;
        box-shadow: 0 0 0 1px rgba(79, 70, 229, 0.2);
    }
    .timer-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(239, 68, 68, 0.08);
        color: #b91c1c;
        font-size: 13px;
        font-weight: 600;
    }
    .question-text {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
        margin-top: 8px;
        margin-bottom: 12px;
    }
    .options-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 8px;
        margin-bottom: 10px;
    }
    .option-item {
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        padding: 8px 10px;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        background: #f9fafb;
    }
    .option-item input {
        margin: 0;
    }
    .option-item:hover {
        background: #eef2ff;
        border-color: #a5b4fc;
    }
    .option-item.correct {
        background: #dcfce7;
        border-color: #22c55e;
    }
    .option-item.wrong {
        background: #fee2e2;
        border-color: #ef4444;
    }
    .section {
        margin-top: 14px;
        padding-top: 12px;
        border-top: 1px dashed rgba(148, 163, 184, 0.7);
    }
    .section-title {
        font-size: 14px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .pill-list {
        list-style: none;
        padding-left: 0;
        margin-top: 6px;
    }
    .pill-list li {
        padding: 4px 8px;
        border-radius: 999px;
        background: #f3f4ff;
        display: inline-block;
        margin-right: 4px;
        margin-bottom: 4px;
        font-size: 12px;
        color: #4b5563;
    }
    .results-list {
        list-style: none;
        padding-left: 0;
        margin-top: 6px;
    }
    .results-list li {
        font-size: 13px;
        padding: 4px 0;
        border-bottom: 1px dashed #e5e7eb;
    }
    .results-list li:last-child {
        border-bottom: none;
    }
    .muted {
        color: #9ca3af;
        font-size: 13px;
    }
    .score-box {
        margin-top: 8px;
        padding: 8px 10px;
        border-radius: 12px;
        background: #f3f4ff;
        font-size: 13px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .error-text {
        color: #b91c1c;
        font-size: 13px;
        margin-bottom: 6px;
    }
</style>
"""

# --- HTML şablonları (f-string YOK, base_css template ile geliyor) ---

INDEX_HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Bilgi Yarışması</title>
    {{ base_css|safe }}
</head>
<body>
    <div class="page-wrapper">
        <div class="card">
            <div class="card-header">
                <div>
                    <div class="card-title">
                        🧠 Bilgi Yarışması
                    </div>
                    <div class="card-subtitle">
                        Ekip içi mini bilgi yarışmanız – admin veya yarışmacı olarak katıl.
                    </div>
                </div>
                <span class="badge badge-primary">Çok sorulu prototip</span>
            </div>

            <p>Başlamak için rolünü seç:</p>

            <div class="button-row">
                <a href="{{ url_for('admin_login') }}">
                    <button class="btn btn-primary">🎛 Admin olarak gir</button>
                </a>
                <a href="{{ url_for('join') }}">
                    <button class="btn btn-outline">🙋 Yarışmacı olarak katıl</button>
                </a>
            </div>

            <div class="section">
                <div class="section-title">ℹ️ Nasıl çalışır?</div>
                <p class="muted">
                    Admin toplam soru sayısını ve süreyi belirler. Sistem soru kütüphanesinden
                    yaklaşık %30 kolay, %30 orta, %30 zor, %10 çok zor dağılımıyla soruları seçer.
                    Her doğru cevap hız ve zorluk çarpanına göre puan kazandırır. 3 doğru seri yapanlara
                    ekstra bonus puan verilir. Doğru şıklar yeşil, yanlış işaretlenen şıklar kırmızı gösterilir.
                </p>
            </div>
        </div>
    </div>
</body>
</html>
"""

ADMIN_LOGIN_HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Admin Girişi • Bilgi Yarışması</title>
    {{ base_css|safe }}
</head>
<body>
    <div class="page-wrapper">
        <div class="card">
            <div class="card-header">
                <div>
                    <div class="card-title">
                        🔐 Admin Girişi
                    </div>
                    <div class="card-subtitle">
                        Sadece senin kontrolünde bir admin paneli.
                    </div>
                </div>
                <span class="badge badge-warning">Güvenli erişim</span>
            </div>

            {% if error %}
                <p class="error-text">{{ error }}</p>
            {% endif %}

            <form method="post">
                <div class="form-group">
                    <label>Kullanıcı adı</label>
                    <input type="text" name="username" placeholder="admin" required>
                </div>
                <div class="form-group">
                    <label>Şifre</label>
                    <input type="password" name="password" placeholder="••••••••" required>
                </div>
                <button type="submit" class="btn btn-primary">Giriş Yap</button>
            </form>

            <div class="section">
                <p class="muted">
                    Kullanıcı adı ve şifreyi kod içinde <code>ADMIN_USERNAME</code> ve <code>ADMIN_PASSWORD</code>
                    sabitlerinden değiştirebilirsin.
                </p>
                <p><a href="{{ url_for('index') }}">← Ana sayfaya dön</a></p>
            </div>
        </div>
    </div>
</body>
</html>
"""

JOIN_HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Yarışmaya Katıl • Bilgi Yarışması</title>
    {{ base_css|safe }}
</head>
<body>
    <div class="page-wrapper">
        <div class="card">
            <div class="card-header">
                <div>
                    <div class="card-title">
                        🙋 Yarışmaya Katıl
                    </div>
                    <div class="card-subtitle">
                        Kullanıcı adını yaz, yarışmaya dahil ol.
                    </div>
                </div>
                <span class="badge badge-success">Yarışmacı</span>
            </div>

            <form method="post">
                <div class="form-group">
                    <label>Kullanıcı adın</label>
                    <input type="text" name="player_name" placeholder="Örn. Heysem" required>
                </div>
                <button type="submit" class="btn btn-primary">Odaya Gir</button>
            </form>

            <div class="section">
                <p class="muted">
                    Bu pencereyi kapatma. Admin oyunu başlattığında sıradaki sorular otomatik olarak
                    bu ekrana düşecek.
                </p>
                <p><a href="{{ url_for('index') }}">← Ana sayfaya dön</a></p>
            </div>
        </div>
    </div>
</body>
</html>
"""

PLAYER_HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Yarışmacı Paneli • {{ player.name }}</title>
    {{ base_css|safe }}
    <script>
        let remaining = {{ time_left | int }};
        const questionActive = {{ 'true' if game_state.question_active else 'false' }};

        function tick() {
            if (remaining > 0) {
                remaining -= 1;
                var el = document.getElementById("timer");
                if (el) {
                    el.innerText = remaining + " sn";
                }
                setTimeout(tick, 1000);
            }
        }

        function setupAutoRefresh() {
            // Soru AKTİF DEĞİLSE (yani oyun başlamamışsa veya soru arasıysa)
            // oyuncu ekranını 3 saniyede bir yenile.
            if (!questionActive) {
                setInterval(function() {
                    location.reload();
                }, 3000);
            }
        }

        window.onload = function() {
            tick();
            setupAutoRefresh();
        }
    </script>
</head>
<body>
    <div class="page-wrapper">
        <div class="card">
            <div class="card-header">
                <div>
                    <div class="card-title">
                        🎮 Yarışmacı: {{ player.name }}
                    </div>
                    <div class="card-subtitle">
                        Cevabını seç, süre bitmeden gönder.
                    </div>
                </div>
                <span class="badge badge-secondary">Kişisel ekran</span>
            </div>

            {% if not game_state.question_active %}
                {% if game_state.total_rounds == 0 %}
                    <p>Oyun henüz başlamadı. <strong>Admin'in oyunu başlatmasını bekle.</strong></p>
                {% elif game_state.current_round >= game_state.total_rounds %}
                    <p>Oyun bitti. Admin yeni oyun başlatana kadar skor tablosu sabit kalacak.</p>
                {% else %}
                    <p>Soru {{ game_state.current_round + 1 }} / {{ game_state.total_rounds }} bitti.</p>
                    <p>Bir sonraki soruyu admin başlatacak, lütfen bekle.</p>
                {% endif %}

                {% if game_state.last_results %}
                    <div class="section">
                        <div class="section-title">📊 Skor Tablosu</div>
                        <ul class="results-list">
                            {% for item in game_state.last_results %}
                                <li>{{ item }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                {% endif %}

                <div class="section">
                    <div class="section-title">👥 Oyuncular</div>
                    {% if players %}
                        <ul class="pill-list">
                            {% for pid, p in players.items() %}
                                <li>{{ p.name }}</li>
                            {% endfor %}
                        </ul>
                    {% else %}
                        <p class="muted">Henüz başka oyuncu yok.</p>
                    {% endif %}
                </div>

                <div class="section">
                    <p><a href="{{ url_for('player_view', player_id=player_id) }}" class="muted">↻ Sayfayı yenile</a></p>
                </div>

            {% else %}
                <div class="section">
                    <span class="timer-pill">
                        ⏱ Kalan süre: <span id="timer">{{ time_left | int }} sn</span>
                    </span>
                    <p class="muted">Soru {{ game_state.current_round + 1 }} / {{ game_state.total_rounds }}</p>
                </div>

                <div class="section">
                    <div class="section-title">❓ Soru</div>
                    <div class="question-text">
                        {{ current_question.text }}
                    </div>
                </div>

                {% set has_answer = (player_answer_index is not none) %}

                {% if time_left <= 0 or has_answer %}
                    <div class="options-grid">
                        {% for idx, opt in enumerate(current_question.options) %}
                            <div class="option-item{% if correct_index is not none and idx == correct_index %} correct{% endif %}{% if has_answer and player_answer_index is not none and idx == player_answer_index and player_answer_index != correct_index %} wrong{% endif %}">
                                <span>{{ opt }}</span>
                            </div>
                        {% endfor %}
                    </div>

                    {% if has_answer %}
                        {% if player_answer_index == correct_index %}
                            <p><strong>Doğru cevap!</strong> Yeşil işaretli şık doğru cevaptır.</p>
                        {% else %}
                            <p><strong>Yanlış cevap.</strong> Yeşil şık doğru cevabı, kırmızı şık senin işaretlediğini gösteriyor.</p>
                        {% endif %}
                    {% else %}
                        <p>Süre doldu. Yeşil şık doğru cevabı gösteriyor.</p>
                    {% endif %}

                    <div class="section">
                        <div class="section-title">📊 Skor Tablosu</div>
                        {% if game_state.last_results %}
                            <ul class="results-list">
                                {% for item in game_state.last_results %}
                                    <li>{{ item }}</li>
                                {% endfor %}
                            </ul>
                        {% else %}
                            <p class="muted">Bu soruya ait skorlar henüz hesaplanmadı.</p>
                        {% endif %}
                    </div>

                    <p><a href="{{ url_for('player_view', player_id=player_id) }}" class="muted">↻ Sayfayı yenile</a></p>
                {% else %}
                    <form method="post" action="{{ url_for('submit_answer', player_id=player_id) }}">
                        <div class="options-grid">
                            {% for idx, opt in enumerate(current_question.options) %}
                                <label class="option-item">
                                    <input type="radio" name="answer" value="{{ idx }}" required>
                                    <span>{{ opt }}</span>
                                </label>
                            {% endfor %}
                        </div>
                        <button type="submit" class="btn btn-primary">Cevabı Gönder</button>
                    </form>

                    <p class="muted" style="margin-top: 8px;">
                        Tereddütteysen bile bir şık işaretle; yanlış veya boş cevap 0 puan demek.
                    </p>
                    <p><a href="{{ url_for('player_view', player_id=player_id) }}" class="muted">↻ Sayfayı yenile</a></p>
                {% endif %}
            {% endif %}

            <div class="section">
                <div class="section-title">🏅 Skorun</div>
                <div class="score-box">
                    <span>Toplam skorun:</span>
                    <strong>{{ total_score }}</strong>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

ADMIN_HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Admin Paneli • Bilgi Yarışması</title>
    {{ base_css|safe }}
</head>
<body>
    <div class="page-wrapper">
        <div class="card">
            <div class="card-header">
                <div>
                    <div class="card-title">
                        🎛 Admin Paneli
                    </div>
                    <div class="card-subtitle">
                        Oyuncuları gör, oyunu başlat, soruları ilerlet ve puanları hesapla.
                    </div>
                </div>
                <span class="badge badge-warning">Admin</span>
            </div>

            <div class="section">
                <div class="section-title">👥 Oyuncular</div>
                {% if players %}
                    <ul class="pill-list">
                    {% for pid, p in players.items() %}
                        <li>{{ p.name }} • Skor: {{ scores.get(pid, 0) }}</li>
                    {% endfor %}
                    </ul>
                {% else %}
                    <p class="muted">Henüz oyuncu yok. Yarışmacılara <code>/join</code> linkini gönder.</p>
                {% endif %}
            </div>

            <div class="section">
                <div class="section-title">🧩 Oyun Durumu</div>
                {% if game_state.total_rounds == 0 %}
                    <p>Oyun henüz başlatılmadı.</p>
                    <form method="post" action="{{ url_for('admin_configure_game') }}">
                        <div class="form-group" style="max-width: 220px;">
                            <label>Toplam soru sayısı</label>
                            <input type="number" name="total_rounds" value="10" min="1" max="30" required>
                        </div>
                        <div class="form-group" style="max-width: 220px;">
                            <label>Soru başına süre (saniye)</label>
                            <input type="number" name="duration" value="{{ game_state.question_duration }}" min="5" max="120" required>
                        </div>
                        <button type="submit" class="btn btn-primary">🎬 Oyunu Başlat</button>
                    </form>
                {% else %}
                    <p>Toplam soru: <strong>{{ game_state.total_rounds }}</strong></p>
                    <p>Şu anki durum:
                        {% if game_state.current_round >= game_state.total_rounds %}
                            <strong>Oyun bitti.</strong>
                        {% elif game_state.question_active %}
                            <strong>Soru {{ game_state.current_round + 1 }} / {{ game_state.total_rounds }} aktif.</strong>
                        {% else %}
                            <strong>Soru {{ game_state.current_round + 1 }} / {{ game_state.total_rounds }} beklemede.</strong>
                        {% endif %}
                    </p>
                    <p class="muted">Soru süresi: {{ game_state.question_duration }} sn</p>

                    {% if not game_state.question_active and game_state.current_round < game_state.total_rounds %}
                        <form method="post" action="{{ url_for('admin_start_round') }}" style="margin-top: 10px;">
                            <button type="submit" class="btn btn-primary">✨ Sıradaki Soruyu Başlat</button>
                        </form>
                    {% elif game_state.question_active %}
                        <p style="margin-top: 10px;">
                            <span class="timer-pill">
                                ⏱ Tahmini kalan süre: {{ time_left | int }} sn
                            </span>
                        </p>
                        <div class="section">
                            <div class="section-title">📥 Gelen cevaplar</div>
                            {% if game_state.answers %}
                                <ul class="results-list">
                                {% for pid, ans in game_state.answers.items() %}
                                    <li>
                                        <strong>{{ players[pid].name }}</strong> →
                                        "{{ current_question.options[ans.answer_index] }}"
                                    </li>
                                {% endfor %}
                                </ul>
                            {% else %}
                                <p class="muted">Henüz cevap yok.</p>
                            {% endif %}
                        </div>
                        <form method="post" action="{{ url_for('admin_finish_round') }}" style="margin-top: 10px;">
                            <button type="submit" class="btn btn-outline btn-sm">✅ Soruyu Bitir ve Puanları Hesapla</button>
                        </form>
                    {% endif %}
                {% endif %}

                <form method="post" action="{{ url_for('admin_new_game') }}" style="margin-top: 10px;">
                    <button type="submit" class="btn btn-outline btn-sm">🆕 Yeni Oyun Başlat (Tam Sıfırla)</button>
                </form>
            </div>

            {% if game_state.last_results %}
                <div class="section">
                    <div class="section-title">📊 Skor Tablosu</div>
                    <ul class="results-list">
                        {% for item in game_state.last_results %}
                            <li>{{ item }}</li>
                        {% endfor %}
                    </ul>
                </div>
            {% endif %}

            <div class="section">
                <p>
                    <a href="{{ url_for('index') }}">← Ana sayfa</a> ·
                    <a href="{{ url_for('admin_panel') }}" class="muted">↻ Yenile</a> ·
                    <a href="{{ url_for('admin_logout') }}" class="muted">🚪 Çıkış yap</a>
                </p>
            </div>
        </div>
    </div>
</body>
</html>
"""

# --- Yardımcı fonksiyonlar ---

def current_time():
    return time.time()

def get_time_left():
    if not GAME_STATE["question_active"] or GAME_STATE["question_start_time"] is None:
        return 0
    end_time = GAME_STATE["question_start_time"] + GAME_STATE["question_duration"]
    return max(0, end_time - current_time())

def get_current_question():
    idx = GAME_STATE["current_round"]
    if 0 <= idx < len(GAME_STATE["selected_questions"]):
        return GAME_STATE["selected_questions"][idx]
    return None

def reset_game():
    """Yeni oyun için her şeyi sıfırla."""
    PLAYERS.clear()
    GAME_STATE["question_active"] = False
    GAME_STATE["question_start_time"] = None
    GAME_STATE["answers"] = {}
    GAME_STATE["scores"] = {}
    GAME_STATE["last_results"] = []
    GAME_STATE["selected_questions"] = []
    GAME_STATE["current_round"] = 0
    GAME_STATE["total_rounds"] = 0
    GAME_STATE["streaks"] = {}

def select_questions_for_game(total_rounds):
    """Soru kütüphanesinden istenen dağılıma yakın şekilde soru seç."""
    easy = [q for q in QUESTION_BANK if q["difficulty"] == "kolay"]
    medium = [q for q in QUESTION_BANK if q["difficulty"] == "orta"]
    hard = [q for q in QUESTION_BANK if q["difficulty"] == "zor"]
    very_hard = [q for q in QUESTION_BANK if q["difficulty"] == "cok_zor"]

    def round_int(x):
        return int(round(x))

    n = min(total_rounds, len(QUESTION_BANK))
    n_easy = round_int(n * 0.3)
    n_medium = round_int(n * 0.3)
    n_hard = round_int(n * 0.3)
    n_very_hard = n - (n_easy + n_medium + n_hard)
    if n_very_hard < 0:
        n_very_hard = 0

    selected = []

    def pick_from_pool(pool, count):
        if count <= 0:
            return []
        if len(pool) <= count:
            return pool
        return random.sample(pool, count)

    selected += pick_from_pool(easy, n_easy)
    selected += pick_from_pool(medium, n_medium)
    selected += pick_from_pool(hard, n_hard)
    selected += pick_from_pool(very_hard, n_very_hard)

    if len(selected) < n:
        remaining = [q for q in QUESTION_BANK if q not in selected]
        extra_needed = n - len(selected)
        if remaining:
            selected += pick_from_pool(remaining, extra_needed)

    random.shuffle(selected)
    return selected[:n]

def score_current_question():
    """Aktif soruyu bitir, hız+zorluk+streak bonusu ile puanları hesapla."""
    if not GAME_STATE["question_active"]:
        return

    GAME_STATE["question_active"] = False

    current_question = get_current_question()
    if current_question is None:
        GAME_STATE["last_results"] = []
        return

    N = len(PLAYERS)
    if N == 0:
        GAME_STATE["last_results"] = []
        return

    diff = current_question["difficulty"]
    multiplier = DIFFICULTY_MULTIPLIER.get(diff, 1)
    correct_index = current_question["correct_index"]

    correct_answers = []
    for pid, ans in GAME_STATE["answers"].items():
        if ans["answer_index"] == correct_index:
            correct_answers.append((pid, ans["answer_time"]))

    correct_answers.sort(key=lambda x: x[1])

    base_points = N

    for pid in PLAYERS:
        if pid not in GAME_STATE["streaks"]:
            GAME_STATE["streaks"][pid] = 0

    for rank, (pid, ans_time) in enumerate(correct_answers):
        base = max(0, base_points - rank)
        gained = base * multiplier

        GAME_STATE["streaks"][pid] += 1

        if GAME_STATE["streaks"][pid] % 3 == 0:
            bonus = int(round(N / 2.0))
            gained += bonus

        GAME_STATE["scores"][pid] = GAME_STATE["scores"].get(pid, 0) + gained

    for pid in PLAYERS:
        if pid not in GAME_STATE["answers"]:
            GAME_STATE["streaks"][pid] = 0
        else:
            if GAME_STATE["answers"][pid]["answer_index"] != correct_index:
                GAME_STATE["streaks"][pid] = 0

  # Her oyuncunun mutlaka skor kaydı olsun (cevap vermese bile 0 p ile listede görünsün)
    for pid in PLAYERS:
        GAME_STATE["scores"].setdefault(pid, 0)

    ordered = sorted(GAME_STATE["scores"].items(), key=lambda x: x[1], reverse=True)
    results = []
    for idx, (pid, score) in enumerate(ordered, start=1):
        name = PLAYERS[pid]["name"]
        results.append(f"{idx}. {name} - {score}p")

    GAME_STATE["last_results"] = results
    GAME_STATE["answers"] = {}


# --- Admin oturumu kontrolü ---

def is_admin_logged_in():
    return session.get("is_admin", False)

def require_admin():
    if not is_admin_logged_in():
        return False
    return True

# --- Route'lar ---

@app.route("/")
def index():
    return render_template_string(INDEX_HTML, base_css=BASE_CSS)


@app.route("/join", methods=["GET", "POST"])
def join():
    if request.method == "POST":
        name = request.form.get("player_name", "").strip()
        if not name:
            return render_template_string(JOIN_HTML, base_css=BASE_CSS)
        pid = str(uuid.uuid4())
        PLAYERS[pid] = {"name": name}
        if pid not in GAME_STATE["scores"]:
            GAME_STATE["scores"][pid] = 0
        return redirect(url_for("player_view", player_id=pid))
    return render_template_string(JOIN_HTML, base_css=BASE_CSS)


@app.route("/player/<player_id>")
def player_view(player_id):
    if player_id not in PLAYERS:
        return "Oyuncu bulunamadı. Yeniden katılmayı deneyin.", 404

    player = PLAYERS[player_id]
    time_left = get_time_left()
    total_score = GAME_STATE["scores"].get(player_id, 0)
    current_question = get_current_question()

    player_answer_index = None
    if player_id in GAME_STATE["answers"]:
        player_answer_index = GAME_STATE["answers"][player_id]["answer_index"]

    correct_index = None
    if current_question:
        correct_index = current_question["correct_index"]

    return render_template_string(
        PLAYER_HTML,
        base_css=BASE_CSS,
        player=player,
        player_id=player_id,
        current_question=current_question,
        answers=GAME_STATE["answers"],
        game_state=GAME_STATE,
        time_left=time_left,
        total_score=total_score,
        player_answer_index=player_answer_index,
        correct_index=correct_index,
        players=PLAYERS,
        enumerate=enumerate
    )


@app.route("/answer/<player_id>", methods=["POST"])
def submit_answer(player_id):
    if player_id not in PLAYERS:
        return "Oyuncu bulunamadı.", 404

    if not GAME_STATE["question_active"]:
        return redirect(url_for("player_view", player_id=player_id))

    if get_time_left() <= 0:
        return redirect(url_for("player_view", player_id=player_id))

    if player_id in GAME_STATE["answers"]:
        return redirect(url_for("player_view", player_id=player_id))

    try:
        answer_index = int(request.form.get("answer"))
    except (TypeError, ValueError):
        return redirect(url_for("player_view", player_id=player_id))

    current_question = get_current_question()
    if not current_question:
        return redirect(url_for("player_view", player_id=player_id))

    if answer_index < 0 or answer_index >= len(current_question["options"]):
        return redirect(url_for("player_view", player_id=player_id))

    GAME_STATE["answers"][player_id] = {
        "answer_index": answer_index,
        "answer_time": current_time()
    }

    return redirect(url_for("player_view", player_id=player_id))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin_panel"))
        else:
            return render_template_string(ADMIN_LOGIN_HTML, base_css=BASE_CSS, error="Kullanıcı adı veya şifre hatalı.")
    return render_template_string(ADMIN_LOGIN_HTML, base_css=BASE_CSS, error=None)


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))


@app.route("/admin")
def admin_panel():
    if not require_admin():
        return redirect(url_for("admin_login"))
    time_left = get_time_left()
    current_question = get_current_question()
    return render_template_string(
        ADMIN_HTML,
        base_css=BASE_CSS,
        players=PLAYERS,
        scores=GAME_STATE["scores"],
        game_state=GAME_STATE,
        current_question=current_question,
        time_left=time_left
    )


@app.route("/admin/configure_game", methods=["POST"])
def admin_configure_game():
    if not require_admin():
        return redirect(url_for("admin_login"))

    try:
        total_rounds = int(request.form.get("total_rounds", 10))
    except ValueError:
        total_rounds = 10

    try:
        duration = int(request.form.get("duration", GAME_STATE["question_duration"]))
    except ValueError:
        duration = GAME_STATE["question_duration"]

    total_rounds = max(1, min(total_rounds, 30))
    GAME_STATE["question_duration"] = max(5, min(duration, 120))
    GAME_STATE["selected_questions"] = select_questions_for_game(total_rounds)
    GAME_STATE["total_rounds"] = len(GAME_STATE["selected_questions"])
    GAME_STATE["current_round"] = 0
    GAME_STATE["question_active"] = False
    GAME_STATE["answers"] = {}
    GAME_STATE["last_results"] = []
    GAME_STATE["scores"] = {pid: 0 for pid in PLAYERS}      # tüm mevcut oyuncular 0’dan başlasın
    GAME_STATE["streaks"] = {pid: 0 for pid in PLAYERS}

    return redirect(url_for("admin_panel"))


@app.route("/admin/start_round", methods=["POST"])
def admin_start_round():
    if not require_admin():
        return redirect(url_for("admin_login"))

    if GAME_STATE["current_round"] >= GAME_STATE["total_rounds"]:
        return redirect(url_for("admin_panel"))

    GAME_STATE["question_start_time"] = current_time()
    GAME_STATE["question_active"] = True
    GAME_STATE["answers"] = {}

    return redirect(url_for("admin_panel"))


@app.route("/admin/finish_round", methods=["POST"])
def admin_finish_round():
    if not require_admin():
        return redirect(url_for("admin_login"))

    score_current_question()

    if GAME_STATE["current_round"] < GAME_STATE["total_rounds"]:
        GAME_STATE["current_round"] += 1

    return redirect(url_for("admin_panel"))


@app.route("/admin/new_game", methods=["POST"])
def admin_new_game():
    if not require_admin():
        return redirect(url_for("admin_login"))
    reset_game()
    return redirect(url_for("admin_panel"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
