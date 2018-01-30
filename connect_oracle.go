package main

import (
    "C"
    "database/sql"
    _ "github.com/mattn/go-oci8"
    "log"
    "strings"
    "fmt"
)
//export Query
func Query(address *C.char ,sql1 *C.char) *C.char{
    // 为log添加短文件名,方便查看行数
    log.SetFlags(log.Lshortfile | log.LstdFlags)
    fmt.Println(C.GoString(address))
    fmt.Println(C.GoString(sql1))
    // 用户名/密码@实例名  跟sqlplus的conn命令类似
    db, err := sql.Open("oci8", C.GoString(address))
    fmt.Print("test")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()
    rows, err := db.Query(C.GoString(sql1))
    fmt.Print("ok")
    //rows, err := db.Query("select * from student1")
    if err != nil {
        log.Fatal(err)
    }
    msgs := []string{}
    for rows.Next() {
        var sno string
        var name string
        rows.Scan(&sno, &name)
        msgs = append(msgs, name)
        log.Printf("Name = %s, len=%d", name, len(name))
        log.Printf("Sno = %s, len=%d", sno, len(sno))
    }
    str1 := strings.Join(msgs, ",")
    rows.Close()
    str2 := C.CString(str1)
    return str2
}

//export query
func query(address *C.char ,sql1 *C.char) *C.char{
    log.SetFlags(log.Lshortfile | log.LstdFlags)
    // 用户名/密码@实例名  跟sqlplus的conn命令类似
    db, err := sql.Open("oci8", C.GoString(address))
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()
    rows, err := db.Query(C.GoString(sql1))
    //rows, err := db.Query("select * from student1")
    if err != nil {
        log.Fatal(err)
    }

    columns, clmErr := rows.Columns()
    if clmErr != nil {}
    result := []string{}
    for rows.Next() {
        scanArgs := make([]interface{}, len(columns))
        for i := range scanArgs {
	    scanArgs[i] = &scanArgs[i]
	}
	scanErr := rows.Scan(scanArgs...)
	if scanErr != nil {
	}
        msgs := make([]string, len(columns))
        for index, value := range scanArgs {
		if value == nil {
			value = "NULL"
		}
		msgs[index] = fmt.Sprintf("\"%s\":\"%s\"", columns[index], value)
	}
	message := strings.Join(msgs, ",")
        message = "{" + message + "}"
        result = append(result, message)
    }
    result1 := C.CString(strings.Join(result, ","))
    return result1
}
//export Past
func Past(s string) string {
    return s
}

//export Hello
func Hello() string {
    return "Hello"
}

func main() {
}

