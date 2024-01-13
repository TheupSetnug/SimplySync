#openai
from openai import OpenAI
import yaml
from pprint import pprint

#load config.yaml
with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
key = config['OPENAI_API_KEY']

client = OpenAI(api_key = key)

def create_completion():
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
        {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
    ])
    return completion

completion = create_completion()
pprint(completion)