import env

import app

if __name__ == '__main__':
    try_again = True
    while try_again:
        try:
            app.Application().run()
            try_again = False
        except:
            raise
