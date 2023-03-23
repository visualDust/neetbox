def test_registry():
    from neetbox.pipeline import Registry
    reg1 = Registry("SOME-1")
    reg2 = Registry("SOME-1")
    reg3 = Registry("SOME-2")
    
    @reg1.register()
    def a():
        pass
    @reg2.register()
    def b():
        pass
    print(reg1)
    @reg3.register()
    class C:
        pass
    print(reg3)