def test_registry():
    from neetbox.pipeline import Registry
    reg1 = Registry("RName-functions")
    reg2 = Registry("RName-classes")
    
    @reg1.register(name='a', tags=['function'])
    def a():
        pass
    
    @reg1.register(name='b', tags='function')
    def b():
        pass
    
    @reg1.register(name='b', tags='function')
    def b1():
        pass
    
    @reg2.register(name='C', tags='class')
    class C:
        pass
    
    print(f"Things in reg1: {reg1}")
    print(f"Things in reg2: {reg2}")
    print(f"Finding functions: {Registry.find(tags='function')}")

    