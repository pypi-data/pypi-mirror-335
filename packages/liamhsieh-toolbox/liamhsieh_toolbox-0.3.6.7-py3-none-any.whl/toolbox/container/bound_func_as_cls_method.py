from functools import partial

class BoundFuncAsClsMethod:
    def __init__(self, mapper: dict, class_to_attach_on = None, simple_mode = True):
        """_summary_

        Args:
            mapper (dict): _description_
            class_to_attach_on (_type_, optional): _description_. Defaults to None.
            simple_mode (bool, optional): _description_. Defaults to True.
        Example:
            ################ data required to create an instance of BoundFuncAsClsMethod ##############
            def m1(self):
                return f"{self.user_name}'s method 1"

            def m2(self):
                return self.msg

            def m3(self,favorite):
                return f"{self.user_name} likes {favorite}"

            method_mapper = {
                "method1":m1,
                "method2":m2,
                "method3":m3,
            }
            ############################################################################################

            
            # simple mode
            class Tester:
                def __init__(self,user_name):
                    self.user_name=user_name
                    self.methods = BoundFuncAsClsMethod(method_mapper)

            tester=Tester("Liam")
            tester.msg="original msg"

            # method 1 can access tester.user_name
            print(tester.methods.method1(tester))

            # method2 can access tester.msg while instance of Tester has been passed to m2 as an arg during initilization
            print(tester.methods.method2(tester))

            # modify the content of msg
            tester.msg="new one"

            # the output also changes
            print(tester.methods.method2(tester))

            # testing how it handles additional argument 
            print(tester.methods.method3(tester,"guava"))

            # Non simple mode
            class Tester:
                def __init__(self,user_name):
                    self.user_name=user_name
                    self.methods = BoundFuncAsClsMethod(method_mapper, self, simple_mode=False)

            tester=Tester("Liam")
            tester.msg="original msg"

            # passing or not passing tester as arg for mehtod1 has the same result
            print(tester.methods.method1())

            # passing or not passing tester as arg for mehtod1 has the same result
            print(tester.methods.method2())

            # modify the content of msg
            tester.msg="new one"

            # the output also changes
            print(tester.methods.method2())

            # testing how it handles additional argument 
            print(tester.methods.method3("guava"))

            # Output
            In this example, both modes will have the same output as follows:
            Liam's method 1
            original msg
            new one
            Liam likes guava
        """
        if simple_mode:
            # read through method_mapper and iteratively assign each value to a new property using key value
            for method_name, method in mapper.items():
                setattr(self,method_name, method)
        else:
            assert class_to_attach_on, "When using non simple mode, simple_mode=False, class_to_attch_on needs to be passed for initilizing the instance of BoundFuncAsClsMethod"
            
            for method_name, method in mapper.items():
                # bound_method = lambda self=class_to_attach_on, method=method: method(self)
                # setattr(self, method_name, bound_method)
                # Bind the method to class_to_attach_on and allow additional arguments to be passed later
                bound_method = partial(method, class_to_attach_on) 
                setattr(self, method_name, bound_method)


