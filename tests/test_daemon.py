def test_neet_action():
    import time

    from neetbox.client import action
    from neetbox.client.apis._action import actionManager

    @action(name="some_func")
    def some(a, b):
        time.sleep(0.1)
        return f"a = {a}, b = {b}"

    print("registered actions:")
    action_dict = actionManager.get_action_dict()
    print(action_dict)

    def callback_fun(text):
        print(f"callback_fun print: {text}")

    actionManager.eval_call("some_func", params={"a": "3", "b": "4"}, callback=callback_fun)
    print("you should see this line first before callback_fun print")
    time.sleep(0.2)
