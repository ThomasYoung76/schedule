# schedule

    脚本调度通过目录下的execute.py实现，调度语法：
    usage：
        Python execute.py casename [-t times] [-r is_random] [-e executetime] [-c cycle]
    说明：后面4个参数为可选参数。
    结果备份功能：脚本在运行前会首先把local的日志备份到backup目录，backup目录按照执行点的时间戳按目录存储，最多存储3次，存储次数在config的script的配置文件中配置，备份用于后续结果比对。如果casename取值为用例列表（caselist），用例在执行完后会
## 参数说明
    Casename ： 必填字段，需要执行的用例ID配置，取值范围为：case_id, 支持通配符*，当为*时执行所有的用例
    -t times: 脚本运行的次数，默认为1
    -r is_random： 脚本随机顺序执行开关，取值范围：True, False(大小写不敏感）， 为True则随机执行，为False则按目录默认顺序执行。默认为False
    -r executetime：脚本运行的时间，当前只支持hh:mm方式
    -c cycle：脚本运行的周期，可以设置day，week，month，场景意义不大，根据需要实现
	
## 参数典型场景举例
    1、python ./execute.py *：运行本地所有的脚本文件，场景：单台机器验证
    2、python ./execute.py * -t 0：运行所有脚本，无限循环执行，
    3、python ./execute.py * -t 10：运行所有脚本，运行10次
    4、python ./execute.py * -t 10 -r True：运行所有脚本，运行10次，且每次运行的脚本为随机顺序执行
    5、python ./execute.py caseid：支持执行执行caseid的脚本
    6、python ./execute.py 00*: 支持匹配符合00* 的脚本
    7、python ./execute.py 00* -e 10:00 : 每天十点钟执行用例。每次运行一遍，执行00*匹配的用例[脚本会一直挂起]
    8、python execute.py E:\workspace\tdsql\config\case.txt： 运行case.txt中的case id一编
    9、python execute.py E:\workspace\tdsql\config\case.txt -t 1 -r False -e“10：00”：运行case.txt中的用例，每次运行一遍，按照文件列表顺序执行，每天十点执行

    其他命令：
    python ./execute.py -h 查看帮助信息


## 退出码：
    100X:  执行命令中的参数存在问题
    200X:  获取用例存在错误

    1001：执行命令的参数列表存在错误
    1002：执行命令的参数casename不存在或不合法
    1003：参数times错误，times必须为大于或等于0的整数
    1004：参数is_random错误，is_random只能为true或false，大小写不敏感
    1005：参数execute_time格式不正确。格式必须为”%H:%M”
    2001：获取用例id异常
    2002：匹配用例id异常

## 部分API说明
	* get_args:
		  通过getopt模块获取命令参数。
		  输出参数4个参数组成的元祖
		  Casename为字符串，times为整数，is_rand为bool值，限定True或False，
		  execute_time默认为None

	* scan_dir
	      递归遍历脚本所在路径，将获取到的每个脚本路径写入配置文件。返回所有的脚本路径组成的列表


	* filter_script
		   filter_script(str_case_name, dir_path):
		  先调用scan_dir获得所有脚本路径组成的列表，遍历列表，抽出其中的case_id，通过参数case_name匹配列表中每一个case_id，并和脚本路径组成元祖，一起返回，支持linux的通配符*进行模糊匹配。