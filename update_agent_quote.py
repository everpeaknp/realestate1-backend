import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realtor_pal.settings')
django.setup()

from agents.models import Agent

agent = Agent.objects.get(id=1)
agent.quote = "I believe real estate is more than a transaction; it's about finding the space where your life's best moments happen."
agent.bio = "Principal Director"
agent.save()

print(f"Agent updated successfully!")
print(f"Name: {agent.name}")
print(f"Bio: {agent.bio}")
print(f"Quote: {agent.quote}")
