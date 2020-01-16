# from app import app
# application = app

# if __name__ == '__main__':
#   application.run()

def application(env, start_response):
  start_response('200 OK', [('Content-Type','text/html')])
  return [b"Hello World"]