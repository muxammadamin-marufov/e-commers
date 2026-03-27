# Python 3.10 talqini (Django 6.0 uchun mos)
FROM python:3.10
# Hugging Face uchun maxsus foydalanuvchi yaratish (xavfsizlik uchun)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Kutubxonalarni o'rnatish
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Loyihani to'liq nusxalash
COPY --chown=user . .

# Static fayllarni yig'ish (WhiteNoise ishlatganimiz uchun)
RUN python manage.py collectstatic --noinput

# Hugging Face 7860 portini talab qiladi
ENV PORT=7860
EXPOSE 7860

# Gunicorn orqali Djangoni ishga tushirish
# 'core.wsgi' qismini loyihangiz nomiga qarab o'zgartiring (settings.py qaysi papkada bo'lsa o'sha)
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:7860"]