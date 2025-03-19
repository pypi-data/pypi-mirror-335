#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
# import requests
from datetime import datetime
from shadowshell.logger_factory import LoggerFactory

"""
ShadowShell

@author: shadow shell
"""
class ShadowShell:

    def __init__(self):
        pass

    def hello(self):
        print("Hi, i am shadow shell." )
        current_time = datetime.now()
        formatted_current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        print("Now is " + formatted_current_time)

    def test(self):
        self.hello()
    
    # def request(self):
    #     print(requests.get("https://wwww.baidu.com"))


class TestTemplate:

    def __init__(self):
        return

    def test(self):

        try:
            self.console('-->> Ready')
            
            self.test0()

            self.console('-->> Do something')

        except Exception as e:
            self.console(e)
        except:
            self.console(sys.exc_info()[0])
        finally:
            self.console('-->> Done')
            return

    def test0(self):
        self.console('Nothing')
        return

    def console(self, content):
        print('[CONSOLE] %s' % (content))

logger = LoggerFactory().get_logger()

def testserver():
    os.system("ping shadowshell.xyz")
    
def cnnserver():
    os.system("ssh admin@shadowshell.xyz")

def hello(**args):
    logger.info(f"Hello {args}")

def shadowshell(**args):
    logger.info(f"shadow shell : {args}")

def invoke_with_tmpl(func, **args):
    try:
        logger.info('-->> Ready')
        func(**args)
        logger.info('-->> Do something')
    except Exception as e:
        logger.error(e)
    except:
        logger.error(sys.exc_info()[0])
    finally:
        logger.info('-->> Done')
    return

if __name__ == "__main__":
    #ShadowShell().test()
    invoke_with_tmpl(shadowshell)
    invoke_with_tmpl(shadowshell, a='1')
    invoke_with_tmpl(shadowshell, a='1', b='2')
    invoke_with_tmpl(hello, a='shell', b='shadow')
