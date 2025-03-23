def test_connect():
    import uiautomator2 as u2

    d = u2.connect()
    print(d.info)
    print(d.device_info)
    print(d.app_list_running())
    print(d.app_current())
