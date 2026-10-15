# AI Security Log Analyzer

CSV güvenlik loglarını kural tabanlı kontroller ve Isolation Forest modeliyle
analiz eden küçük bir başlangıç projesidir. Üretilen uyarılar inceleme önceliği
gösterir; tek başına saldırı kanıtı değildir.

## Kurulum

Python 3.11 veya daha yeni bir sürümle:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Kullanım

Örnek logları analiz edip rapor ve model üretmek için:

```powershell
ai-security analyze data/raw/sample_security_logs.csv
```

Varsayılan çıktılar:

- `reports/anomalies.csv`: puanlar, tetiklenen kurallar ve açıklamalar
- `artifacts/isolation_forest.joblib`: eğitilmiş model ve özellik sütunları

Farklı yollar veya ayarlar kullanılabilir:

```powershell
ai-security analyze logs.csv --config configs/default.yaml --report rapor.csv --model model.joblib
```

Girdi CSV dosyasının zorunlu sütunları:

| Sütun | Açıklama | Örnek |
|---|---|---|
| `timestamp` | ISO 8601 zaman damgası | `2026-10-15T08:00:00Z` |
| `source_ip` | Kaynak IP adresi | `10.0.0.15` |
| `user` | Kullanıcı adı | `alice` |
| `event_type` | Olay türü | `login` |
| `outcome` | `success` veya `failure` | `failure` |
| `bytes_transferred` | Aktarılan bayt | `1024` |
| `destination` | Hedef sistem | `vpn-gateway` |

Her kayıt için aynı IP'nin yapılandırılmış zaman penceresindeki olay sayısı,
başarısız giriş sayısı ve hedef çeşitliliği hesaplanır. Kurallar açıklanabilir
uyarılar üretirken model davranışsal olarak sıra dışı kayıtları puanlar.

## Test

```powershell
pytest
```

