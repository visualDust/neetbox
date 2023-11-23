def test_neet_action():
    import time

    from neetbox.daemon import NeetActionManager, action

    @action(name="some_func")
    def some(a, b):
        time.sleep(1)
        return f"a = {a}, b = {b}"

    print("registered actions:")
    action_dict = NeetActionManager.get_action_dict()
    print(action_dict)

    def callback_fun(text):
        print(f"callback_fun print: {text}")

    NeetActionManager.eval_call("some", {"a": "3", "b": "4"}, callback=callback_fun)
    print("you should see this line first before callback_fun print")
    time.sleep(4)
