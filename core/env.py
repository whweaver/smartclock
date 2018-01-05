import sys
import os
import django

sys.path.append(os.path.abspath("mock_hw"))
sys.path.append(os.path.abspath("app"))
sys.path.append(os.path.abspath("lib"))
sys.path.append(os.path.abspath("../webapp"))

os.environ["DJANGO_SETTINGS_MODULE"] = 'webapp.settings'
django.setup()
