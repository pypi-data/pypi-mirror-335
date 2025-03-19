import environ

env = environ.Env()

environ.Env.read_env()

WATCHMAN_API_KEY = env('WATCHMAN_API_KEY')
