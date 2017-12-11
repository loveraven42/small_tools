#- coding:utf-8 -*-
import melon
import sys
import os
import traceback

class CryptApp():

    def __init__(self,input_name,output_name):
        input_name = input_name.strip()
        self.input_name = input_name
        if output_name.endswith('.dat'):
            self.output_name = output_name
        else:
            print 'output_file type is error'
            sys.exit(1)


    def encrypt_app(self):
        try:
            melon.encrypt(self.input_name,self.output_name)
        except Exception,e:
            traceback.print_exc()
