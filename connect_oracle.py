from ctypes import *  
  
class StructPointer(Structure):  
    _fields_ = [("p", c_char_p), ("n", c_longlong)]  
  
if __name__ == "__main__":  
    lib = cdll.LoadLibrary("./libhello2.so")  
    lib.Query.argtype = [c_char_p, c_char_p]
    lib.Query.restype = c_char_p
    #print(lib.Query("system/123456@10.67.19.112:1521/orcl","select * from student1"))
    lib.query.restype = c_char_p
    print(lib.query("system/123456@10.67.19.112:1521/orcl","select SNAME from student1"))
