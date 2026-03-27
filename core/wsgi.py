import os
from django.core.wsgi import get_wsgi_application
# WhiteNoise statik fayllarni (CSS, JS) serverda ko'rsatishga yordam beradi
from whitenoise import WhiteNoise

# 'core.settings' qismini o'zingizning settings papkangiz nomiga qarab tekshiring
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()

# Statik fayllarni WhiteNoise orqali o'rash (HF uchun shart)
application = WhiteNoise(application, root=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'staticfiles'))