from ollama_client.py import OllamaClient

class GenFunction:

    # returns false if functions.txt is not found
    def functions_file_exists():
        try:
            with open("functions.txt") as f:
                return True
        except FileNotFoundError:
            return False
    
    # finds the comment in functions.txt // desc and returns the string starting on the
    # next line and ending at // end
    def find_function(desc):
        with open("functions.txt") as f:
            found_desc = False
            comment = []
            for line in f:
                if found_desc:
                    if "# end RANID9203481094328" in line:
                        break
                    comment.append(line)
                if "# " + desc + " RANID9203481094328" in line:
                    found_desc = True
            return "".join(comment) if comment else None
        
    def get_function(desc):
        # TODO: is this first check needed?
        if not GenFunction.functions_file_exists():
            return None

        return GenFunction.find_function(desc)
    
    def add_function(desc, *args):
        try:
            fun = GenFunction.gen_function(desc, *args)
        except:
            return False

        with open("functions.txt", "a") as f:
            f.write("# " + desc + " RANID9203481094328\n")
            f.write(fun)
            f.write("# end RANID9203481094328\n")

        return True

    # return a list of the type of each argument
    def args_string(*args):
        return ", ".join([str(type(arg)).split("'")[1] for arg in args])
    
    def gen_function(desc, *args):
        prompt = "Create a python function according to the following description\nand with the following argument types.\nDo not include any other text in your response.\n\n"
        prompt += "Description:" + desc + "\n\n"
        prompt += "Arguments: " + GenFunction.args_string(*args) + "\n\n"

        response = OllamaClient.generate(prompt, "gemma3:4b")

        # add the prompt and reponse to a logg file
        with open("functions_log.txt", "a") as f:
            f.write(prompt)
            f.write(response)
            f.write("\n\n73108210312781023192\n\n")

        response = response.split("```python")[1].split("```")[0]

        return response

    #def gen_function(desc, *args):
        #return "def mult(a, b):\n\treturn a * b\n"  # Using spaces instead of tabs
        
    def f(desc: str, *args):
        function = GenFunction.get_function(desc)
        if function is None:
            if (not GenFunction.add_function(desc, *args)):
                raise Exception("please launch ollama and confirm that gemma3:4b is installed")
            function = GenFunction.get_function(desc)
        
        local_vars = {}
        exec(function, {}, local_vars)
        function_name = function[function.find("def ") + 4:function.find("(")].strip()
        return local_vars[function_name](*args)